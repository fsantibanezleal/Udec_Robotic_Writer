"""Scorbot III robot model with state management, motion planning, and simulation.

Encapsulates the physical robot parameters, current joint state, and provides
high-level motion commands (move to joint angles, move to Cartesian position,
open/close gripper) with trajectory interpolation.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

from .kinematics import (
    ForwardKinematics,
    InverseKinematics,
    JointState,
    JOINT_LIMITS_DEG,
    GRIPPER_MAX_APERTURE_MM,
)


class MotionStatus(str, Enum):
    IDLE = "idle"
    MOVING = "moving"
    ERROR = "error"


@dataclass
class MotionStep:
    """A single step in a trajectory, used for simulation playback."""

    joint_state: JointState
    end_effector_xyz: np.ndarray
    timestamp: float
    gripper_mm: float
    description: str = ""


@dataclass
class TrajectoryPlan:
    """A planned trajectory: sequence of MotionSteps from start to goal."""

    steps: list[MotionStep] = field(default_factory=list)
    total_duration: float = 0.0

    @property
    def positions(self) -> np.ndarray:
        """(N, 3) array of end-effector positions along the trajectory."""
        return np.array([s.end_effector_xyz for s in self.steps])


class ScorbotIII:
    """High-level model of the Scorbot III robotic arm.

    Provides motion planning with linear interpolation in joint space,
    forward/inverse kinematics access, and trajectory recording for simulation.
    """

    HOME_POSITION_XYZ = np.array([456.0, 0.0, 189.0])

    def __init__(self, interpolation_steps: int = 50, speed_factor: float = 1.0):
        """Initialize the robot at home position.

        Args:
            interpolation_steps: Number of intermediate points for trajectory generation.
            speed_factor: Multiplier for simulated motion speed (1.0 = real-time).
        """
        self.fk = ForwardKinematics()
        self.ik = InverseKinematics()
        self.interpolation_steps = interpolation_steps
        self.speed_factor = speed_factor

        self.joint_state = JointState()
        self.status = MotionStatus.IDLE
        self.trajectory_log: list[MotionStep] = []

    @property
    def end_effector_position(self) -> np.ndarray:
        """Current end-effector XYZ position in mm."""
        result = self.fk.compute(self.joint_state)
        return result["position"]

    @property
    def joint_positions_3d(self) -> np.ndarray:
        """Current 3D positions of all joint frames."""
        return self.fk.joint_positions(self.joint_state)

    def plan_joint_move(
        self, target: JointState, duration: float = 2.0
    ) -> TrajectoryPlan:
        """Plan a linear interpolation in joint space from current state to target.

        Args:
            target: Goal joint angles.
            duration: Desired motion duration in seconds.

        Returns:
            TrajectoryPlan with interpolated steps.
        """
        plan = TrajectoryPlan(total_duration=duration)
        start_angles = self.joint_state.angles_rad.copy()
        end_angles = target.angles_rad.copy()
        start_gripper = self.joint_state.gripper_mm
        end_gripper = target.gripper_mm

        for i in range(self.interpolation_steps + 1):
            t = i / self.interpolation_steps
            # Smooth interpolation (cubic ease in-out)
            t_smooth = 3 * t**2 - 2 * t**3

            angles = start_angles + t_smooth * (end_angles - start_angles)
            gripper = start_gripper + t_smooth * (end_gripper - start_gripper)

            state = JointState(angles_rad=angles, gripper_mm=gripper)
            fk_result = self.fk.compute(state)

            step = MotionStep(
                joint_state=state,
                end_effector_xyz=fk_result["position"],
                timestamp=t * duration,
                gripper_mm=gripper,
            )
            plan.steps.append(step)

        return plan

    def plan_cartesian_move(
        self,
        target_xyz: np.ndarray,
        approach_angle_deg: float = -90.0,
        duration: float = 2.0,
        gripper_mm: Optional[float] = None,
    ) -> TrajectoryPlan:
        """Plan a move to a Cartesian position via IK.

        Args:
            target_xyz: Desired [x, y, z] in mm.
            approach_angle_deg: Gripper approach pitch angle.
            duration: Motion duration in seconds.
            gripper_mm: Target gripper aperture (None = keep current).

        Returns:
            TrajectoryPlan.
        """
        target_state = self.ik.compute_for_position(target_xyz, approach_angle_deg)
        if gripper_mm is not None:
            target_state.gripper_mm = gripper_mm
        else:
            target_state.gripper_mm = self.joint_state.gripper_mm
        return self.plan_joint_move(target_state, duration)

    def execute_plan(self, plan: TrajectoryPlan) -> None:
        """Execute a trajectory plan (update internal state and log).

        In simulation mode this instantly applies the trajectory. For real hardware,
        the hardware adapter sends commands step by step.
        """
        self.status = MotionStatus.MOVING
        for step in plan.steps:
            step.timestamp += (
                self.trajectory_log[-1].timestamp if self.trajectory_log else 0.0
            )
            self.trajectory_log.append(step)

        # Apply final state
        final = plan.steps[-1]
        self.joint_state = final.joint_state
        self.joint_state.gripper_mm = final.gripper_mm
        self.status = MotionStatus.IDLE

    def move_to_xyz(
        self,
        target_xyz: np.ndarray,
        approach_angle_deg: float = -90.0,
        duration: float = 2.0,
        gripper_mm: Optional[float] = None,
    ) -> TrajectoryPlan:
        """Plan and execute a Cartesian move."""
        plan = self.plan_cartesian_move(target_xyz, approach_angle_deg, duration, gripper_mm)
        self.execute_plan(plan)
        return plan

    def open_gripper(self, aperture_mm: float = 40.0, duration: float = 0.5) -> TrajectoryPlan:
        """Open the gripper to a specified aperture."""
        target = JointState(
            angles_rad=self.joint_state.angles_rad.copy(),
            gripper_mm=aperture_mm,
        )
        plan = self.plan_joint_move(target, duration)
        self.execute_plan(plan)
        return plan

    def close_gripper(self, duration: float = 0.5) -> TrajectoryPlan:
        """Close the gripper (aperture = 0)."""
        return self.open_gripper(0.0, duration)

    def go_home(self, duration: float = 3.0) -> TrajectoryPlan:
        """Move to home position."""
        home_state = JointState()  # All zeros
        plan = self.plan_joint_move(home_state, duration)
        self.execute_plan(plan)
        return plan

    def reset_trajectory_log(self) -> None:
        """Clear the recorded trajectory."""
        self.trajectory_log.clear()

    def get_trajectory_data(self) -> dict:
        """Get trajectory log as arrays for visualization."""
        if not self.trajectory_log:
            return {"timestamps": [], "positions": [], "gripper": []}
        return {
            "timestamps": [s.timestamp for s in self.trajectory_log],
            "positions": [s.end_effector_xyz.tolist() for s in self.trajectory_log],
            "gripper": [s.gripper_mm for s in self.trajectory_log],
            "joint_angles_deg": [s.joint_state.angles_deg.tolist() for s in self.trajectory_log],
        }
