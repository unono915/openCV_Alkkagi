import threading
from handGesture import cval
from game import game_main


if __name__ == "__main__":
    # cap = cv2.VideoCapture(0)
    cv_thread = threading.Thread(target=cval)
    cv_thread.start()
    game_main()

    # game_thread = threading.Thread(target=game_main)
    # game_thread.start()
