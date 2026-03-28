"""FastAPI application for the Robotic Writer.

Provides REST API endpoints for:
    - Running the writer simulation
    - Computing forward/inverse kinematics
    - Controlling hardware adapters (MATLAB, Arduino, serial)
    - Querying robot state and configuration
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core.kinematics import ForwardKinematics, InverseKinematics, JointState, JOINT_LIMITS_DEG
from ..core.robot import ScorbotIII
from ..core.writer import RoboticWriter, BlockCircle, WritingLine
from ..core.rrt_planner import RRTPlanner
from ..core.cursive import generate_cursive_path


# ── Pydantic models ────────────────────────────────────────────────────────

class JointAnglesRequest(BaseModel):
    """Joint angles in degrees."""
    angles_deg: list[float] = Field(..., min_length=5, max_length=5)
    gripper_mm: float = Field(0.0, ge=0.0, le=59.0)


class CartesianRequest(BaseModel):
    """Target Cartesian position in mm."""
    x: float
    y: float
    z: float
    approach_angle_deg: float = -90.0


class WriteRequest(BaseModel):
    """Request to write a text string."""
    text: str = Field(..., min_length=1, max_length=50)
    block_radius_mm: float = Field(280.0, ge=200.0, le=400.0)
    block_height_mm: float = Field(50.0, ge=0.0, le=200.0)
    min_angular_separation_deg: float = Field(8.0, ge=3.0, le=20.0)
    writing_radius_mm: float = 300.0
    writing_center_angle_deg: float = -25.0
    writing_angular_spacing_deg: float = Field(4.0, ge=2.0, le=8.0)


class HardwareConnectRequest(BaseModel):
    """Hardware connection parameters."""
    adapter_type: str = Field(..., pattern="^(matlab|arduino|serial)$")
    port: Optional[str] = None
    baud: Optional[int] = None


# ── Application state ──────────────────────────────────────────────────────

class AppState:
    def __init__(self):
        self.robot = ScorbotIII()
        self.writer: Optional[RoboticWriter] = None
        self.fk = ForwardKinematics()
        self.ik = InverseKinematics()
        self.hardware = None


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and clean up application state."""
    state.robot = ScorbotIII()
    yield
    if state.hardware is not None:
        state.hardware.disconnect()


# ── FastAPI app ────────────────────────────────────────────────────────────

app = FastAPI(
    title="Robotic Writer API",
    description=(
        "REST API for simulating and controlling a Scorbot III robotic arm "
        "that picks letter blocks from a circular arrangement and places "
        "them in a line to write words."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Kinematics endpoints ──────────────────────────────────────────────────

@app.post("/api/kinematics/forward")
async def forward_kinematics(req: JointAnglesRequest):
    """Compute end-effector position from joint angles."""
    joint_state = JointState.from_degrees(req.angles_deg, req.gripper_mm)
    valid, violations = joint_state.is_within_limits()
    if not valid:
        raise HTTPException(400, detail=f"Joint limits violated: {violations}")

    result = state.fk.compute(joint_state)
    positions = state.fk.joint_positions(joint_state)

    return {
        "end_effector": {
            "x": float(result["position"][0]),
            "y": float(result["position"][1]),
            "z": float(result["position"][2]),
        },
        "orientation": result["orientation"].tolist(),
        "joint_positions": positions.tolist(),
    }


@app.post("/api/kinematics/inverse")
async def inverse_kinematics(req: CartesianRequest):
    """Compute joint angles for a target Cartesian position."""
    try:
        target = np.array([req.x, req.y, req.z])
        joint_state = state.ik.compute_for_position(target, req.approach_angle_deg)
        fk_result = state.fk.compute(joint_state)

        return {
            "angles_deg": joint_state.angles_deg.tolist(),
            "gripper_mm": joint_state.gripper_mm,
            "achieved_position": {
                "x": float(fk_result["position"][0]),
                "y": float(fk_result["position"][1]),
                "z": float(fk_result["position"][2]),
            },
            "motor_steps": joint_state.to_motor_steps(),
        }
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


# ── Writer simulation endpoints ───────────────────────────────────────────

@app.post("/api/writer/simulate")
async def simulate_writing(req: WriteRequest):
    """Run the full writing simulation and return trajectory data."""
    try:
        block_circle = BlockCircle(
            radius_mm=req.block_radius_mm,
            block_height_mm=req.block_height_mm,
            min_angular_separation_deg=req.min_angular_separation_deg,
        )
        writing_line = WritingLine(
            radius_mm=req.writing_radius_mm,
            center_angle_deg=req.writing_center_angle_deg,
            angular_spacing_deg=req.writing_angular_spacing_deg,
        )
        robot = ScorbotIII()
        writer = RoboticWriter(robot=robot, block_circle=block_circle, writing_line=writing_line)

        action_log = writer.write_text(req.text)
        sim_data = writer.get_simulation_data()

        return {
            "text": req.text,
            "action_log": action_log,
            "simulation": sim_data,
            "summary": {
                "total_actions": len(action_log),
                "characters_placed": sum(1 for a in action_log if a["action"] == "place"),
                "trajectory_points": len(sim_data["trajectory"]["timestamps"]),
            },
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/api/writer/config")
async def get_writer_config():
    """Get current writer configuration defaults."""
    return {
        "block_circle": {
            "radius_mm": 280.0,
            "block_height_mm": 50.0,
            "block_size_mm": 25.0,
            "min_angular_separation_deg": 8.0,
            "charset": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        },
        "writing_line": {
            "radius_mm": 300.0,
            "center_angle_deg": -25.0,
            "angular_spacing_deg": 4.0,
            "height_mm": 50.0,
        },
        "robot": {
            "safe_height_mm": 75.0,
            "approach_angle_deg": -70.0,
            "gripper_open_mm": 40.0,
            "home_position_xyz": [456.0, 0.0, 189.0],
        },
    }


# ── Robot state endpoints ─────────────────────────────────────────────────

@app.get("/api/robot/state")
async def get_robot_state():
    """Get current robot joint state and end-effector position."""
    fk_result = state.fk.compute(state.robot.joint_state)
    return {
        "joint_angles_deg": state.robot.joint_state.angles_deg.tolist(),
        "gripper_mm": state.robot.joint_state.gripper_mm,
        "end_effector": {
            "x": float(fk_result["position"][0]),
            "y": float(fk_result["position"][1]),
            "z": float(fk_result["position"][2]),
        },
        "status": state.robot.status.value,
    }


# ── Hardware endpoints ─────────────────────────────────────────────────────

@app.post("/api/hardware/connect")
async def connect_hardware(req: HardwareConnectRequest):
    """Connect to a hardware adapter."""
    from ..hardware import MatlabAdapter, ArduinoAdapter, SerialAdapter

    adapters = {
        "matlab": MatlabAdapter,
        "arduino": ArduinoAdapter,
        "serial": SerialAdapter,
    }

    adapter_cls = adapters.get(req.adapter_type)
    if adapter_cls is None:
        raise HTTPException(400, detail=f"Unknown adapter: {req.adapter_type}")

    adapter = adapter_cls()
    kwargs = {}
    if req.port:
        kwargs["port"] = req.port
    if req.baud:
        kwargs["baud"] = req.baud

    success = adapter.connect(**kwargs)
    if not success:
        raise HTTPException(500, detail=f"Failed to connect to {req.adapter_type}")

    state.hardware = adapter
    return {"status": "connected", "adapter": req.adapter_type}


@app.post("/api/hardware/disconnect")
async def disconnect_hardware():
    """Disconnect from current hardware adapter."""
    if state.hardware is not None:
        state.hardware.disconnect()
        state.hardware = None
    return {"status": "disconnected"}


@app.get("/api/hardware/status")
async def hardware_status():
    """Check hardware connection status."""
    if state.hardware is None:
        return {"connected": False, "adapter": None}
    return {
        "connected": state.hardware.is_connected(),
        "adapter": type(state.hardware).__name__,
    }


@app.get("/api/trajectory-frames")
async def trajectory_frames(
    text: str = "HELLO",
    block_radius_mm: float = 280.0,
    block_height_mm: float = 50.0,
    min_angular_separation_deg: float = 8.0,
    writing_radius_mm: float = 300.0,
    writing_center_angle_deg: float = -25.0,
    writing_angular_spacing_deg: float = 4.0,
    frame_step: int = 5,
):
    """Return animation frames for a writing trajectory.

    Computes the full pick-and-place trajectory for the given text and
    returns a list of frames suitable for Plotly animation. Each frame
    contains joint positions, end-effector position, gripper aperture,
    and timestamp.

    The frontend can use these frames with plotly.graph_objects.Frame
    to animate the robot arm movement in 3D.

    Args:
        text: Text to write (max 15 characters).
        block_radius_mm: Radius of the letter block circle.
        block_height_mm: Height of blocks above ground.
        min_angular_separation_deg: Angular separation between blocks.
        writing_radius_mm: Radius of the writing arc.
        writing_center_angle_deg: Center angle of the writing arc.
        writing_angular_spacing_deg: Angular spacing between writing slots.
        frame_step: Sample every N-th trajectory step to reduce payload.
            Set to 1 for all frames.

    Returns:
        JSON with:
        - text: The input text
        - total_steps: Total trajectory steps before subsampling
        - frames: List of frame dicts with keys:
            - index: Frame index
            - timestamp: Time in seconds
            - joint_angles_deg: [j1, j2, j3, j4, j5]
            - joint_positions: [[x,y,z], ...] for each joint frame
            - end_effector: {x, y, z}
            - gripper_mm: Gripper aperture
    """
    if not text or len(text) > 15:
        raise HTTPException(400, detail="Text must be 1-15 characters")

    text = text.upper()
    frame_step = max(1, min(frame_step, 100))

    try:
        from ..core.kinematics import ForwardKinematics

        block_circle = BlockCircle(
            radius_mm=block_radius_mm,
            block_height_mm=block_height_mm,
            min_angular_separation_deg=min_angular_separation_deg,
        )
        writing_line = WritingLine(
            radius_mm=writing_radius_mm,
            center_angle_deg=writing_center_angle_deg,
            angular_spacing_deg=writing_angular_spacing_deg,
        )
        robot = ScorbotIII(interpolation_steps=30)
        writer = RoboticWriter(
            robot=robot,
            block_circle=block_circle,
            writing_line=writing_line,
            infinite_replacement=True,
        )

        action_log = writer.write_text(text)
        traj_data = robot.get_trajectory_data()

        fk = ForwardKinematics()
        total_steps = len(traj_data["timestamps"])

        frames = []
        for i in range(0, total_steps, frame_step):
            angles_deg = traj_data["joint_angles_deg"][i]
            js = JointState.from_degrees(angles_deg)
            joint_positions = fk.joint_positions(js)

            frames.append({
                "index": len(frames),
                "timestamp": traj_data["timestamps"][i],
                "joint_angles_deg": angles_deg,
                "joint_positions": joint_positions.tolist(),
                "end_effector": {
                    "x": traj_data["positions"][i][0],
                    "y": traj_data["positions"][i][1],
                    "z": traj_data["positions"][i][2],
                },
                "gripper_mm": traj_data["gripper"][i],
            })

        return {
            "text": text,
            "total_steps": total_steps,
            "frame_step": frame_step,
            "n_frames": len(frames),
            "action_log": action_log,
            "frames": frames,
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))


class RRTPlanRequest(BaseModel):
    """Request for RRT path planning."""
    start_deg: list[float] = Field(..., min_length=5, max_length=5)
    goal_deg: list[float] = Field(..., min_length=5, max_length=5)
    step_size: float = Field(5.0, ge=1.0, le=30.0)
    max_iterations: int = Field(1000, ge=100, le=10000)
    goal_threshold: float = Field(3.0, ge=0.5, le=20.0)
    smooth: bool = True


@app.post("/api/rrt-plan")
async def rrt_plan(req: RRTPlanRequest):
    """Plan a collision-free path in joint space using RRT.

    Returns a list of joint configurations (degrees) from start to goal
    that respect joint limits. Optionally smooths the path.
    """
    joint_limits = np.array(JOINT_LIMITS_DEG)
    planner = RRTPlanner(
        joint_limits=joint_limits,
        step_size=req.step_size,
        max_iterations=req.max_iterations,
        goal_threshold=req.goal_threshold,
    )

    start = np.array(req.start_deg)
    goal = np.array(req.goal_deg)

    # Validate start and goal are within limits
    if not planner._within_limits(start):
        raise HTTPException(400, detail="Start configuration violates joint limits")
    if not planner._within_limits(goal):
        raise HTTPException(400, detail="Goal configuration violates joint limits")

    path = planner.plan(start, goal, seed=42)
    if path is None:
        raise HTTPException(
            404,
            detail="RRT failed to find a path within the iteration limit",
        )

    if req.smooth:
        path = planner.smooth_path(path, seed=42)

    return {
        "path": [p.tolist() for p in path],
        "num_waypoints": len(path),
        "start_deg": req.start_deg,
        "goal_deg": req.goal_deg,
    }


@app.get("/api/cursive-path")
async def cursive_path(
    text: str = "hello",
    letter_width: float = 15.0,
    letter_height: float = 20.0,
    spacing: float = 2.0,
    points_per_segment: int = 15,
):
    """Generate a cursive Bezier path for the given text.

    Returns a list of (x, y) points forming a continuous cursive path.
    Pen-up events (spaces between words) are represented as null entries.

    Args:
        text: Text to write in cursive (will be lowercased).
        letter_width: Width of each letter in mm.
        letter_height: Height of each letter in mm.
        spacing: Extra spacing between letters in mm.
        points_per_segment: Points per Bezier segment.
    """
    if not text or len(text) > 100:
        raise HTTPException(400, detail="Text must be 1-100 characters")

    path = generate_cursive_path(
        text,
        letter_width=letter_width,
        letter_height=letter_height,
        spacing=spacing,
        points_per_segment=points_per_segment,
    )

    # Separate into segments (split at None pen-up markers)
    segments = []
    current_segment = []
    for pt in path:
        if pt is None:
            if current_segment:
                segments.append(current_segment)
                current_segment = []
        else:
            current_segment.append({"x": pt[0], "y": pt[1]})
    if current_segment:
        segments.append(current_segment)

    return {
        "text": text.lower(),
        "total_points": sum(len(s) for s in segments),
        "num_segments": len(segments),
        "segments": segments,
        "path": [{"x": pt[0], "y": pt[1]} if pt is not None else None for pt in path],
    }


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}
