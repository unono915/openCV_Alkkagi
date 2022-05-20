import cv2
import mediapipe as mp
import math

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

def dist(x1,y1,x2,y2):
    return math.sqrt(math.pow(x1-x2,2)) +  math.sqrt(math.pow(y1-y2,2))

compareIndex = [[18,4],[6,8],[10,12],[14,16],[18,20]]
open = [False,False,False,False,False]
gesture = [[True,True,True,True,True,"Hi!"],
            [False,True,True,False,False,"Yeah!"],
            [True,True,False,False,True,"SpiderMan!"],
            [True,True,True,False,False,"3"],
            [True,True,True,True,False,"4"]]

while cap.isOpened():
    success, img = cap.read()
    if not success:
        continue
    h,w,c = img.shape
    imageRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)

    image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(0,5):
                open[i] = dist(hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y, hand_landmarks.landmark[compareIndex[i][0]].x, hand_landmarks.landmark[compareIndex[i][0]].y) < dist(hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y,hand_landmarks.landmark[compareIndex[i][1]].x, hand_landmarks.landmark[compareIndex[i][1]].y)
            print(open)
            text_x = (hand_landmarks.landmark[0].x*w)
            text_y = (hand_landmarks.landmark[0].y*h)
            for i in range(0,5):
                flag = True
                for j in range(0,5):
                    if(gesture[i][j] != open[j]):
                        flag = False
                if(flag == True):
                    cv2.putText(img,gesture[i][5],(round(text_x)-50,round(text_y)-250),cv2.FONT_HERSHEY_COMPLEX,4,(0,0,0),4)
                mpDraw.draw_landmarks(img,hand_landmarks,mpHands.HAND_CONNECTIONS)

    cv2.imshow("123",img)
    cv2.waitKey(1)