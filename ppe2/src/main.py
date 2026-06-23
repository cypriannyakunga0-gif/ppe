"""Live webcam PPE monitoring with Arduino buzzer."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from config import ALARM_DEBOUNCE_SEC, CAMERA_INDEX, DISPLAY_WIDTH, REQUIRED_PPE
from download_model import download_ppe_model
from src.arduino_buzzer import ArduinoBuzzer, list_serial_ports
from src.compliance import ComplianceResult, Detection, evaluate_compliance, is_valid_ppe_on_person
from src.detector import PPEDetector

COLOR_OK = (0, 200, 0)
COLOR_BAD = (0, 0, 255)
COLOR_PERSON = (255, 180, 0)
COLOR_PPE = (0, 255, 255)


def draw_overlay(
    frame: np.ndarray,
    persons,
    ppe_items,
    status: ComplianceResult,
) -> np.ndarray:
    out = frame.copy()
    for p in persons:
        _draw_box(out, p.xyxy, f"person {p.confidence:.2f}", COLOR_PERSON)
    for item in ppe_items:
        if item.class_name not in REQUIRED_PPE:
            continue
        valid = any(is_valid_ppe_on_person(item, p) for p in persons) if persons else False
        color = COLOR_PPE if valid else (128, 128, 128)
        tag = "ok" if valid else "ignored"
        _draw_box(out, item.xyxy, f"{item.class_name} {item.confidence:.2f} ({tag})", color)

    banner_color = COLOR_OK if status.compliant or not status.person_detected else COLOR_BAD
    label = status.message if status.message else "Monitoring"
    cv2.rectangle(out, (0, 0), (out.shape[1], 42), banner_color, -1)
    cv2.putText(out, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
    return out


def _draw_box(img, xyxy, label, color):
    x1, y1, x2, y2 = map(int, xyxy)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.putText(img, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def run(camera_index: int, port: str | None, no_arduino: bool) -> None:
    download_ppe_model()
    detector = PPEDetector()
    buzzer = ArduinoBuzzer(port=port)

    if not no_arduino:
        if not buzzer.connect():
            ports = list_serial_ports()
            print("Available serial ports:", ports or "(none)")
            print("Continuing without Arduino — buzzer commands will print to console.")
    else:
        print("Arduino disabled (--no-arduino). Buzzer state prints to console.")

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {camera_index}")

    violation_since: float | None = None
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            persons, ppe_items = detector.detect(frame)
            status = evaluate_compliance(persons, ppe_items, frame.shape[:2])
            display = draw_overlay(frame, persons, ppe_items, status)

            if status.person_detected and not status.compliant:
                if violation_since is None:
                    violation_since = time.time()
                elapsed = time.time() - violation_since
                if elapsed >= ALARM_DEBOUNCE_SEC:
                    buzzer.set_alarm(True)
            else:
                violation_since = None
                buzzer.set_alarm(False)

            h, w = display.shape[:2]
            if w > DISPLAY_WIDTH:
                scale = DISPLAY_WIDTH / w
                display = cv2.resize(display, (DISPLAY_WIDTH, int(h * scale)))

            cv2.imshow("PPE Monitor", display)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        buzzer.close()
        cap.release()
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="PPE detection with Arduino buzzer")
    parser.add_argument("--camera", type=int, default=CAMERA_INDEX, help="Webcam index")
    parser.add_argument("--port", type=str, default=None, help="Arduino serial port, e.g. COM3")
    parser.add_argument("--no-arduino", action="store_true", help="Skip serial; log buzzer state")
    parser.add_argument("--list-ports", action="store_true", help="List serial ports and exit")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.list_ports:
        print("Serial ports:", list_serial_ports())
        sys.exit(0)
    run(args.camera, args.port, args.no_arduino)
