# PPE Detection System

Real-time **helmet**, **safety vest**, and **safety boots** monitoring from a laptop webcam, with an **Arduino buzzer** when required PPE is missing.

## Model

Uses [itsadityabaniya/yolov8n-ppe-detection-6classes](https://huggingface.co/itsadityabaniya/yolov8n-ppe-detection-6classes) (YOLOv8n) plus YOLOv8n COCO for person detection.

| Class        | Role              |
|-------------|-------------------|
| `helmet`    | Hard hat          |
| `Vest`      | Safety vest       |
| `safety_shoe` | Safety boots    |

## Hardware

| Part | Notes |
|------|--------|
| Laptop | Runs Python + webcam |
| USB webcam | Default camera (`index 0`) |
| Arduino Uno/Nano | USB serial to laptop |
| Buzzer (2 pins) | See wiring below |

### 2-pin buzzer wiring

Most student kits use a **2-pin buzzer** (not a 3-pin module). Serial can show `OK:ALARM` even when wiring is wrong — fix the physical connection first.

**Step 1 — Identify type (optional):**

| Type | How to tell | What works |
|------|-------------|------------|
| **Passive** | Often says "Passive" or has no label | Needs `tone()` in code (included in sketch) |
| **Active** | Sticker on top or says "Active" | DC voltage; sketch uses `tone()` which usually still works |

**Step 2 — Connect (try this first):**

```
Arduino Pin 8  ----->  Buzzer pin 1  (or + / red / long leg)
Arduino GND    ----->  Buzzer pin 2  (or - / black / short leg)
```

If **no sound**, swap the two buzzer wires.

**Step 3 — Upload sketch and listen**

After upload, you should hear **one short beep** (startup test). No beep = wiring or wrong buzzer type.

**Step 4 — If still silent (louder active buzzer)**

Arduino pin 8 may not supply enough current. Use a small NPN transistor (2N2222 / S8050):

```
5V ---------> buzzer (+)
buzzer (-) --> collector (NPN transistor)
emitter -----> GND
pin 8 --> 1kΩ resistor --> base
```

**3-pin buzzer module (if you have one later):**

```
VCC -> 5V
GND -> GND
SIG -> Pin 8
```

## Setup

### 1. Python environment

```bash
cd ppe
pip install -r requirements.txt
python download_model.py
```

### 2. Arduino

1. Open `arduino/ppe_buzzer/ppe_buzzer.ino` in Arduino IDE.
2. Select your board (Uno/Nano) and COM port.
3. Upload the sketch.

### 3. Configure serial port

Edit `config.py` and set your Arduino port:

```python
ARDUINO_PORT = "COM3"   # Windows — check Device Manager
```

List ports:

```bash
python -m src.main --list-ports
```

## Run

**Live monitoring (webcam + buzzer):**

```bash
python -m src.main --port COM3
```

**Without Arduino (testing):**

```bash
python -m src.main --no-arduino
```

**Single image test:**

```bash
python scripts/test_image.py path/to/photo.jpg
```

Press **Q** in the video window to quit.

## How it works

1. **Person model** (YOLOv8n COCO) finds workers in the frame.
2. **PPE model** detects helmet, vest, and safety shoes.
3. For each person, the system checks whether all three PPE items overlap their body region.
4. If anything is missing for **2 seconds** (`ALARM_DEBOUNCE_SEC`), the laptop sends `ALARM` over serial and the buzzer turns on.
5. When compliant (or no person), it sends `SILENT`.

## Project structure

```
ppe/
├── config.py              # Thresholds, COM port, camera index
├── download_model.py      # Fetch best.pt from Hugging Face
├── requirements.txt
├── models/best.pt         # Downloaded weights
├── src/
│   ├── main.py            # Webcam loop + display
│   ├── detector.py        # YOLO inference
│   ├── compliance.py      # Helmet / vest / boots rules
│   └── arduino_buzzer.py  # Serial buzzer control
├── arduino/ppe_buzzer/    # Arduino sketch
└── scripts/test_image.py  # Offline image test
```

## Tips for best accuracy

- Mount the camera so **feet and head** are visible.
- Use good lighting; avoid strong backlight.
- Boots are the hardest class (~64% mAP) — keep shoes in lower frame.
- Fine-tune on your own site photos if accuracy is low (Roboflow + Ultralytics).

## License

Model weights follow the Hugging Face model card. Use ethically with worker consent.
