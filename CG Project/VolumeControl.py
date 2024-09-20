import cv2
import mediapipe as mp
import time
import HandTrackingModule as htm
import numpy as np
import os

# Initialize hand detector
detector = htm.HandDetector()

# Open the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

cTime = 0
pTime = 0

minVol = 0  # Minimum volume (0%)
maxVol = 100  # Maximum volume (100%)
vol = 0
volBar = 400
volPer = 0

def set_system_volume(vol_per):
    """Set system volume on macOS using osascript."""
    vol_per = int(vol_per)
    os.system(f"osascript -e 'set volume output volume {vol_per}'")

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)
    
    # Find hand and landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
        x2, y2 = lmList[8][1], lmList[8][2]  # Index finger tip
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        
        length = np.hypot(x2 - x1, y2 - y1)
        
        # Convert hand range to volume range
        volPer = np.interp(length, [20, 200], [minVol, maxVol])
        set_system_volume(volPer)
        volBar = np.interp(length, [20, 200], [400, 150])
        
        # Change color if hand is close
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
    
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    
    cv2.imshow("Image", img)
    cv2.waitKey(1)


