from wsgiref.util import shift_path_info
import cv2
from cvzone.HandTrackingModule import HandDetector
import mediapipe as mp
import math
from time import sleep,time
from pynput.keyboard import Key, Controller

keyboard = Controller()

########################
wCam, hCam = 480, 480
########################

cap = cv2.VideoCapture(1)

# 동영상 크기 변환
cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam) # 가로
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam) # 세로
fps = cv2.CAP_PROP_FPS
print("초당 프레임수 : {}".format(fps))
detector = HandDetector(maxHands=1, detectionCon=0.8)

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#ready가 3이되면 슈팅 가능
ready = 0
ready_tf = False
shootingtime = 0
shooting_s = 0
max_dist = 0
max_power = 0

#초당 20번 실행
with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8) as hands:

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            continue
        img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        #화면에 손이 있어야 실행
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                d1_to_2 = abs(math.dist((hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y), (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y)))
                d1_to_2 = (d1_to_2*1000.0)
                
                d0_to_1 = abs(math.dist((hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y), (hand_landmarks.landmark[1].x, hand_landmarks.landmark[1].y)))
                d0_to_1 = (d0_to_1*1000.0)
                
                #print("%d, %d, %d" % (d1_to_2, d0_to_1, d1_to_2/d0_to_1))
            
            # 3초동안 Okay손모양하고 있으면 Ready완료
            if d1_to_2 < 100 and not ready_tf:
                ready += 1/20
            else: 
                ready = 0
            if ready > 3:
                start_dist = d1_to_2
                ready_tf = True
                print("Start")
            
            #2초안에 슈팅
            if ready_tf:
                if shootingtime == 0:
                    shootingtime = time()
                #print("%d, %d, %d" % (d1_to_2, d0_to_1, d1_to_2/d0_to_1))
                if d1_to_2 > 100:
                    shooting_s += 1
                if d1_to_2 > max_dist:
                    max_dist = d1_to_2
                    max_shooting_s = shooting_s
                    if max_shooting_s != 0:
                        #max_power = (max_dist-start_dist)/max_shooting_s
                        max_power = (max_dist-start_dist)

                if time() - shootingtime > 2:
                    print(max_power)
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)
                    # max_power -> vel으로 전달해야함
                    ready_tf = False
                    shootingtime = 0
                    shooting_s = 0
                    max_dist = 0
                    max_power = 0


        # cv2.rectangle(img, (50, 350), (600, 450), (175, 0, 175), cv2.FILLED)
        # cv2.putText(img, "finalText", (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) == ord('q'):
            break