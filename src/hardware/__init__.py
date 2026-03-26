"""Hardware abstraction layer for connecting to real robot controllers."""

from .base import HardwareAdapter, MotorCommand, CommandType
from .matlab_adapter import MatlabAdapter
from .arduino_adapter import ArduinoAdapter
from .serial_adapter import SerialAdapter

__all__ = [
    "HardwareAdapter",
    "MotorCommand",
    "CommandType",
    "MatlabAdapter",
    "ArduinoAdapter",
    "SerialAdapter",
]
