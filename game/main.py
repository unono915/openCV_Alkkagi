import threading
from queue import Queue
from algame import game_main
from handGesture import cval


queue_cam2game = Queue(1)
queue_game2cam = Queue(1)

if __name__ == "__main__":
    cv_thread = threading.Thread(target=cval, args=(queue_cam2game, queue_game2cam))
    cv_thread.start()
    game_main(queue_cam2game, queue_game2cam)

    # game_thread = threading.Thread(target=game_main)
    # game_thread.start()
