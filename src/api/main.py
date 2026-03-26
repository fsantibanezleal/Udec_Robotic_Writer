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

from ..core.kinematics import ForwardKinematics, InverseKinematics, JointState
from ..core.robot import ScorbotIII
from ..core.writer import RoboticWriter, BlockCircle, WritingLine


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
    block_radius_mm: float = Field(350.0, ge=200.0, le=600.0)
    block_height_mm: float = Field(50.0, ge=0.0, le=200.0)
    min_angular_separation_deg: float = Field(8.0, ge=3.0, le=20.0)
    writing_line_x: float = 300.0
    writing_line_y: float = -200.0
    writing_line_z: float = 50.0
    block_spacing_mm: float = Field(30.0, ge=15.0, le=60.0)


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
            start_xyz=np.array([req.writing_line_x, req.writing_line_y, req.writing_line_z]),
            spacing_mm=req.block_spacing_mm,
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
            "radius_mm": 350.0,
            "block_height_mm": 50.0,
            "block_size_mm": 25.0,
            "min_angular_separation_deg": 8.0,
            "charset": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        },
        "writing_line": {
            "start_xyz": [300.0, -200.0, 50.0],
            "direction": [1.0, 0.0, 0.0],
            "spacing_mm": 30.0,
        },
        "robot": {
            "safe_height_mm": 150.0,
            "approach_angle_deg": -90.0,
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


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}
