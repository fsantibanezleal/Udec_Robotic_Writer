"""Generic serial adapter for direct communication with robot controllers.

This adapter sends raw Scorbot III protocol bytes over a serial port,
compatible with the original Winwedge/DDE protocol used in the MATLAB
implementation. It can also be used with other controllers that accept
the same byte-level protocol.

Supported controllers:
    - Scorbot III (original protocol via RS-232)
    - Any microcontroller implementing the Scorbot byte protocol
    - USB-to-serial adapters connected to legacy hardware
"""

from __future__ import annotations

import logging
from typing import Optional

from .base import HardwareAdapter, MotorCommand, CommandType

logger = logging.getLogger(__name__)


class SerialAdapter(HardwareAdapter):
    """Direct serial port adapter using the Scorbot III byte protocol."""

    DEFAULT_BAUD = 9600
    TIMEOUT_SEC = 2.0

    def __init__(self) -> None:
        self._serial = None
        self._port: str = ""

    def connect(self, **kwargs) -> bool:
        """Open serial connection.

        Keyword Args:
            port: Serial port (e.g., 'COM1', '/dev/ttyS0').
            baud: Baud rate (default: 9600 for Scorbot III).
            timeout: Read timeout in seconds.
        """
        self._port = kwargs.get("port", "COM1")
        baud = kwargs.get("baud", self.DEFAULT_BAUD)
        timeout = kwargs.get("timeout", self.TIMEOUT_SEC)

        try:
            import serial  # type: ignore

            self._serial = serial.Serial(
                port=self._port,
                baudrate=baud,
                timeout=timeout,
            )
            logger.info(f"Serial connected on {self._port} at {baud} baud.")
            return True

        except ImportError:
            logger.error("pyserial not installed. Install with: pip install pyserial")
            return False
        except Exception as e:
            logger.error(f"Serial connection failed: {e}")
            return False

    def disconnect(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def send_command(self, command: MotorCommand) -> Optional[str]:
        """Send raw Scorbot III protocol bytes."""
        if not self.is_connected():
            logger.error("Serial not connected.")
            return None

        try:
            data = command.to_scorbot_bytes()
            self._serial.write(data)
            self._serial.flush()

            response = self._serial.readline().decode("ascii", errors="replace").strip()
            return response if response else "OK"

        except Exception as e:
            logger.error(f"Serial command failed: {e}")
            return None

    def emergency_stop(self) -> None:
        """Stop all motors (send stop to motors 1-5)."""
        if self.is_connected():
            for motor_id in range(1, 6):
                cmd = MotorCommand(motor_id=motor_id, command_type=CommandType.STOP)
                self.send_command(cmd)
