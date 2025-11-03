from termcolor import colored
import numpy as np
import win32gui, win32ui, win32con, win32api   # ← added win32api
import torch
import serial
import time
import keyboard   # you can leave this if you still need it elsewhere
import pathlib
from pathlib import Path
pathlib.PosixPath = pathlib.WindowsPath

fov = 320
mid = fov / 2
height = int((1920 / 2) - mid)
width = int((1080 / 2) - mid)

model = torch.hub.load(
    'v/scripts/yolov5-master',
    'custom',
    path='v/scripts/best640.pt',
    source='local',
    force_reload=True
).cuda()

if torch.cuda.is_available():
    print(colored("CUDA ACCELERATION [ENABLED]", "green"))

ard = serial.Serial("COM5", 9600, writeTimeout=0)

def calculatedistance(x, y):
    code = f"{x:.2f},{y:.2f}*"
    ard.write(str.encode(code))
    time.sleep(0.2)  # match whatever delay you need

def windowcapture():
    hwnd = None
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, fov, fov)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (fov, fov), dcObj, (height, width), win32con.SRCCOPY)
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8').reshape((fov, fov, 4))
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    return img

print('Running!')

while True:
    sct_img = windowcapture()
    results = model(sct_img, size=320)
    df = results.pandas().xyxy[0]

    if not df.empty:
        xmin, ymin, xmax, ymax = df.iloc[0, :4]
        cX = (xmin + xmax) / 2
        cY = (ymin + ymax) / 2
        x = (cX - mid) if cX > mid else -(mid - cX)
        y = (cY - mid) if cY > mid else -(mid - cY)

        # ← Instead of checking Ctrl, we check Left‐Mouse here:
        if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
            calculatedistance(x, y)