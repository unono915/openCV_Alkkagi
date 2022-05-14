import cv2
from cvzone.HandTrackingModule import HandDetector

########################
wCam, hCam = 4*300,3*300
########################

cap = cv2.VideoCapture(0)
# 원본 동영상 크기 정보
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("원본 동영상 너비(가로) : {}, 높이(세로) : {}".format(w, h))

# 동영상 크기 변환
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720) # 가로
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 520) # 세로

# 변환된 동영상 크기 정보
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("변환된 동영상 너비(가로) : {}, 높이(세로) : {}".format(w, h))
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)
print("초당 프레임수 : {}".format(cv2.CAP_PROP_FPS))

detector = HandDetector(maxHands=1, detectionCon=0.8)

# Hand - dict - lmList - bbox - center - type
cnt = 0
while cap.isOpened():
    cnt+=1
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands = detector.findHands(img, draw=False)  # No Draw
    lmList = 0
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]  # List of 21 Landmarks points
        bbox = hand["bbox"]
        print(bbox)
    cv2.rectangle(img, (50, 350), (600, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, "finalText", (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
    cv2.imshow("Image", img)
    cv2.waitKey(1)