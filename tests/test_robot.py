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
