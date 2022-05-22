import cv2
import mediapipe as mp
import math
from time import time, sleep
from pynput.keyboard import Key, Controller
import numpy as np

gesture = {
    0: "rock",
    1: "one",
    2: "two",
    3: "two1",
    4: "three",
    5: "three1",
    6: "spider",
}

keyboard = Controller()
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Gesture recognition model
file = np.genfromtxt("assets/gesture_train.csv", delimiter=",")
angle = file[:, :-1].astype(np.float32)
label = file[:, -1].astype(np.float32)
knn = cv2.ml.KNearest_create()
knn.train(angle, cv2.ml.ROW_SAMPLE, label)

cap = cv2.VideoCapture(0)


def angle_0to5(a, b):
    dy = a.y - b.y
    dx = a.x - b.x
    if dx == 0:
        return -90 if dy > 0 else 90

    angle = math.atan(dy / dx) * 180 / math.pi
    if dx < 0.0:
        angle += 180.0
    else:
        if dy < 0.0:
            angle += 360.0
    return (angle + 180) % 360


def gesture(res):
    joint = np.zeros((21, 3))
    for j, lm in enumerate(res.landmark):
        joint[j] = [lm.x, lm.y, lm.z]

    # Compute angles between joints
    v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0, 13, 14, 15, 0, 17, 18, 19], :]  # Parent joint
    v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :]  # Child joint
    v = v2 - v1  # [20,3]
    # Normalize v
    v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

    # Get angle using arcos of dot product
    angle = np.arccos(
        np.einsum(
            "nt,nt->n",
            v[[0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18], :],
            v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :],
        )
    )  # [15,]

    angle = np.degrees(angle)  # Convert radian to degree

    # Inference gesture
    idx = 0
    data = np.array([angle], dtype=np.float32)
    ret, results, neighbours, dist = knn.findNearest(data, 3)
    idx = int(results[0][0])
    return idx


def cval(queue_cam2game, queue_game2cam):

    # ready가 3이되면 슈팅 가능
    ready = 0
    ready_tf = False
    shootingtime = 0
    shooting_s = 0
    max_dist = 0
    max_power = 0
    cnt = 0
    mode_ready = True
    mode_idx = 0
    while cap.isOpened():

        try:  # handGesture 에서 queue를 이용해 값 가져오기
            mode_ready = queue_game2cam.get_nowait()
        except Exception:
            pass

        cnt += 1
        send = {"shoot_power": 0, "shoot_angle": None, "select_mode": 0}

        success, img = cap.read()
        if not success:
            continue
        # img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(cv2.flip(cv2.flip(img, 1), 0), cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        hand_landmark = None
        # 화면에 손이 있어야 실행
        if results.multi_hand_landmarks is not None:
            for hand_landmarks in results.multi_hand_landmarks:
                hand_landmark = hand_landmarks
                d1_to_2 = abs(
                    math.dist(
                        (hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y),
                        (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y),
                    )
                )
                d1_to_2 = d1_to_2 * 1000.0

            if mode_ready:
                idx = gesture(hand_landmark)
                if mode_idx != idx:
                    ready = 0
                    mode_idx = idx
                if mode_idx == idx:
                    ready += 1 / 20
                if ready > 2:
                    send["select_mode"] = mode_idx
                    queue_cam2game.put(send)
                    mode_ready = False
                    print("Let's game")
                if mode_ready:
                    continue

            if cnt % 2 and not ready_tf:
                shoot_angle = angle_0to5(hand_landmark.landmark[0], hand_landmark.landmark[5])
                send["shoot_angle"] = shoot_angle
                # print(shoot_angle, "도")

            # 3초동안 Okay손모양하고 있으면 Ready완료
            if d1_to_2 < 100 and not ready_tf:
                ready += 1 / 20
            else:
                ready = 0
            if ready > 2:
                # d0_to_1 = d0_to_1 * 1000.0
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
                        max_power = (max_dist - start_dist) / max_shooting_s
                        # max_power = max_dist - start_dist

                if time() - shootingtime > 1:
                    send["shoot_power"] = max_power * 3

                    ready_tf = False
                    shootingtime = 0
                    shooting_s = 0
                    max_dist = 0
                    max_power = 0

            queue_cam2game.put(send)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) == ord("q"):
            break
