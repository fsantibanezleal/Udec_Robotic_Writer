"""Arduino adapter for controlling stepper/servo motors via serial.

This adapter communicates with an Arduino board running a compatible
firmware that accepts motor commands over serial (USB). It supports
controlling multiple stepper motors and a servo-based gripper.

Arduino Firmware Protocol:
    Commands are sent as ASCII strings terminated by newline:
        M<motor_id><direction><steps>\\n   - Move motor
        S<motor_id>\\n                      - Stop motor
        H\\n                                - Home all motors
        Q<motor_id>\\n                      - Query position
        G<aperture>\\n                      - Set gripper aperture (0-180 for servo)
        E\\n                                - Emergency stop all

    Responses:
        OK\\n                               - Command acknowledged
        POS:<motor_id>:<steps>\\n           - Position response
        ERR:<message>\\n                    - Error

Example Arduino firmware is provided in docs/arduino_firmware.md
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from .base import HardwareAdapter, MotorCommand, CommandType

logger = logging.getLogger(__name__)


class ArduinoAdapter(HardwareAdapter):
    """Hardware adapter for Arduino-based motor control via serial port.

    Supports stepper motors (via A4988/DRV8825 drivers) and servo gripper.
    """

    DEFAULT_BAUD = 115200
    TIMEOUT_SEC = 2.0

    def __init__(self) -> None:
        self._serial = None
        self._port: str = ""
        self._baud: int = self.DEFAULT_BAUD

    def connect(self, **kwargs) -> bool:
        """Open serial connection to Arduino.

        Keyword Args:
            port: Serial port name (e.g., 'COM3', '/dev/ttyUSB0').
            baud: Baud rate (default: 115200).
            timeout: Read timeout in seconds (default: 2.0).

        Returns:
            True if connection succeeded.
        """
        self._port = kwargs.get("port", "COM3")
        self._baud = kwargs.get("baud", self.DEFAULT_BAUD)
        timeout = kwargs.get("timeout", self.TIMEOUT_SEC)

        try:
            import serial  # type: ignore

            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baud,
                timeout=timeout,
            )
            # Wait for Arduino to reset after serial connection
            time.sleep(2.0)
            # Flush any startup messages
            self._serial.reset_input_buffer()

            logger.info(f"Arduino connected on {self._port} at {self._baud} baud.")
            return True

        except ImportError:
            logger.error("pyserial not installed. Install with: pip install pyserial")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Arduino on {self._port}: {e}")
            return False

    def disconnect(self) -> None:
        """Close the serial connection."""
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        logger.info("Arduino disconnected.")

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def send_command(self, command: MotorCommand) -> Optional[str]:
        """Send a command to the Arduino over serial.

        Translates MotorCommand to the ASCII protocol and reads the response.
        """
        if not self.is_connected():
            logger.error("Arduino not connected.")
            return None

        try:
            cmd_str = self._encode_command(command)
            if cmd_str is None:
                return None

            self._serial.write(cmd_str.encode("ascii"))
            self._serial.flush()

            # Read response
            response = self._serial.readline().decode("ascii").strip()
            logger.debug(f"Arduino TX: {cmd_str.strip()} -> RX: {response}")
            return response

        except Exception as e:
            logger.error(f"Arduino command failed: {e}")
            return None

    def _encode_command(self, command: MotorCommand) -> Optional[str]:
        """Convert MotorCommand to Arduino ASCII protocol string."""
        if command.command_type == CommandType.MOVE:
            direction = "+" if command.steps >= 0 else "-"
            return f"M{command.motor_id}{direction}{abs(command.steps)}\n"

        elif command.command_type == CommandType.STOP:
            return f"S{command.motor_id}\n"

        elif command.command_type == CommandType.HOME:
            return "H\n"

        elif command.command_type == CommandType.QUERY_POSITION:
            return f"Q{command.motor_id}\n"

        elif command.command_type == CommandType.GRIPPER_OPEN:
            return f"G{command.steps}\n"

        elif command.command_type == CommandType.GRIPPER_CLOSE:
            return "G0\n"

        else:
            logger.warning(f"Unsupported command type for Arduino: {command.command_type}")
            return None

    def emergency_stop(self) -> None:
        """Send emergency stop to all motors."""
        if self.is_connected():
            try:
                self._serial.write(b"E\n")
                self._serial.flush()
            except Exception as e:
                logger.error(f"Emergency stop failed: {e}")

    @staticmethod
    def list_ports() -> list[str]:
        """List available serial ports."""
        try:
            import serial.tools.list_ports  # type: ignore
            return [p.device for p in serial.tools.list_ports.comports()]
        except ImportError:
            return []
