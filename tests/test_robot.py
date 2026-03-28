"""Tests for the ScorbotIII robot model and writer logic."""

import math

import numpy as np
import pytest

from src.core.robot import ScorbotIII, MotionStatus
from src.core.writer import BlockCircle, WritingLine, RoboticWriter


class TestRobotCreation:
    def test_robot_has_5_dof(self):
        """ScorbotIII should initialize with a 5-element joint angle array."""
        robot = ScorbotIII()
        assert robot.joint_state.angles_rad.shape == (5,)

    def test_robot_starts_idle(self):
        """Robot should start in IDLE status."""
        robot = ScorbotIII()
        assert robot.status == MotionStatus.IDLE

    def test_robot_starts_at_home(self):
        """All joint angles should be zero at initialization."""
        robot = ScorbotIII()
        np.testing.assert_array_equal(robot.joint_state.angles_rad, np.zeros(5))

    def test_robot_gripper_starts_closed(self):
        """Gripper aperture should be 0 mm at initialization."""
        robot = ScorbotIII()
        assert robot.joint_state.gripper_mm == 0.0

    def test_end_effector_position_is_3d(self):
        """End-effector position should be a 3-element array."""
        robot = ScorbotIII()
        pos = robot.end_effector_position
        assert pos.shape == (3,)


class TestInterpolation:
    def test_cubic_smoothstep_endpoints(self):
        """Cubic smoothstep should map 0->0 and 1->1."""
        assert ScorbotIII._smoothstep(0.0, order=3) == 0.0
        assert ScorbotIII._smoothstep(1.0, order=3) == 1.0

    def test_quintic_smoothstep_endpoints(self):
        """Quintic smoothstep should map 0->0 and 1->1."""
        assert abs(ScorbotIII._smoothstep(0.0, order=5)) < 1e-15
        assert abs(ScorbotIII._smoothstep(1.0, order=5) - 1.0) < 1e-15

    def test_quintic_smoothstep_midpoint(self):
        """Quintic smoothstep at t=0.5 should be 0.5 (symmetric)."""
        val = ScorbotIII._smoothstep(0.5, order=5)
        assert abs(val - 0.5) < 1e-15

    def test_quintic_smoothstep_monotonic(self):
        """Quintic smoothstep should be monotonically increasing on [0, 1]."""
        t_values = np.linspace(0, 1, 100)
        s_values = [ScorbotIII._smoothstep(t, order=5) for t in t_values]
        for i in range(1, len(s_values)):
            assert s_values[i] >= s_values[i-1], \
                f"Not monotonic at t={t_values[i]}: {s_values[i]} < {s_values[i-1]}"

    def test_quintic_zero_acceleration_at_endpoints(self):
        """Quintic smoothstep should have near-zero second derivative at endpoints."""
        # Numerical second derivative at t=0 and t=1
        eps = 1e-6
        # At t=0: f''(0) via finite difference
        f0 = ScorbotIII._smoothstep(0.0, order=5)
        f1 = ScorbotIII._smoothstep(eps, order=5)
        f2 = ScorbotIII._smoothstep(2*eps, order=5)
        d2_start = (f2 - 2*f1 + f0) / eps**2
        assert abs(d2_start) < 1.0, f"Second derivative at t=0 should be ~0, got {d2_start}"

        # At t=1
        f0 = ScorbotIII._smoothstep(1.0 - 2*eps, order=5)
        f1 = ScorbotIII._smoothstep(1.0 - eps, order=5)
        f2 = ScorbotIII._smoothstep(1.0, order=5)
        d2_end = (f2 - 2*f1 + f0) / eps**2
        assert abs(d2_end) < 1.0, f"Second derivative at t=1 should be ~0, got {d2_end}"

    def test_robot_with_quintic_interpolation(self):
        """Robot initialized with quintic order should produce valid trajectory."""
        robot = ScorbotIII(interpolation_order=5)
        assert robot.interpolation_order == 5
        # Plan a move and verify it completes
        from src.core.kinematics import JointState
        target = JointState(angles_rad=np.array([0.1, 0.2, -0.1, 0.0, 0.05]))
        plan = robot.plan_joint_move(target, duration=1.0)
        assert len(plan.steps) == robot.interpolation_steps + 1
        # First step should be at start, last at target
        np.testing.assert_allclose(plan.steps[-1].joint_state.angles_rad,
                                   target.angles_rad, atol=1e-10)

    def test_cubic_vs_quintic_differ(self):
        """Cubic and quintic interpolation should produce different midpoint values."""
        cubic_mid = ScorbotIII._smoothstep(0.3, order=3)
        quintic_mid = ScorbotIII._smoothstep(0.3, order=5)
        assert cubic_mid != quintic_mid, "Cubic and quintic should differ at t=0.3"


class TestTrapezoidalProfile:
    def test_endpoints(self):
        """Trapezoidal profile should map t=0 -> 0 and t=t_total -> 1."""
        s0 = ScorbotIII._trapezoidal_profile(0.0, t_total=2.0)
        s1 = ScorbotIII._trapezoidal_profile(2.0, t_total=2.0)
        assert abs(s0) < 1e-10, f"s(0) should be 0, got {s0}"
        assert abs(s1 - 1.0) < 1e-10, f"s(t_total) should be 1, got {s1}"

    def test_monotonic(self):
        """Trapezoidal profile should be monotonically increasing."""
        t_total = 3.0
        t_values = np.linspace(0, t_total, 200)
        s_values = [ScorbotIII._trapezoidal_profile(t, t_total) for t in t_values]
        for i in range(1, len(s_values)):
            assert s_values[i] >= s_values[i-1] - 1e-12, \
                f"Not monotonic at t={t_values[i]}: {s_values[i]} < {s_values[i-1]}"

    def test_bounded_zero_one(self):
        """Profile values should stay in [0, 1]."""
        t_total = 2.0
        for t in np.linspace(0, t_total, 100):
            s = ScorbotIII._trapezoidal_profile(t, t_total)
            assert -1e-10 <= s <= 1.0 + 1e-10, f"s({t}) = {s} is out of [0, 1]"

    def test_triangle_profile(self):
        """Short duration should produce a triangle profile (no cruise phase)."""
        # v_max=1.0, a_max=2.0 -> t_accel=0.5. With t_total=0.5, 2*t_accel > t_total
        s_mid = ScorbotIII._trapezoidal_profile(0.25, t_total=0.5, v_max=1.0, a_max=2.0)
        assert 0.0 < s_mid < 1.0, f"Mid-point should be between 0 and 1, got {s_mid}"
        s_end = ScorbotIII._trapezoidal_profile(0.5, t_total=0.5, v_max=1.0, a_max=2.0)
        assert abs(s_end - 1.0) < 1e-10, f"End should be 1.0, got {s_end}"

    def test_symmetric_midpoint(self):
        """Profile at midpoint should be approximately 0.5 for symmetric trapezoidal."""
        t_total = 4.0
        s_mid = ScorbotIII._trapezoidal_profile(t_total / 2, t_total, v_max=1.0, a_max=2.0)
        assert abs(s_mid - 0.5) < 0.1, f"Midpoint should be ~0.5, got {s_mid}"


class TestBlockCircle:
    def test_default_has_26_blocks(self):
        """Default block circle should contain 26 letter blocks (A-Z)."""
        bc = BlockCircle()
        assert len(bc.blocks) == 26

    def test_blocks_on_circle(self):
        """All blocks should lie at the specified radius from the origin."""
        radius = 300.0
        bc = BlockCircle(radius_mm=radius)
        for block in bc.blocks:
            r = math.sqrt(block.position_xyz[0] ** 2 + block.position_xyz[1] ** 2)
            assert abs(r - radius) < 1e-6, f"Block '{block.character}' at radius {r}, expected {radius}"

    def test_blocks_at_correct_height(self):
        """All blocks should be at the specified table height."""
        bc = BlockCircle(block_height_mm=55.0)
        for block in bc.blocks:
            assert block.position_xyz[2] == 55.0

    def test_arc_is_symmetric(self):
        """The arc should be centered at theta=0 (symmetric about the X axis)."""
        bc = BlockCircle()
        angles = [b.angle_rad for b in bc.blocks]
        assert angles[0] < 0, "First block angle should be negative"
        assert angles[-1] > 0, "Last block angle should be positive"
        assert abs(angles[0] + angles[-1]) < 1e-6, "Arc should be symmetric"

    def test_find_block(self):
        """find_block should return the correct block for a given letter."""
        bc = BlockCircle()
        block_a = bc.find_block("A")
        assert block_a is not None
        assert block_a.character == "A"
        assert block_a.index == 0

    def test_find_block_case_insensitive(self):
        """find_block should be case-insensitive."""
        bc = BlockCircle()
        block = bc.find_block("z")
        assert block is not None
        assert block.character == "Z"


class TestWritingLine:
    def test_slot_positions_at_radius(self):
        """Writing line slots should be at the specified radius."""
        wl = WritingLine(radius_mm=320.0)
        for i in range(10):
            pos = wl.slot_position(i)
            r = math.sqrt(pos[0] ** 2 + pos[1] ** 2)
            assert abs(r - 320.0) < 1e-6

    def test_slot_positions_sequential(self):
        """Successive slots should be separated by the angular spacing."""
        wl = WritingLine(angular_spacing_deg=5.0)
        pos0 = wl.slot_position(0)
        pos1 = wl.slot_position(1)
        angle0 = math.atan2(pos0[1], pos0[0])
        angle1 = math.atan2(pos1[1], pos1[0])
        assert abs(math.degrees(angle1 - angle0) - 5.0) < 1e-6

    def test_get_slot_positions_shape(self):
        """get_slot_positions should return (N, 3) array."""
        wl = WritingLine()
        positions = wl.get_slot_positions(8)
        assert positions.shape == (8, 3)


class TestPickAndPlace:
    def test_write_text_returns_actions(self):
        """write_text should return a non-empty action log."""
        writer = RoboticWriter()
        actions = writer.write_text("AB")
        assert len(actions) > 0

    def test_trajectory_has_pick_and_place(self):
        """The action log should contain both 'pick' and 'place' actions."""
        writer = RoboticWriter()
        actions = writer.write_text("A")
        action_types = [a["action"] for a in actions]
        assert "pick" in action_types, "Expected a 'pick' action"
        assert "place" in action_types, "Expected a 'place' action"

    def test_space_is_skipped(self):
        """Spaces should produce a 'space' action, not a pick-and-place."""
        writer = RoboticWriter()
        actions = writer.write_text("A B")
        action_types = [a["action"] for a in actions]
        assert "space" in action_types

    def test_simulation_data_structure(self):
        """get_simulation_data should contain trajectory, block_circle, and writing_line."""
        writer = RoboticWriter()
        writer.write_text("HI")
        sim = writer.get_simulation_data()
        assert "trajectory" in sim
        assert "block_circle" in sim
        assert "writing_line" in sim
        assert len(sim["trajectory"]["positions"]) > 0

    def test_infinite_replacement_keeps_blocks(self):
        """With infinite replacement, blocks remain available after picking."""
        writer = RoboticWriter(infinite_replacement=True)
        writer.write_text("AA")
        action_types = [a["action"] for a in writer._action_log]
        pick_count = action_types.count("pick")
        assert pick_count == 2, "Should pick 'A' twice with infinite replacement"
