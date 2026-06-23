"""Project configuration — edit COM port and thresholds here."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
PPE_MODEL_PATH = MODELS_DIR / "best.pt"

# Hugging Face model (helmet, vest, safety_shoe + extras)
HF_MODEL_ID = "itsadityabaniya/yolov8n-ppe-detection-6classes"
HF_MODEL_FILE = "best.pt"

# COCO person detector (auto-downloaded by Ultralytics on first run)
PERSON_MODEL = str(MODELS_DIR / "yolov8n.pt")

# PPE classes required for compliance (must match model label names)
REQUIRED_PPE = {"helmet", "Vest", "safety_shoe"}

# Detection confidence thresholds (global minimum sent to YOLO)
PPE_CONF = 0.40
PERSON_CONF = 0.50

# Stricter per-class thresholds after detection (reduces false positives)
PPE_CLASS_CONF = {
    "helmet": 0.62,       # raise if hoods still count as helmets
    "Vest": 0.50,
    "safety_shoe": 0.45,
}

# Spatial rules: PPE must sit on the correct body zone (fraction of person box height)
HELMET_MAX_HEAD_HEIGHT = 0.35   # helmet box height <= 35% of person height
HELMET_MAX_HEAD_WIDTH = 0.90    # helmet box width <= 90% of person width
HELMET_HEAD_ZONE = 0.42         # helmet center in top 42% of person
VEST_TORSO_ZONE = (0.18, 0.72)  # vest center between 18%–72% from top
BOOTS_FOOT_ZONE = 0.62          # boots center in bottom 38% (below 62% from top)

# Buzz only after violations persist this many seconds (reduces flicker)
ALARM_DEBOUNCE_SEC = 2.0

# Serial link to Arduino — set your port, e.g. "COM3" on Windows, "/dev/ttyUSB0" on Linux
ARDUINO_PORT = "COM7"
ARDUINO_BAUD = 9600

# Webcam index (0 = default camera)
CAMERA_INDEX = 0

# Display window size hint (actual size follows camera)
DISPLAY_WIDTH = 960
