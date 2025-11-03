
# **How it works:**
Valorant CV-based aimbot: vision-to-hardware pipeline that captures live screen data, uses a YOLOv5 model for real-time object detection, and sends cursor movement commands to an Arduino Leonardo emulating a USB mouse.

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/76c8ae7f-8bdf-4cdc-a003-ddf5a013032d" />


 # **High-Level Project Pipeline Overview**

Game Feed (Live View)

    ↓
Screen Capture → (OpenCV)

    ↓
Frame Preprocessing (resize, normalize) → (NumPy / OpenCV)

    ↓
Object Detection (enemy boxes + confidences) → (YOLO model via Hugging Face)

    ↓
Postprocessing (NMS + Tracking) → (OpenCV / custom tracker)

    ↓
Target Selection (FOV + confidence rules) → (Python logic)

    ↓
Error Vector Computation (anchor – crosshair) → (NumPy)

    ↓
Motion Planning (smoothing, easing, gradient-descent steps) → (custom Python algorithm)

    ↓
Mouse Command Output → (Serial communication via PySerial)

    ↓
Microcontroller (USB-HID firmware, ran on Arduino Leonardo + USB Host Shield 2.0)

    ↓
Cursor Movement in OS/Game

**Additional modules:**

- Calibration → (in-game settings + OS sensitivity + device DPI)

- Telemetry & Tuning → (Python logging / dashboard)

- GPU Acceleration → (CUDA / Tensor Cores for YOLO inference)


- Safety Controls → (hotkey activation, kill switch, profile presets)

**Further description:**

* The program reads the live game view as a continuous stream of frames, always working with the most recent screen image.
* Each frame is resized and normalized for consistent, fast processing.
* A YOLO-style object detector (open-source on Hugging Face) scans each frame for enemies, outputting bounding boxes with confidence scores.
* Non-maximum suppression (NMS) removes overlapping boxes, keeping only the most confident detection per target.
* A short-term tracker links detections between frames using overlap/IoU and confidence smoothing to reduce flicker.
* From the stabilized detections, a rule selects one “action target” based on proximity to the crosshair, field-of-view cone, and confidence threshold.
* The aim point is set near the upper-center of the target box (approximate head location).
* The difference between the aim point and crosshair yields a screen-space **error vector**, indicating direction and distance for correction (applied using **Gradient Descent**).
* The **motion planner** converts this error into many small, smooth cursor adjustments:

  * Easing to avoid abrupt motion.
  * A dead zone to prevent jitter near the center.
  * Speed and jerk limits to ensure natural acceleration/deceleration.
* The system applies **gradient descent principles** for stable, iterative correction.
* Commands are sent to a **microcontroller board** recognized by the OS as a **USB-HID mouse** via serial connection.
* The **board firmware** translates commands into standard X/Y mouse movement reports.
* **Calibration** aligns OS sensitivity, in-game sensitivity, and device DPI/report rate to maintain consistent pixels-to-counts scaling.
* A **hold-to-activate hotkey** and **instant kill-switch** control system operation; multiple profiles can be saved for different setups.
* The system records **telemetry** such as frame rate, detection time, queue depth, and delay from “target seen” → “cursor moved.”
* **GPU acceleration** (CUDA/Tensor Cores) handles heavy computation like convolutions and matrix operations for low-latency inference.
* Reduced inference time improves responsiveness and smoothness of cursor tracking.
* **Robustness** is tested under conditions like lighting variation, motion blur, occlusion, and color changes to balance precision and recall.
* Overall, the system operates as a **vision-based pipeline** of “see → decide → move,” without reading from or modifying any game memory or files.


# Vision → Arduino HID Demo — Setup Guide
---

## System requirements
- **GPU:** RTX 2060 (min) — RTX 3050 recommended — RTX 4060 for fastest performance  
- **OS:** Windows (screen capture & HID support tested)  
- **Python:** 3.9+ (virtualenv recommended)  
- **CUDA:** 12.1 (if using GPU)

---

## 1) Arduino — prepare HID firmware
1. Install **Arduino IDE 1.8.xx**.  
2. Install **USB Host Shield 2.0** libraries (Library Manager or ZIP).  
3. Open `mouse/mouse.ino` and set mapping to match the byte layout your PC script sends. Example mapping:
   ```cpp
   // byte buffer mapping (adjust indices to match your PC script)
   buttons = buf[0];
   xm      = buf[2];
   ym      = buf[4];
   scr     = buf[6];
(I use Logitech G Pro X superlight, can also try 0, 1, 2, 3 respectively.)

Upload to Arduino Leonardo. Test by sending simple serial packets and verifying cursor moves. Iterate until mapping matches expected behavior.

## 2) Python + YOLOv5 environment

Install Python 3.9+ (virtualenv recommended).
Install CUDA 12.1 and matching PyTorch wheel. Example pip (CUDA 12.1):
```cpp pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 ```

Clone / prepare YOLOv5 copy (your repo path):
```cpp
cd v/scripts
ensure yolov5-master is present
cd yolov5-master
pip install -r requirements.txt
```
Install extras:
```cpppip install pyserial pywin32 keyboard termcolor scipy==1.12.0```

## 3) Configure the Python script

Set serial port to your Arduino: ```cpp
ard = serial.Serial("COM3", 9600, writeTimeout=0)
Replace "COM3" with the port shown in Device Manager. ```

Adjust detection / timing parameters for your hardware:
time.sleep(...) loop interval (lower = faster; tune to GPU + USB throughput)
confidence / NMS thresholds inside YOLO inference

Keep mouse settings neutral on Windows (for consistent mapping) — you can use default sensitivity and test in a local window.
