import cv2
import mediapipe as mp
 
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
 
cap = cv2.VideoCapture(0)
 
with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
 
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
 
        results = hands.process(image)
 
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
 
        #즉, 업지손가락 끝은 landmark[4]에, 검지 손가락 끝은 landmark[8]에 좌표값이 반환되는데,
        # 좌표값은 image상의 x,y위치값을 0.0~1.0 사이의 값으로 표시한다. 즉 image 좌측 최상단은 x=0.0 y=0.0  우측최하단은 x=1.0, y=1.0이 된다.
        # 따라서int(hand_landmarks.landmark[4].x * 100)은 엄지손가락 끝의 x좌표를 100분율로 표시한 것이 된다. 
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger1 = int(hand_landmarks.landmark[4].x * 100 )
                finger2 = int(hand_landmarks.landmark[8].x * 100 )
                dist = abs(finger1 - finger2)
                cv2.putText(
                    image, text='f1=%d f2=%d dist=%d ' % (finger1,finger2,dist), org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
                    color=255, thickness=3)
 
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
 
        cv2.imshow('image', image)
        if cv2.waitKey(1) == ord('q'):
            break
 
cap.release()