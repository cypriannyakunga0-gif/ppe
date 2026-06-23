"""Map detections to compliance rules (helmet, vest, safety boots)."""

from dataclasses import dataclass, field

from config import (
    BOOTS_FOOT_ZONE,
    HELMET_HEAD_ZONE,
    HELMET_MAX_HEAD_HEIGHT,
    HELMET_MAX_HEAD_WIDTH,
    PPE_CLASS_CONF,
    REQUIRED_PPE,
    VEST_TORSO_ZONE,
)


@dataclass
class Detection:
    class_name: str
    confidence: float
    xyxy: tuple[float, float, float, float]


@dataclass
class ComplianceResult:
    person_detected: bool
    compliant: bool
    missing: set[str] = field(default_factory=set)
    message: str = ""


def _center(box: tuple[float, float, float, float]) -> tuple[float, float]:
    x1, y1, x2, y2 = box
    return (x1 + x2) / 2, (y1 + y2) / 2


def _box_size(box: tuple[float, float, float, float]) -> tuple[float, float]:
    x1, y1, x2, y2 = box
    return x2 - x1, y2 - y1


def _person_zone(person: tuple[float, float, float, float], top: float, bottom: float) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = person
    h = y2 - y1
    return x1, y1 + top * h, x2, y1 + bottom * h


def _center_in_zone(center: tuple[float, float], zone: tuple[float, float, float, float]) -> bool:
    cx, cy = center
    zx1, zy1, zx2, zy2 = zone
    return zx1 <= cx <= zx2 and zy1 <= cy <= zy2


def is_valid_ppe_on_person(item: Detection, person: Detection) -> bool:
    """Reject low-confidence or misplaced detections (e.g. hood counted as helmet)."""
    min_conf = PPE_CLASS_CONF.get(item.class_name, 0.5)
    if item.confidence < min_conf:
        return False

    pbox = person.xyxy
    ibox = item.xyxy
    icx, icy = _center(ibox)
    pw, ph = _box_size(pbox)
    iw, ih = _box_size(ibox)

    if item.class_name == "helmet":
        head_zone = _person_zone(pbox, 0.0, HELMET_HEAD_ZONE)
        if not _center_in_zone((icx, icy), head_zone):
            return False
        if ih > ph * HELMET_MAX_HEAD_HEIGHT:
            return False
        if iw > pw * HELMET_MAX_HEAD_WIDTH:
            return False
        return True

    if item.class_name == "Vest":
        torso = _person_zone(pbox, VEST_TORSO_ZONE[0], VEST_TORSO_ZONE[1])
        return _center_in_zone((icx, icy), torso)

    if item.class_name == "safety_shoe":
        foot_zone = _person_zone(pbox, BOOTS_FOOT_ZONE, 1.0)
        return _center_in_zone((icx, icy), foot_zone)

    return item.class_name in REQUIRED_PPE


def evaluate_compliance(
    persons: list[Detection],
    ppe_items: list[Detection],
    frame_shape: tuple[int, int],
) -> ComplianceResult:
    """
    For each detected person, check helmet / vest / boots with spatial + confidence filters.
    Buzz when any person is missing required PPE.
    """
    if not persons:
        return ComplianceResult(
            person_detected=False,
            compliant=True,
            message="No person in frame",
        )

    worst_missing: set[str] = set()
    any_violation = False

    for person in persons:
        worn: set[str] = set()

        for item in ppe_items:
            if item.class_name not in REQUIRED_PPE:
                continue
            if not is_valid_ppe_on_person(item, person):
                continue
            worn.add(item.class_name)

        missing = REQUIRED_PPE - worn
        if missing:
            any_violation = True
            worst_missing |= missing

    if any_violation:
        labels = ", ".join(sorted(_friendly_name(c) for c in worst_missing))
        return ComplianceResult(
            person_detected=True,
            compliant=False,
            missing=worst_missing,
            message=f"Missing: {labels}",
        )

    return ComplianceResult(
        person_detected=True,
        compliant=True,
        message="All required PPE detected",
    )


def _friendly_name(class_name: str) -> str:
    return {
        "helmet": "helmet",
        "Vest": "safety vest",
        "safety_shoe": "safety boots",
    }.get(class_name, class_name)
