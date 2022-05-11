import cv2
import mediapipe as mp
import time
 
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_Draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
 
while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    #print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_Draw.draw_landmarks(img,handLms,mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Image",img)
    cv2.waitKey(1)

