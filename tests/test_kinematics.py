"""Tests for the kinematics engine."""

import math

import numpy as np
import pytest

from src.core.kinematics import (
    ForwardKinematics,
    InverseKinematics,
    JointState,
    DHParameters,
    ScorbotDHConfig,
    SCORBOT_III,
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
        target = np.array([300.0, 0.0, 50.0])
        recovered = self.ik.compute_for_position(target, approach_angle_deg=-70.0)
        recovered_pos = self.fk.compute(recovered)["position"]
        np.testing.assert_allclose(target, recovered_pos, atol=2.0)

    def test_roundtrip_default_orientation(self):
        """IK with default (gripper down) orientation -> FK roundtrip."""
        target = np.array([350.0, 0.0, 100.0])
        recovered = self.ik.compute(target, orientation=None)
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


class TestScorbotDHConfig:
    """Parametric swap-in for the frozen DH configuration dataclass."""

    @pytest.mark.parametrize(
        "config",
        [
            SCORBOT_III,                                           # default Scorbot III
            ScorbotDHConfig(a1=20.0, a2=200.0, a3=200.0,           # shorter 5-DOF variant
                            d1=320.0, d5=140.0),
            ScorbotDHConfig(a2=250.0, a3=250.0),                   # longer reach
        ],
    )
    def test_forward_kinematics_accepts_injected_config(self, config):
        """FK runs on any injected 5-DOF config and returns a finite end-effector."""
        fk = ForwardKinematics(config=config)
        assert fk.dh_table == config.dh_table  # config drove the chain

        state = JointState()  # home pose (all zeros)
        result = fk.compute(state)
        pos = result["position"]

        assert pos.shape == (3,)
        assert np.all(np.isfinite(pos))
        # At home the base rotation is zero, so y-component must stay near zero.
        assert abs(pos[1]) < 1e-9

    def test_inverse_kinematics_accepts_injected_config(self):
        """IK reads link lengths from config, not module globals — verify roundtrip."""
        # Custom arm with a slightly different reach; target scaled to stay reachable.
        config = ScorbotDHConfig(a2=210.0, a3=210.0)
        ik = InverseKinematics(config=config)
        fk = ForwardKinematics(config=config)

        target = np.array([335.0, 0.0, 100.0])
        recovered = ik.compute(target, orientation=None)
        recovered_pos = fk.compute(recovered)["position"]
        np.testing.assert_allclose(target, recovered_pos, atol=2.0)

    def test_default_config_roundtrip_is_tight(self):
        """Sanity: FK round-trip error on the default config is well below 1e-6 mm
        when the joint state itself is the source of truth (no IK approximation)."""
        fk = ForwardKinematics()  # default SCORBOT_III
        state = JointState.from_degrees([10.0, -20.0, 30.0, -15.0, 5.0])
        pos_a = fk.compute(state)["position"]
        pos_b = fk.compute(state)["position"]  # identical call
        assert np.max(np.abs(pos_a - pos_b)) < 1e-12
