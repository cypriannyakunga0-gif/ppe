"""YOLO inference wrappers for person + PPE models."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from ultralytics import YOLO

from config import PERSON_CONF, PERSON_MODEL, PPE_CONF, PPE_MODEL_PATH
from src.compliance import Detection


class PPEDetector:
    def __init__(self, ppe_weights: Path | None = None) -> None:
        weights = ppe_weights or PPE_MODEL_PATH
        if not Path(weights).exists():
            raise FileNotFoundError(
                f"PPE model not found at {weights}. Run: python download_model.py"
            )
        self.ppe_model = YOLO(str(weights))
        self.person_model = YOLO(PERSON_MODEL if Path(PERSON_MODEL).exists() else "yolov8n.pt")

    def detect(self, frame: np.ndarray) -> tuple[list[Detection], list[Detection]]:
        persons = self._run_person(frame)
        ppe_items = self._run_ppe(frame)
        return persons, ppe_items

    def _run_person(self, frame: np.ndarray) -> list[Detection]:
        results = self.person_model.predict(
            frame,
            conf=PERSON_CONF,
            classes=[0],
            verbose=False,
        )
        return _parse_results(results, person_only=True)

    def _run_ppe(self, frame: np.ndarray) -> list[Detection]:
        results = self.ppe_model.predict(frame, conf=PPE_CONF, verbose=False)
        return _parse_results(results, person_only=False)


def _parse_results(results, person_only: bool) -> list[Detection]:
    detections: list[Detection] = []
    if not results or results[0].boxes is None:
        return detections

    names = results[0].names
    for box in results[0].boxes:
        cls_id = int(box.cls.item())
        class_name = names[cls_id]
        if person_only and class_name != "person":
            continue
        xyxy = tuple(float(v) for v in box.xyxy[0].tolist())
        detections.append(
            Detection(
                class_name=class_name,
                confidence=float(box.conf.item()),
                xyxy=xyxy,
            )
        )
    return detections
