import pygame
import sys

# cam
import threading
from handGesture import cval

# game
from Stone import Stone
from game_features import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# Movement substeps at the given timestep
movement_substeps = 1
# Target FPS
FPS = 60.0
# dt (should be 1.0/FPS for realtime, but you can change it to speed up or slow down time)
dt = 1.0 / FPS
turn = 0
turn_changed = False
num_of_stone = 10  # 돌의 개수
now_select = 0  # 현재 선택된 돌의 번호


icon = pygame.Surface((1, 1))
icon.set_alpha(0)
pygame.display.set_icon(icon)
pygame.display.set_caption("OOP_LIGHTBULB")
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.init()

fontObj = pygame.font.Font("assets/NanumSquareRoundB.ttf", 16)

# team 0
stones = [Stone(start_x=i * 78 + 244, start_y=144, mass=i, team=0, surface=surface) for i in range(5)]
# team 1
stones += [Stone(start_x=i * 78 + 244, start_y=457, mass=i + 5, team=1, surface=surface) for i in range(5)]
prev_select = [0, 5]

# 화면 생성
# screen = Screen("lightbulb", 1000, 600, (0, 0, 0))
window = Screen("lightbulb", 1000, 600, (0, 0, 0)).screen  # 게임화면

# 바둑판
board_img = pygame.image.load("assets/board.png").convert()
board_img = pygame.transform.scale(board_img, (500, 500))
window.blit(board_img, (150, 50))  # 바둑판 위치

# 화살표
arrow_img = pygame.image.load("assets/arrow6.png").convert_alpha()
arrow_img = pygame.transform.scale(arrow_img, (60, 15))
offset = pygame.math.Vector2(arrow_img.get_width() // 2, 0)  # 벡터

contents = {
    "stones": stones,
    "board_img": board_img,
    "arrow_img": arrow_img,
    "offset": offset,
    "fontObj": fontObj,
}


if __name__ == "__main__":
    # cap = cv2.VideoCapture(0)
    t = threading.Thread(target=cval)
    t.start()

    clock = pygame.time.Clock()
    while True:

        set_angle(stones, now_select)  # 각도 결정
        events = pygame.event.get()
        now_select = select_stone(events, now_select, turn)  # 돌 결정
        if now_select == -111:  # 종료
            break
        vel, newturn = shoot(events, stones[now_select], turn)  # 슛
        turn_changed = turn != newturn

        if stones[now_select].is_dead():
            now_select += 1
            if now_select == 5 or now_select == 10:
                now_select -= 5

        prev_select[turn] = now_select
        turn = newturn
        stones[now_select].vel += vel

        # 움직임

        new_move(stones)
        new_draw(window, contents, now_select, turn)

        if turn_changed:
            now_select = prev_select[newturn]
            turn_changed = False

        game_result = score_text(stones, now_select)
        if game_result == "GRAY WIN" or game_result == "WHITE WIN":
            print_end(window, game_result)  # 개임오버 메세지
            break

        clock.tick(FPS)

    pygame.display.update()
    pygame.quit()
    sys.exit()
