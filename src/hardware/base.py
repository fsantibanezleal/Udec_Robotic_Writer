"""Abstract base class for hardware adapters.

Defines the interface that all hardware backends (MATLAB, Arduino, serial, etc.)
must implement to control the physical robot motors.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CommandType(str, Enum):
    """Types of motor commands."""
    MOVE = "move"
    STOP = "stop"
    HOME = "home"
    QUERY_POSITION = "query_position"
    QUERY_SWITCH = "query_switch"
    GRIPPER_OPEN = "gripper_open"
    GRIPPER_CLOSE = "gripper_close"


@dataclass
class MotorCommand:
    """A command to send to a motor controller.

    Attributes:
        motor_id: Motor number (1-5 for joints, 8 for gripper on Scorbot III).
        command_type: Type of command.
        steps: Number of steps to move (positive or negative).
        speed: Optional speed parameter (controller-dependent).
    """

    motor_id: int
    command_type: CommandType
    steps: int = 0
    speed: Optional[float] = None

    def to_scorbot_bytes(self) -> bytes:
        """Encode as Scorbot III serial protocol (original DDE/Winwedge format).

        Protocol: [motor_id, 'M', direction, d4, d3, d2, d1, CR]
        """
        if self.command_type == CommandType.STOP:
            return bytes([self.motor_id + 0x30, ord("P"), 13])

        if self.command_type == CommandType.QUERY_POSITION:
            return bytes([self.motor_id + 0x30, ord("Q"), 13])

        if self.command_type == CommandType.QUERY_SWITCH:
            return bytes([self.motor_id + 0x30, ord("L"), 13])

        direction = ord("+") if self.steps >= 0 else ord("-")
        abs_steps = min(abs(self.steps), 9999)
        d4 = (abs_steps // 1000) + 0x30
        d3 = ((abs_steps % 1000) // 100) + 0x30
        d2 = ((abs_steps % 100) // 10) + 0x30
        d1 = (abs_steps % 10) + 0x30

        return bytes([self.motor_id + 0x30, ord("M"), direction, d4, d3, d2, d1, 13])


class HardwareAdapter(abc.ABC):
    """Abstract interface for robot hardware communication.

    Subclasses implement the connection and command-sending logic
    for specific hardware backends (MATLAB Engine, Arduino serial, etc.).
    """

    @abc.abstractmethod
    def connect(self, **kwargs) -> bool:
        """Establish connection to the hardware controller.

        Returns:
            True if connection succeeded.
        """

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Cleanly disconnect from the hardware."""

    @abc.abstractmethod
    def send_command(self, command: MotorCommand) -> Optional[str]:
        """Send a motor command and return any response.

        Args:
            command: The motor command to send.

        Returns:
            Response string from the controller, or None.
        """

    @abc.abstractmethod
    def is_connected(self) -> bool:
        """Check if the hardware connection is active."""

    @abc.abstractmethod
    def emergency_stop(self) -> None:
        """Immediately stop all motors."""

    def move_motor(self, motor_id: int, steps: int) -> Optional[str]:
        """Convenience: send a move command."""
        cmd = MotorCommand(motor_id=motor_id, command_type=CommandType.MOVE, steps=steps)
        return self.send_command(cmd)

    def stop_motor(self, motor_id: int) -> Optional[str]:
        """Convenience: stop a specific motor."""
        cmd = MotorCommand(motor_id=motor_id, command_type=CommandType.STOP)
        return self.send_command(cmd)

    def query_position(self, motor_id: int) -> Optional[str]:
        """Convenience: query remaining steps."""
        cmd = MotorCommand(motor_id=motor_id, command_type=CommandType.QUERY_POSITION)
        return self.send_command(cmd)
