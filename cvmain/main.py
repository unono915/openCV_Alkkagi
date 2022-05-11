import cv2
from cvzone.HandTrackingModule import HandDetector

########################
wCam, hCam = 640, 480
########################

cap = cv2.VideoCapture(1)
cap.set(3, wCam)
cap.set(4, hCam)

detector = HandDetector(maxHands=1, detectionCon=0.8)

# Hand - dict - lmList - bbox - center - type
while True:
    success, img = cap.read()
    hands = detector.findHands(img, draw=False)  # No Draw
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]  # List of 21 Landmarks points
        bbox = hand["bbox"]
        print(lmList[8])
    cv2.imshow("Image", img)
    cv2.waitKey(1)