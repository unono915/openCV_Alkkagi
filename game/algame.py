from time import sleep
import pygame
import sys
import random
from Stone import Stone
from game_features import *
from handGesture import angle_0to5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Movement substeps at the given timestep
# movement_substeps = 1
# Target FPS
FPS = 60.0
# dt (should be 1.0/FPS for realtime, but you can change it to speed up or slow down time)
# dt = 1.0 / FPS


def init_window():
    global stones, window, contents, prev_select
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

    # 화살표
    arrow_img = pygame.image.load("assets/arrow6.png").convert_alpha()
    arrow_img = pygame.transform.scale(arrow_img, (60, 15))
    arrow_offset = pygame.math.Vector2(arrow_img.get_width() // 2, 0)  # 벡터

    # 점선
    dotline_img = pygame.image.load("assets/dotline.png").convert_alpha()
    # print(dotline_img.get_size())
    dotline_img = pygame.transform.scale(dotline_img, (650, 160))
    dotline_offset = pygame.math.Vector2(dotline_img.get_width() // 2, 0)  # 벡터

    contents = {
        "stones": stones,
        "board_img": board_img,
        "arrow_img": arrow_img,
        "dotline_img": dotline_img,
        "arrow_offset": arrow_offset,
        "dotline_offset": dotline_offset,
        "fontObj": fontObj,
    }


def start_screen():
    fontObj = contents["fontObj"]
    textprint(window, fontObj, "1. Single Play", 400, 300)
    textprint(window, fontObj, "2. Multi Play", 400, 350)
    textprint(window, fontObj, "3. Exit", 400, 400)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1
                elif event.key == pygame.K_2:
                    return 2
                elif event.key == pygame.K_3:
                    waiting = False
                    pygame.quit()
                    sys.exit()


def single_game(queue):
    turn = 0
    turn_changed = False
    now_select = 0  # 현재 선택된 돌의 번호
    window.blit(contents["board_img"], (150, 50))  # 바둑판 위치
    clock = pygame.time.Clock()
    while True:
        if turn == 0:
            sleep(2)
            me = random.randint(0, 4)
            while stones[me].is_dead():
                me = me - 4 if target == 4 else me + 1
            target = random.randint(5, 9)
            while stones[target].is_dead():
                target = target - 4 if target == 9 else target + 1

            stones[target].angle = stones[target].arrow_angle = angle_0to5(stones[me], stones[target])
            stones[target].vel = random.random() * 1000
            turn = 1 - turn
            continue

        else:
            try:  # handGesture 에서 queue를 이용해 값 가져오기
                recieve = queue.get_nowait()
            except Exception:
                recieve = {"shoot_power": 0, "shoot_angle": None}

            # 각도가 있을 경우 (0도도 포함)
            if recieve["shoot_angle"] != None:
                stones[now_select].arrow_angle = recieve["shoot_angle"]

            newturn = turn
            # 발사(손튕기기)한 경우
            if recieve["shoot_power"]:
                stones[now_select].angle = stones[now_select].arrow_angle
                stones[now_select].vel = recieve["shoot_power"]
                turn_changed = True
                newturn = 1 - turn

            events = pygame.event.get()
            now_select = select_stone(events, now_select, turn)  # 돌 결정
            if now_select == -111:  # 종료
                break
            elif now_select == 123:
                game_main(queue)

            if stones[now_select].is_dead():
                now_select += 1
                if now_select == 5 or now_select == 10:
                    now_select -= 5

            prev_select[turn] = now_select

        # 움직임
        new_move(stones)
        new_draw(window, contents, now_select, turn)

        if turn_changed:
            print("turn_changed")
            now_select = prev_select[newturn]
            turn = newturn
            turn_changed = False

        game_result = score_text(stones, now_select)
        if game_result == "GRAY WIN" or game_result == "WHITE WIN":
            print_end(window, game_result)  # 개임오버 메세지
            break

        clock.tick(FPS)


def multi_game(queue):
    turn = 0
    turn_changed = False
    now_select = 0  # 현재 선택된 돌의 번호
    window.blit(contents["board_img"], (150, 50))  # 바둑판 위치
    clock = pygame.time.Clock()
    while True:

        try:  # handGesture 에서 queue를 이용해 값 가져오기
            recieve = queue.get_nowait()
        except Exception:
            recieve = {"shoot_power": 0, "shoot_angle": None}

        # 각도가 있을 경우 (0도도 포함)
        if recieve["shoot_angle"] != None:
            stones[now_select].arrow_angle = recieve["shoot_angle"]

        newturn = turn
        # 발사(손튕기기)한 경우
        if recieve["shoot_power"]:
            stones[now_select].angle = stones[now_select].arrow_angle
            stones[now_select].vel = recieve["shoot_power"]
            turn_changed = True
            newturn = 1 - turn

        events = pygame.event.get()
        now_select = select_stone(events, now_select, turn)  # 돌 결정
        if now_select == -111:  # 종료
            break
        elif now_select == 123:
            game_main(queue)

        if stones[now_select].is_dead():
            now_select += 1
            if now_select == 5 or now_select == 10:
                now_select -= 5

        prev_select[turn] = now_select

        # 움직임
        new_move(stones)
        new_draw(window, contents, now_select, turn)

        if turn_changed:
            print("turn_changed")
            now_select = prev_select[newturn]
            turn = newturn
            turn_changed = False

        game_result = score_text(stones, now_select)
        if game_result == "GRAY WIN" or game_result == "WHITE WIN":
            print_end(window, game_result)  # 개임오버 메세지
            break

        clock.tick(FPS)


def game_main(queue):
    """turn = 0
    turn_changed = False
    now_select = 0  # 현재 선택된 돌의 번호"""
    init_window()
    mode = start_screen()
    if mode == 1:
        single_game(queue)
    elif mode == 2:
        multi_game(queue)

    pygame.display.update()
    pygame.quit()
    sys.exit()
