import threading
from queue import Queue
from algame import game_main
from handGesture import cval


queue = Queue()

if __name__ == "__main__":
    cv_thread = threading.Thread(target=cval, args=(queue,))
    cv_thread.start()
    game_main(queue)

    # game_thread = threading.Thread(target=game_main)
    # game_thread.start()
