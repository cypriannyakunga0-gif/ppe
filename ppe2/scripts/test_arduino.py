"""Quick serial test — run this before the main app to verify Arduino link."""

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import serial
from serial.tools import list_ports

from config import ARDUINO_BAUD, ARDUINO_PORT


def main():
    parser = argparse.ArgumentParser(description="Test Arduino buzzer over serial")
    parser.add_argument("--port", default=ARDUINO_PORT, help="Serial port, e.g. COM7")
    parser.add_argument("--list-ports", action="store_true", help="List ports and exit")
    args = parser.parse_args()

    if args.list_ports:
        for p in list_ports.comports():
            print(f"  {p.device}  {p.description}")
        return

    port = args.port
    print(f"Opening {port} at {ARDUINO_BAUD} baud...")
    try:
        ser = serial.Serial(port, ARDUINO_BAUD, timeout=2)
    except serial.SerialException as exc:
        print(f"FAILED: {exc}")
        if "access is denied" in str(exc).lower():
            print("\nClose Arduino Serial Monitor and any other app using this port.")
        sys.exit(1)

    time.sleep(2)
    ser.reset_input_buffer()

    for cmd in (b"ALARM\n", b"SILENT\n"):
        label = cmd.decode().strip()
        print(f"Sending {label}...")
        ser.write(cmd)
        time.sleep(0.5)
        if ser.in_waiting:
            print("  Arduino:", ser.readline().decode(errors="replace").strip())

    ser.close()
    print("Done — if you heard a short beep, wiring and sketch are OK.")


if __name__ == "__main__":
    main()
