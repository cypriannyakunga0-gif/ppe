"""Serial interface to Arduino buzzer controller."""

from __future__ import annotations

import time

import serial
from serial.tools import list_ports

from config import ARDUINO_BAUD, ARDUINO_PORT


class ArduinoBuzzer:
    def __init__(self, port: str | None = None, baud: int = ARDUINO_BAUD) -> None:
        self.port = port or ARDUINO_PORT
        self.baud = baud
        self._serial: serial.Serial | None = None
        self._alarm_on = False

    def connect(self) -> bool:
        try:
            self._serial = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)
            self._serial.reset_input_buffer()
            self.silent()
            return True
        except serial.SerialException as exc:
            err = str(exc).lower()
            print(f"[Arduino] Could not open {self.port}: {exc}")
            if "access is denied" in err or "permissionerror" in err:
                print(
                    "[Arduino] COM port is locked by another program. Try:\n"
                    "  1. Close Arduino IDE Serial Monitor (most common cause)\n"
                    "  2. Close any other python -m src.main window\n"
                    "  3. Unplug USB, wait 3s, plug back in\n"
                    "  4. Run: python scripts/test_arduino.py --port COM7"
                )
            self._serial = None
            return False

    @property
    def connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def set_alarm(self, active: bool) -> None:
        if active == self._alarm_on:
            return
        self._alarm_on = active
        cmd = b"ALARM\n" if active else b"SILENT\n"
        if self.connected:
            self._serial.write(cmd)
        else:
            state = "ON" if active else "OFF"
            print(f"[Arduino] Simulated buzzer {state} (not connected)")

    def silent(self) -> None:
        self.set_alarm(False)

    def close(self) -> None:
        if self.connected:
            self.silent()
            self._serial.close()
            self._serial = None


def list_serial_ports() -> list[str]:
    return [p.device for p in list_ports.comports()]
