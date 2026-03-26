"""Tests for the kinematics engine."""

import math

import numpy as np
import pytest

from src.core.kinematics import (
    ForwardKinematics,
    InverseKinematics,
    JointState,
    DHParameters,
)


class TestForwardKinematics:
    def setup_method(self):
        self.fk = ForwardKinematics()

    def test_home_position(self):
        """At all-zero angles, the end-effector should be at a known position."""
        state = JointState()
        result = self.fk.compute(state)
        pos = result["position"]
        # At home: x should be positive, y ~0, z should be D1
        assert pos[0] > 0
        assert abs(pos[1]) < 1e-6
        assert pos[2] > 0

    def test_joint_positions_shape(self):
        """Joint positions should have 6 rows (base + 5 joints)."""
        state = JointState()
        positions = self.fk.joint_positions(state)
        assert positions.shape == (6, 3)

    def test_base_rotation_changes_xy(self):
        """Rotating the base should move the end-effector in the XY plane."""
        state0 = JointState()
        state45 = JointState.from_degrees([45.0, 0, 0, 0, 0])

        pos0 = self.fk.compute(state0)["position"]
        pos45 = self.fk.compute(state45)["position"]

        # Y should differ
        assert abs(pos45[1]) > 1.0
        # Z should be approximately the same
        assert abs(pos0[2] - pos45[2]) < 1e-3


class TestInverseKinematics:
    def setup_method(self):
        self.fk = ForwardKinematics()
        self.ik = InverseKinematics()

    def test_roundtrip(self):
        """compute_for_position -> FK should reach the target position."""
        # Use a known reachable position in the workspace
        target = np.array([350.0, 0.0, 100.0])
        recovered = self.ik.compute_for_position(target, approach_angle_deg=-90.0)
        recovered_pos = self.fk.compute(recovered)["position"]

        np.testing.assert_allclose(target, recovered_pos, atol=2.0)

    def test_unreachable_target(self):
        """A target far beyond the workspace should raise ValueError."""
        with pytest.raises(ValueError):
            self.ik.compute_for_position(np.array([2000.0, 0.0, 0.0]))


class TestJointState:
    def test_within_limits(self):
        state = JointState.from_degrees([0.0, 0.0, 0.0, 0.0, 0.0])
        valid, violations = state.is_within_limits()
        assert valid
        assert len(violations) == 0

    def test_exceeds_limits(self):
        state = JointState.from_degrees([200.0, 0.0, 0.0, 0.0, 0.0])
        valid, violations = state.is_within_limits()
        assert not valid
        assert len(violations) > 0

    def test_motor_steps_conversion(self):
        state = JointState.from_degrees([9.4, 11.75, 11.75, 45.8, 45.8])
        steps = state.to_motor_steps()
        assert steps[0] == 100  # 9.4 / 0.094
        assert steps[1] == 100  # 11.75 / 0.1175
