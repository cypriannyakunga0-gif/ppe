"""Run PPE detection on a single image (no camera / Arduino)."""

import argparse
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from download_model import download_ppe_model
from src.compliance import evaluate_compliance
from src.detector import PPEDetector
from src.main import draw_overlay


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("image", type=Path, help="Path to test image")
  parser.add_argument("-o", "--output", type=Path, default=None, help="Save annotated image")
  args = parser.parse_args()

  download_ppe_model()
  detector = PPEDetector()
  frame = cv2.imread(str(args.image))
  if frame is None:
    raise SystemExit(f"Could not read image: {args.image}")

  persons, ppe = detector.detect(frame)
  status = evaluate_compliance(persons, ppe, frame.shape[:2])
  print(status.message)
  if status.missing:
    print("Missing classes:", status.missing)

  out = draw_overlay(frame, persons, ppe, status)
  out_path = args.output or args.image.with_name(args.image.stem + "_ppe.jpg")
  cv2.imwrite(str(out_path), out)
  print(f"Saved {out_path}")


if __name__ == "__main__":
  main()
