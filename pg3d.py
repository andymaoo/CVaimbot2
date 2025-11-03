import time
import serial
import numpy as np
import mss

# ——— CONFIG ———
SERIAL_PORT  = "COM5"
BAUDRATE     = 115200
TOLERANCE    = 40               # color tolerance per channel
TARGET_BGR   = (0, 0, 255)      # BGR for pure red
BOX_SIZE     = 10               # half-width of square around center
CLICK_DELAY  = 0.05             # after click, pause (sec)
LOOP_DELAY   = 0.01             # between checks (sec)
# ————————

# open serial
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)
time.sleep(2)  # let Arduino reset

with mss.mss() as sct:
    # compute center-box coords
    monitor = sct.monitors[1]  # primary
    cx = monitor["width"]  // 2
    cy = monitor["height"] // 2
    region = {
      "left":   cx - BOX_SIZE,
      "top":    cy - BOX_SIZE,
      "width":  BOX_SIZE * 2,
      "height": BOX_SIZE * 2
    }

    while True:
        img = sct.grab(region)
        arr = np.array(img)[:, :, :3]  # BGRA→BGR

        # check if any pixel is within TOL of TARGET_BGR
        diffs = np.abs(arr - TARGET_BGR)
        mask  = np.all(diffs <= TOLERANCE, axis=2)
        if mask.any():
            ser.write(b'c')
            time.sleep(CLICK_DELAY)

        time.sleep(LOOP_DELAY)
