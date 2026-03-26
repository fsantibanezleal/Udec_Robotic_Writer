"""Robotic Writer logic: letter-block selection from a circular arrangement and sequential placement.

The writer orchestrates the full pick-and-place cycle:
1. Parse input text into individual characters.
2. Map each character to a physical block on the circular arc.
3. For each character:
   a. Rotate base to the block's angular position on the arc.
   b. Extend arm to pick up the block.
   c. Retract to safe height.
   d. Rotate to the writing line position.
   e. Place the block at the next sequential slot.
4. Return to home when done.

Block Circle Geometry:
    - N blocks are arranged on an arc of radius R centered on the robot base.
    - The angular span is determined by the minimum angular separation delta_theta
      required for the gripper to safely manipulate each block.
    - Block i is at angle: theta_start + i * delta_theta
    - Writing line is a straight segment at a fixed Y offset from the robot.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .robot import ScorbotIII, TrajectoryPlan, MotionStep


# Default character set: A-Z plus Spanish special characters
DEFAULT_CHARSET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

SPANISH_MAP = {
    "a": "A", "b": "B", "c": "C", "d": "D", "e": "E", "f": "F",
    "g": "G", "h": "H", "i": "I", "j": "J", "k": "K", "l": "L",
    "m": "M", "n": "N", "o": "O", "p": "P", "q": "Q", "r": "R",
    "s": "S", "t": "T", "u": "U", "v": "V", "w": "W", "x": "X",
    "y": "Y", "z": "Z",
}


@dataclass
class LetterBlock:
    """A physical letter block positioned on the circular arc.

    Attributes:
        character: The letter on this block.
        index: Position index on the arc (0-based).
        angle_rad: Angular position on the arc from robot base.
        position_xyz: 3D coordinates of the block center.
        is_available: Whether this block has not yet been picked.
    """

    character: str
    index: int
    angle_rad: float
    position_xyz: np.ndarray
    is_available: bool = True


@dataclass
class BlockCircle:
    """Circular arrangement of letter blocks around the robot.

    The blocks sit on an arc at a fixed radius from the robot base,
    at a fixed height (table level). The arc is centered on the robot's
    forward direction (theta=0) and spans symmetrically.

    Attributes:
        radius_mm: Distance from robot base to block centers.
        block_height_mm: Z-coordinate of blocks (table surface).
        block_size_mm: Side length of each cubic block.
        min_angular_separation_deg: Minimum angle between adjacent blocks.
        charset: String of characters, one per block.
    """

    radius_mm: float = 280.0
    block_height_mm: float = 50.0
    block_size_mm: float = 25.0
    min_angular_separation_deg: float = 8.0
    charset: str = DEFAULT_CHARSET

    blocks: list[LetterBlock] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        """Compute block positions on the arc."""
        self._build_blocks()

    def _build_blocks(self) -> None:
        """Place blocks on a symmetric arc centered at theta=0."""
        n = len(self.charset)
        delta = math.radians(self.min_angular_separation_deg)
        total_span = (n - 1) * delta
        theta_start = -total_span / 2

        self.blocks = []
        for i, char in enumerate(self.charset):
            angle = theta_start + i * delta
            x = self.radius_mm * math.cos(angle)
            y = self.radius_mm * math.sin(angle)
            z = self.block_height_mm

            self.blocks.append(LetterBlock(
                character=char,
                index=i,
                angle_rad=angle,
                position_xyz=np.array([x, y, z]),
            ))

    def find_block(self, character: str) -> Optional[LetterBlock]:
        """Find the first available block matching a character (case-insensitive)."""
        char_upper = character.upper()
        for block in self.blocks:
            if block.character == char_upper and block.is_available:
                return block
        return None

    def get_arc_points(self) -> np.ndarray:
        """Get all block positions as (N, 3) array for visualization."""
        return np.array([b.position_xyz for b in self.blocks])

    def get_arc_angles_deg(self) -> list[float]:
        """Get all block angles in degrees."""
        return [math.degrees(b.angle_rad) for b in self.blocks]

    def reset(self) -> None:
        """Mark all blocks as available again."""
        for block in self.blocks:
            block.is_available = True


@dataclass
class WritingLine:
    """Arc-shaped target area where blocks are placed to form the word.

    Blocks are placed sequentially along an arc at a fixed radius from the
    robot base, ensuring all positions remain within the robot's workspace.
    The arc is centered at a configurable angle with configurable angular spacing.

    Attributes:
        radius_mm: Distance from robot base to slot centers.
        center_angle_deg: Center angle of the writing arc (degrees, 0=forward).
        angular_spacing_deg: Angular separation between slots.
        height_mm: Z-coordinate of slots (table surface).
    """

    radius_mm: float = 300.0
    center_angle_deg: float = -25.0
    angular_spacing_deg: float = 4.0
    height_mm: float = 50.0

    def slot_position(self, index: int) -> np.ndarray:
        """Get the 3D position for the i-th block slot on the arc."""
        angle = math.radians(self.center_angle_deg) + index * math.radians(self.angular_spacing_deg)
        x = self.radius_mm * math.cos(angle)
        y = self.radius_mm * math.sin(angle)
        return np.array([x, y, self.height_mm])

    def get_slot_positions(self, num_slots: int) -> np.ndarray:
        """Get positions of multiple slots as (N, 3) array."""
        return np.array([self.slot_position(i) for i in range(num_slots)])


class RoboticWriter:
    """Orchestrator for the full pick-and-place writing sequence.

    Coordinates the ScorbotIII robot to pick character blocks from the
    BlockCircle and place them on the WritingLine to spell a word.
    """

    SAFE_HEIGHT_MM = 75.0  # Height to lift to between pick and place
    APPROACH_ANGLE_DEG = -70.0  # Near-vertical approach (tilted for better reachability)
    GRIPPER_OPEN_MM = 40.0
    PICK_DURATION = 1.5
    MOVE_DURATION = 2.0
    PLACE_DURATION = 1.5

    def __init__(
        self,
        robot: Optional[ScorbotIII] = None,
        block_circle: Optional[BlockCircle] = None,
        writing_line: Optional[WritingLine] = None,
    ):
        self.robot = robot or ScorbotIII()
        self.block_circle = block_circle or BlockCircle()
        self.writing_line = writing_line or WritingLine()
        self._placed_count = 0
        self._action_log: list[dict] = []

    def write_text(self, text: str) -> list[dict]:
        """Execute the full writing sequence for a text string.

        Args:
            text: The text to write. Spaces are represented as gaps.

        Returns:
            List of action descriptions documenting each step.
        """
        self.robot.reset_trajectory_log()
        self._placed_count = 0
        self._action_log = []

        self._log_action("start", f"Begin writing: '{text}'")
        self.robot.go_home()
        self._log_action("home", "Moved to home position")

        for i, char in enumerate(text):
            if char == " ":
                self._placed_count += 1
                self._log_action("space", f"Slot {i}: space (skip)")
                continue

            block = self.block_circle.find_block(char)
            if block is None:
                self._log_action("skip", f"Slot {i}: '{char}' not found, skipping")
                self._placed_count += 1
                continue

            self._pick_and_place(block, self._placed_count, char, i)
            self._placed_count += 1

        self.robot.go_home()
        self._log_action("done", f"Writing complete. Returned to home.")

        return self._action_log

    def _pick_and_place(
        self, block: LetterBlock, slot_index: int, char: str, text_index: int
    ) -> None:
        """Execute pick-and-place for a single block."""
        block_pos = block.position_xyz
        safe_above_block = block_pos.copy()
        safe_above_block[2] = self.SAFE_HEIGHT_MM

        place_pos = self.writing_line.slot_position(slot_index)
        safe_above_place = place_pos.copy()
        safe_above_place[2] = self.SAFE_HEIGHT_MM

        # 1. Open gripper
        self.robot.open_gripper(self.GRIPPER_OPEN_MM)
        self._log_action("open_gripper", f"Open gripper for '{char}'")

        # 2. Move above block
        self.robot.move_to_xyz(safe_above_block, self.APPROACH_ANGLE_DEG, self.MOVE_DURATION)
        self._log_action("move_above_block", f"Move above block '{char}' at angle {math.degrees(block.angle_rad):.1f} deg")

        # 3. Lower to block
        self.robot.move_to_xyz(block_pos, self.APPROACH_ANGLE_DEG, self.PICK_DURATION)
        self._log_action("lower_to_block", f"Lower to block '{char}'")

        # 4. Close gripper (pick)
        self.robot.close_gripper()
        block.is_available = False
        self._log_action("pick", f"Picked block '{char}'")

        # 5. Lift to safe height
        self.robot.move_to_xyz(safe_above_block, self.APPROACH_ANGLE_DEG, self.PICK_DURATION)
        self._log_action("lift", f"Lift block '{char}'")

        # 6. Move above placement slot
        self.robot.move_to_xyz(safe_above_place, self.APPROACH_ANGLE_DEG, self.MOVE_DURATION)
        self._log_action("move_above_slot", f"Move above slot {slot_index}")

        # 7. Lower to placement
        self.robot.move_to_xyz(place_pos, self.APPROACH_ANGLE_DEG, self.PLACE_DURATION)
        self._log_action("lower_to_slot", f"Lower to slot {slot_index}")

        # 8. Open gripper (place)
        self.robot.open_gripper(self.GRIPPER_OPEN_MM)
        self._log_action("place", f"Placed block '{char}' at slot {slot_index}")

        # 9. Lift to safe height
        self.robot.move_to_xyz(safe_above_place, self.APPROACH_ANGLE_DEG, self.PICK_DURATION)
        self._log_action("lift_after_place", f"Lift after placing '{char}'")

    def _log_action(self, action_type: str, description: str) -> None:
        """Record an action for the activity log."""
        self._action_log.append({
            "action": action_type,
            "description": description,
            "robot_position": self.robot.end_effector_position.tolist(),
            "joint_angles_deg": self.robot.joint_state.angles_deg.tolist(),
            "gripper_mm": self.robot.joint_state.gripper_mm,
        })

    def get_simulation_data(self) -> dict:
        """Get complete simulation data for frontend visualization."""
        return {
            "trajectory": self.robot.get_trajectory_data(),
            "action_log": self._action_log,
            "block_circle": {
                "positions": self.block_circle.get_arc_points().tolist(),
                "characters": [b.character for b in self.block_circle.blocks],
                "available": [b.is_available for b in self.block_circle.blocks],
                "angles_deg": self.block_circle.get_arc_angles_deg(),
                "radius_mm": self.block_circle.radius_mm,
            },
            "writing_line": {
                "radius_mm": self.writing_line.radius_mm,
                "center_angle_deg": self.writing_line.center_angle_deg,
                "angular_spacing_deg": self.writing_line.angular_spacing_deg,
                "height_mm": self.writing_line.height_mm,
            },
        }

    def reset(self) -> None:
        """Reset the writer for a new word."""
        self.block_circle.reset()
        self.robot.go_home()
        self.robot.reset_trajectory_log()
        self._placed_count = 0
        self._action_log = []
