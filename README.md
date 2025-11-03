**High-Level Project Pipeline Overview**

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
