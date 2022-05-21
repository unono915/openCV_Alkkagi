import cv2
import mediapipe as mp
import math
from time import time, sleep
from pynput.keyboard import Key, Controller

keyboard = Controller()
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
cap = cv2.VideoCapture(0)


def angle_0to5(a, b):
    dy = a.y - b.y
    dx = a.x - b.x
    if dx != 0:
        angle = math.atan(dy / dx) * 180 / math.pi
    if dx < 0.0:
        angle += 180.0
    else:
        if dy < 0.0:
            angle += 360.0
    return (angle + 180) % 360


def cval(queue):
    # ready가 3이되면 슈팅 가능
    ready = 0
    ready_tf = False
    shootingtime = 0
    shooting_s = 0
    max_dist = 0
    max_power = 0
    cnt = 0
    while cap.isOpened():
        cnt += 1
        send = {"shoot_power": 0, "shoot_angle": None}

        success, img = cap.read()
        if not success:
            continue
        # img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(cv2.flip(cv2.flip(img, 1), 0), cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # 화면에 손이 있어야 실행
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                d1_to_2 = abs(
                    math.dist(
                        (hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y),
                        (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y),
                    )
                )
                d1_to_2 = d1_to_2 * 1000.0

                if cnt%2:
                    shoot_angle = angle_0to5(hand_landmarks.landmark[0], hand_landmarks.landmark[5])
                    send["shoot_angle"] = shoot_angle
                    # print(shoot_angle, "도")

            # 3초동안 Okay손모양하고 있으면 Ready완료
            if d1_to_2 < 100 and not ready_tf:
                ready += 1 / 20
            else:
                ready = 0
            if ready > 2:
                d0_to_1 = d0_to_1 * 1000.0
                start_dist = d1_to_2
                ready_tf = True
                print("Start")

            # 2초안에 슈팅
            if ready_tf:
                if shootingtime == 0:
                    shootingtime = time()
                if d1_to_2 > 100:
                    shooting_s += 1
                if d1_to_2 > max_dist:
                    max_dist = d1_to_2
                    max_shooting_s = shooting_s
                    if max_shooting_s != 0:
                        max_power = (max_dist-start_dist)/max_shooting_s
                        #max_power = max_dist - start_dist

                if time() - shootingtime > 1:
                    send["shoot_power"] = max_power * 3

                    ready_tf = False
                    shootingtime = 0
                    shooting_s = 0
                    max_dist = 0
                    max_power = 0

            queue.put(send)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) == ord("q"):
            break
