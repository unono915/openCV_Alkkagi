import cv2
import mediapipe as mp
import math
from time import time, sleep
import numpy as np

gesture = {
    0: "okay",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "back",
    7: "jacks",
    8: "circle",
}

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
    gesture_wait = 0
    wait_1to2 = 0
    wait_1to3 = 0
    okay_2or3 = 0
    ready_tf = False
    shootingtime = 0
    shooting_s = 0
    max_dist = 0
    max_power = 0
    cnt = 0
    mode_idx = 0
    angle_send = True

    while cap.isOpened():
        try:  # handGesture 에서 queue를 이용해 값 가져오기
            init_page = queue_game2cam.get_nowait()
        except Exception:
            pass
        cnt += 1
        send = {"shoot_power": 0, "shoot_angle": None, "gesture": None, "select_Al": None, "ready": False}

        success, img = cap.read()
        if not success:
            continue
        # img = cv2.cvtColor(cv2.flip(img, 1), cv2.COLOR_BGR2RGB)
        img = cv2.cvtColor(cv2.flip(cv2.flip(img, 1), 0), cv2.COLOR_BGR2RGB)
        results = hands.process(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # 화면에 손이 있어야 실행
        if results.multi_hand_landmarks is not None:
            for hand_landmarks in results.multi_hand_landmarks:
                d1_to_2 = abs(
                    math.dist(
                        (hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y),
                        (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y),
                    )
                )
                d1_to_3 = abs(
                    math.dist(
                        (hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y),
                        (hand_landmarks.landmark[12].x, hand_landmarks.landmark[12].y),
                    )
                )

                d1_to_2 = d1_to_2 * 1000.0
                d1_to_3 = d1_to_3 * 1000.0
                idx = gesture(hand_landmarks)
                if mode_idx != idx:
                    gesture_wait = 0
                    mode_idx = idx
                if mode_idx == idx and idx != 0:
                    gesture_wait += 1
                if gesture_wait == 20:
                    send["gesture"] = mode_idx
                    print("gesture send")
                    # queue_cam2game.put(send)
                    # print("Let's game")

                if cnt % 2 and angle_send:
                    shoot_angle = angle_0to5(hand_landmarks.landmark[0], hand_landmarks.landmark[5])
                    send["shoot_angle"] = shoot_angle
                    # print(shoot_angle, "도")

                # 2초동안 Okay손모양하고 있으면 Ready완료
                if d1_to_2 < 100 and not ready_tf:
                    wait_1to2 += 1 / 10
                else:
                    wait_1to2 = 0
                if wait_1to2 > 2:
                    start_dist = d1_to_2
                    ready_tf = True
                    okay_2or3 = 2
                    print("쏘세요!")

                if d1_to_3 < 100 and not ready_tf:
                    wait_1to3 += 1 / 10
                else:
                    wait_1to3 = 0
                if wait_1to3 > 2:
                    start_dist = d1_to_3
                    ready_tf = True
                    okay_2or3 = 3
                    print("쏘세요!")

                send["ready"] = ready_tf
                # print(ready_tf)

                # 1초안에 슈팅
                if ready_tf:
                    if okay_2or3 == 2:
                        check_dist = d1_to_2
                    elif okay_2or3 == 3:
                        check_dist = d1_to_3
                    #print(check_dist)
                    if shootingtime == 0:
                        shootingtime = time()
                    if check_dist > 100:
                        angle_send = False
                        shooting_s += 1
                    if check_dist > max_dist:
                        max_dist = check_dist
                        max_shooting_s = shooting_s
                        if max_shooting_s != 0:
                            # max_power = (max_dist - start_dist) / max_shooting_s
                            max_power = max_dist - start_dist

                    if time() - shootingtime > 1:
                        send["shoot_power"] = max_power * 3
                        ready_tf = False
                        shootingtime = 0
                        shooting_s = 0
                        max_dist = 0
                        max_power = 0
                        okay_2or3 = 0
                        angle_send = True

                queue_cam2game.put(send)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) == ord("q"):
            break
