"""MATLAB Engine adapter for controlling the robot via MATLAB.

This adapter uses the MATLAB Engine API for Python to bridge commands
from the Python application to MATLAB, enabling integration with
existing MATLAB-based robot control toolboxes or direct serial
communication through MATLAB.

Requirements:
    - MATLAB installed with the Engine API for Python
    - pip install matlabengine (matching your MATLAB version)

Usage:
    adapter = MatlabAdapter()
    adapter.connect(matlab_path="/path/to/matlab")
    adapter.send_command(MotorCommand(motor_id=1, command_type=CommandType.MOVE, steps=100))
"""

from __future__ import annotations

import logging
from typing import Optional

from .base import HardwareAdapter, MotorCommand, CommandType

logger = logging.getLogger(__name__)


class MatlabAdapter(HardwareAdapter):
    """Hardware adapter that communicates via MATLAB Engine.

    Sends motor commands by calling MATLAB functions that handle
    the serial communication with the robot controller (Winwedge/DDE).
    """

    def __init__(self) -> None:
        self._engine = None
        self._connected = False

    def connect(self, **kwargs) -> bool:
        """Start a MATLAB engine session.

        Keyword Args:
            matlab_path: Optional path to MATLAB installation.
            shared_session: If True, connect to an existing shared session.

        Returns:
            True if MATLAB engine started successfully.
        """
        try:
            import matlab.engine  # type: ignore

            shared = kwargs.get("shared_session", False)
            if shared:
                sessions = matlab.engine.find_matlab()
                if sessions:
                    self._engine = matlab.engine.connect_matlab(sessions[0])
                else:
                    self._engine = matlab.engine.start_matlab()
            else:
                self._engine = matlab.engine.start_matlab()

            self._connected = True
            logger.info("MATLAB engine connected successfully.")
            return True

        except ImportError:
            logger.error(
                "matlab.engine not available. Install with: "
                "pip install matlabengine (requires MATLAB installation)"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to start MATLAB engine: {e}")
            return False

    def disconnect(self) -> None:
        """Quit the MATLAB engine."""
        if self._engine is not None:
            try:
                self._engine.quit()
            except Exception:
                pass
            self._engine = None
        self._connected = False
        logger.info("MATLAB engine disconnected.")

    def is_connected(self) -> bool:
        return self._connected and self._engine is not None

    def send_command(self, command: MotorCommand) -> Optional[str]:
        """Send a command via MATLAB function calls.

        Maps MotorCommand to the equivalent MATLAB function call
        from the original Scorbot III control scripts.
        """
        if not self.is_connected():
            logger.error("MATLAB engine not connected.")
            return None

        try:
            if command.command_type == CommandType.MOVE:
                # Call MATLAB function: Motormove(motor_id, steps, direction)
                direction = "+" if command.steps >= 0 else "-"
                result = self._engine.eval(
                    f"Motormove({command.motor_id}, {abs(command.steps)}, '{direction}')",
                    nargout=0,
                )
                return f"MOVE motor {command.motor_id}: {command.steps} steps"

            elif command.command_type == CommandType.STOP:
                self._engine.eval(
                    f"DetenerMotor({command.motor_id})", nargout=0
                )
                return f"STOP motor {command.motor_id}"

            elif command.command_type == CommandType.QUERY_POSITION:
                result = self._engine.eval(
                    f"CuentasRemanentes({command.motor_id})", nargout=1
                )
                return str(result)

            elif command.command_type == CommandType.QUERY_SWITCH:
                result = self._engine.eval(
                    f"EstadoSwitch({command.motor_id})", nargout=1
                )
                return str(result)

            elif command.command_type == CommandType.HOME:
                self._engine.eval("Hogar()", nargout=0)
                return "HOME sequence executed"

            else:
                logger.warning(f"Unsupported command type: {command.command_type}")
                return None

        except Exception as e:
            logger.error(f"MATLAB command failed: {e}")
            return None

    def emergency_stop(self) -> None:
        """Stop all motors via MATLAB Stop function."""
        if self.is_connected():
            try:
                self._engine.eval("Stop()", nargout=0)
            except Exception as e:
                logger.error(f"Emergency stop failed: {e}")

    def run_matlab_script(self, script: str) -> Optional[str]:
        """Execute arbitrary MATLAB code (for advanced users).

        Args:
            script: MATLAB code string to evaluate.

        Returns:
            Result as string, or None on failure.
        """
        if not self.is_connected():
            return None
        try:
            result = self._engine.eval(script, nargout=1)
            return str(result)
        except Exception as e:
            logger.error(f"MATLAB script failed: {e}")
            return None
