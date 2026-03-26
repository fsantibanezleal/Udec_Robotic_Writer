"""Forward and Inverse Kinematics for a 5-DOF robotic arm using Denavit-Hartenberg convention.

This module implements the kinematic model for the Scorbot III robotic arm,
including DH parameter definitions, forward kinematics (joint angles -> end-effector pose),
and inverse kinematics (desired pose -> joint angles).

Reference: Denavit, J. & Hartenberg, R.S. (1955). "A kinematic notation for
lower-pair mechanisms based on matrices." ASME Journal of Applied Mechanics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class DHParameters:
    """Denavit-Hartenberg parameters for a single joint.

    Each row of the DH table describes one link-joint pair:
        alpha_i : twist angle between z_{i-1} and z_i about x_i  [rad]
        d_i     : offset along z_{i-1} from origin to x_i intersection  [mm]
        a_i     : link length along x_i  [mm]
        theta_i : joint angle about z_{i-1} (variable for revolute joints) [rad]
    """

    alpha: float
    d: float
    a: float
    theta_offset: float = 0.0

    def transformation_matrix(self, theta: float) -> np.ndarray:
        """Compute the 4x4 homogeneous transformation matrix A_i.

        Args:
            theta: Joint angle in radians (added to theta_offset).

        Returns:
            4x4 numpy array representing the transformation from frame i-1 to frame i.
        """
        t = theta + self.theta_offset
        ct, st = math.cos(t), math.sin(t)
        ca, sa = math.cos(self.alpha), math.sin(self.alpha)

        return np.array([
            [ct, -ca * st,  sa * st, self.a * ct],
            [st,  ca * ct, -sa * ct, self.a * st],
            [0.0,     sa,       ca,      self.d],
            [0.0,    0.0,      0.0,        1.0],
        ])


# --- Scorbot III DH Parameters ---
# Link lengths and offsets in mm (from original MATLAB code)
L1 = 16.0    # Base link length
L2 = 220.0   # Shoulder link length
L3 = 220.0   # Elbow link length
D1 = 340.0   # Base height offset
D5 = 151.0   # Wrist-to-gripper offset

SCORBOT_DH_TABLE: list[DHParameters] = [
    DHParameters(alpha=-math.pi / 2, d=D1, a=L1),   # Joint 1 - Base
    DHParameters(alpha=0.0,          d=0.0, a=L2),   # Joint 2 - Shoulder
    DHParameters(alpha=0.0,          d=0.0, a=L3),   # Joint 3 - Elbow
    DHParameters(alpha=-math.pi / 2, d=0.0, a=0.0),  # Joint 4 - Pitch
    DHParameters(alpha=0.0,          d=D5,  a=0.0),   # Joint 5 - Roll
]

# Joint limits in degrees [min, max]
JOINT_LIMITS_DEG: list[tuple[float, float]] = [
    (-126.5, 126.5),   # Base
    (-120.0, 63.0),    # Shoulder
    (-90.0, 90.0),     # Elbow
    (-250.0, 40.0),    # Pitch
    (-180.0, 180.0),   # Roll
]

# Motor step resolutions (degrees per step)
MOTOR_STEP_DEG: list[float] = [
    0.094,    # Motor 1 - Base
    0.1175,   # Motor 2 - Shoulder
    0.1175,   # Motor 3 - Elbow
    0.458,    # Motor 4 - Pitch
    0.458,    # Motor 5 - Roll
]

GRIPPER_STEPS_PER_MM = 6.7797
GRIPPER_MAX_APERTURE_MM = 59.0


@dataclass
class JointState:
    """Current state of all robot joints."""

    angles_rad: np.ndarray = field(default_factory=lambda: np.zeros(5))
    gripper_mm: float = 0.0

    @property
    def angles_deg(self) -> np.ndarray:
        return np.degrees(self.angles_rad)

    @classmethod
    def from_degrees(cls, angles_deg: list[float], gripper_mm: float = 0.0) -> JointState:
        return cls(angles_rad=np.radians(angles_deg), gripper_mm=gripper_mm)

    def is_within_limits(self) -> tuple[bool, list[str]]:
        """Check if all joints are within their mechanical limits."""
        violations = []
        for i, (lo, hi) in enumerate(JOINT_LIMITS_DEG):
            deg = math.degrees(self.angles_rad[i])
            if deg < lo or deg > hi:
                violations.append(
                    f"Joint {i + 1}: {deg:.1f} deg out of range [{lo}, {hi}]"
                )
        if self.gripper_mm < 0 or self.gripper_mm > GRIPPER_MAX_APERTURE_MM:
            violations.append(
                f"Gripper: {self.gripper_mm:.1f} mm out of range [0, {GRIPPER_MAX_APERTURE_MM}]"
            )
        return len(violations) == 0, violations

    def to_motor_steps(self) -> list[int]:
        """Convert joint angles to motor step counts."""
        steps = []
        for i in range(5):
            deg = math.degrees(self.angles_rad[i])
            steps.append(round(deg / MOTOR_STEP_DEG[i]))
        steps.append(round(self.gripper_mm * GRIPPER_STEPS_PER_MM))
        return steps


class ForwardKinematics:
    """Compute end-effector pose from joint angles using DH convention.

    The forward kinematics chain multiplies individual transformation matrices:
        T_total = A_1 * A_2 * A_3 * A_4 * A_5

    The end-effector position is extracted from the last column of T_total.
    """

    def __init__(self, dh_table: Optional[list[DHParameters]] = None):
        self.dh_table = dh_table or SCORBOT_DH_TABLE

    def compute(self, joint_state: JointState) -> dict:
        """Compute the full forward kinematics.

        Args:
            joint_state: Current joint angles.

        Returns:
            Dictionary with 'position' (xyz in mm), 'orientation' (3x3 rotation matrix),
            'transform' (full 4x4 matrix), and 'intermediate_transforms' for visualization.
        """
        T = np.eye(4)
        intermediates = [T.copy()]

        for i, dh in enumerate(self.dh_table):
            A_i = dh.transformation_matrix(joint_state.angles_rad[i])
            T = T @ A_i
            intermediates.append(T.copy())

        return {
            "position": T[:3, 3].copy(),
            "orientation": T[:3, :3].copy(),
            "transform": T.copy(),
            "intermediate_transforms": intermediates,
        }

    def joint_positions(self, joint_state: JointState) -> np.ndarray:
        """Get 3D positions of each joint frame origin (for visualization).

        Returns:
            (N+1, 3) array where row 0 is the base and row N is the end-effector.
        """
        result = self.compute(joint_state)
        positions = np.array([t[:3, 3] for t in result["intermediate_transforms"]])
        return positions


class InverseKinematics:
    """Compute joint angles from desired end-effector position and orientation.

    Uses the analytical closed-form solution specific to the Scorbot III geometry:
    1. theta1 from atan2(y, x) of the target position
    2. theta5 from the orientation matrix and theta1
    3. theta3 from the cosine law applied to the 2-link planar arm
    4. theta2 from the planar geometry
    5. theta4 = theta234 - theta2 - theta3
    """

    def __init__(self, dh_table: Optional[list[DHParameters]] = None):
        self.dh_table = dh_table or SCORBOT_DH_TABLE
        self.fk = ForwardKinematics(dh_table)

    def compute(
        self,
        target_xyz: np.ndarray,
        orientation: Optional[np.ndarray] = None,
    ) -> JointState:
        """Solve inverse kinematics for a target position.

        Args:
            target_xyz: Desired [x, y, z] position in mm.
            orientation: Optional 3x3 rotation matrix. If None, a default
                         top-down approach orientation is used.

        Returns:
            JointState with the computed joint angles.

        Raises:
            ValueError: If the target is unreachable.
        """
        qx, qy, qz = float(target_xyz[0]), float(target_xyz[1]), float(target_xyz[2])

        a1, a2, a3 = L1, L2, L3
        d1, d5 = D1, D5

        if orientation is None:
            # Default: gripper pointing down, approach from above
            orientation = np.array([
                [1.0, 0.0,  0.0],
                [0.0, 1.0,  0.0],
                [0.0, 0.0, -1.0],
            ])

        ux, uy, uz = orientation[0, 2], orientation[1, 2], orientation[2, 2]

        # Theta 1: base rotation
        if abs(qx) < 1e-10 and abs(qy) < 1e-10:
            theta1 = 0.0
        else:
            theta1 = math.atan2(qy, qx)

        # Theta 5: wrist roll
        inter5 = ux * math.sin(theta1) - uy * math.cos(theta1)
        inter5 = max(-1.0, min(1.0, inter5))
        theta5 = math.asin(inter5)

        # Combined pitch angle theta234
        cos5 = math.cos(theta5)
        if abs(cos5) < 1e-10:
            theta234 = 0.0
        else:
            num = -uz / cos5
            den = (ux * math.cos(theta1) + uy * math.sin(theta1)) / cos5
            theta234 = math.atan2(num, den)

        # Intermediate k1, k2 for the planar 2-link problem
        k1 = (qx * math.cos(theta1) + qy * math.sin(theta1)
               - a1 + d5 * math.sin(theta234))
        k2 = -qz + d1 - d5 * math.cos(theta234)

        # Theta 3: elbow (cosine law)
        cos3 = (k1**2 + k2**2 - a2**2 - a3**2) / (2 * a2 * a3)
        if abs(cos3) > 1.0 + 1e-6:
            raise ValueError(
                f"Target [{qx:.1f}, {qy:.1f}, {qz:.1f}] is unreachable "
                f"(cos(theta3) = {cos3:.4f})"
            )
        cos3 = max(-1.0, min(1.0, cos3))
        theta3 = math.acos(cos3)

        # Theta 2: shoulder
        denom = a2**2 + a3**2 + 2 * a2 * a3 * math.cos(theta3)
        if abs(denom) < 1e-10:
            raise ValueError("Singular configuration: cannot solve theta2.")
        cos2 = (k1 * (a2 + a3 * math.cos(theta3)) + k2 * a3 * math.sin(theta3)) / denom
        sin2 = (-k1 * a3 * math.sin(theta3) + k2 * (a2 + a3 * math.cos(theta3))) / denom
        theta2 = math.atan2(sin2, cos2)

        # Theta 4: pitch
        theta4 = theta234 - theta2 - theta3

        angles = np.array([theta1, theta2, theta3, theta4, theta5])
        state = JointState(angles_rad=angles)

        valid, violations = state.is_within_limits()
        if not valid:
            raise ValueError(f"Solution violates joint limits: {violations}")

        return state

    def compute_for_position(
        self,
        target_xyz: np.ndarray,
        approach_angle_deg: float = -90.0,
    ) -> JointState:
        """Simplified IK: reach a position with the gripper approaching from a given pitch.

        Args:
            target_xyz: Desired [x, y, z] in mm.
            approach_angle_deg: Pitch angle of approach (default -90 = straight down).

        Returns:
            JointState with computed angles.
        """
        pitch = math.radians(approach_angle_deg)
        # Build orientation: gripper z-axis aligned with approach direction
        cp, sp = math.cos(pitch), math.sin(pitch)
        # Compute base angle from target position
        base_angle = math.atan2(target_xyz[1], target_xyz[0])
        cb, sb = math.cos(base_angle), math.sin(base_angle)

        orientation = np.array([
            [cb * cp,  -sb, cb * sp],
            [sb * cp,   cb, sb * sp],
            [-sp,      0.0,     cp],
        ])

        return self.compute(target_xyz, orientation)
