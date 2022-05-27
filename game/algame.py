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
BLUE = (0, 0, 255)

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# Movement substeps at the given timestep
# movement_substeps = 1
# Target FPS
FPS = 60.0
# dt (should be 1.0/FPS for realtime, but you can change it to speed up or slow down time)
# dt = 1.0 / FPS


def init_window():
    global stones, window, contents, prev_select
    """icon = pygame.Surface((1, 1))
    icon.set_alpha(0)
    pygame.display.set_icon(icon)
    pygame.display.set_caption("OOP_LIGHTBULB")"""

    # 화면 생성
    # screen = Screen("lightbulb", 1000, 600, (0, 0, 0))
    window = Screen("lightbulb", SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0)).screen  # 게임화면

    pygame.init()
    fontObj = pygame.font.Font("assets/DungGeunMo.ttf", 25)

    # team 0
    stones = [Stone(start_x=i * 78 + 244, start_y=144, mass=i, team=0, surface=window) for i in range(5)]
    # team 1
    stones += [Stone(start_x=i * 78 + 244, start_y=457, mass=i + 5, team=1, surface=window) for i in range(5)]
    prev_select = [0, 5]

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

    # 배경화면
    bg_img1 = pygame.image.load("assets/bg5.png")
    bg_img1 = pygame.transform.scale(bg_img1, (SCREEN_WIDTH, SCREEN_HEIGHT))
    window.blit(bg_img1, (0, 0))

    # 배경음악
    """pygame.mixer.music.load("assets/intro.mp3")
    pygame.mixer.music.play(-1)"""

    contents = {
        "stones": stones,
        "board_img": board_img,
        "arrow_img": arrow_img,
        "dotline_img": dotline_img,
        "arrow_offset": arrow_offset,
        "dotline_offset": dotline_offset,
        "fontObj": fontObj,
    }


def gesture_handler(queue_cam2game, queue_game2cam):
    global newturn, turn_changed
    try:  # handGesture 에서 queue를 이용해 값 가져오기
        recieve = queue_cam2game.get_nowait()

        # 각도가 있을 경우 (0도도 포함)
        if recieve["shoot_angle"] != None:
            stones[now_select].arrow_angle = recieve["shoot_angle"]

        if recieve["gesture"] in (1, 2, 3, 4, 5, 7):  # 7은 jax손
            if recieve["gesture"] == 7:
                recieve["gesture"] = 3
            now_select = recieve["gesture"] - 1 + turn * 5

        newturn = turn
        # 발사(손튕기기)한 경우
        if recieve["shoot_power"]:
            stones[now_select].angle = stones[now_select].arrow_angle
            stones[now_select].vel = recieve["shoot_power"]
            turn_changed = True
            newturn = 1 - turn

        if recieve["gesture"] == 6:  # 권총 손가락 --> 뒤로가기
            if ask_exit(window, queue_cam2game, contents["fontObj"]):
                game_main(queue_cam2game, queue_game2cam)

    except Exception:
        pass


def start_screen(queue_cam2game):

    menu = pygame.Surface((400, 300))
    menu.fill(WHITE)
    menu = menu.convert_alpha()
    fontObj = contents["fontObj"]
    pygame.draw.rect(menu, BLUE, (0, 0, 400, 100))
    textprint(menu, pygame.font.Font("assets/DungGeunMo.ttf", 40), "OpenCV 알까기", 200, 50, bg=BLUE)
    textprint(menu, fontObj, "1. Single Play", 200, 150, BLACK, WHITE)
    textprint(menu, fontObj, "2. Multi Play", 200, 200, BLACK, WHITE)
    textprint(menu, fontObj, "3. Exit", 200, 250, BLACK, WHITE)
    window.blit(menu, (300, 150))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            pass

        try:  # handGesture 에서 queue를 이용해 값 가져오기
            recieve = queue_cam2game.get_nowait()
            if recieve["gesture"] == 1:
                return 1
            if recieve["gesture"] == 2:
                return 2
            if recieve["gesture"] == 3:
                print("Exit blocked")
                """waiting = False
                pygame.quit()
                sys.exit()"""
        except Exception:
            pass


def single_game(queue_cam2game, queue_game2cam):
    global turn
    turn = 0
    turn_changed = False
    now_select = 0  # 현재 선택된 돌의 번호
    window.blit(contents["board_img"], (150, 50))  # 바둑판 위치
    clock = pygame.time.Clock()
    while True:
        if turn == 1:  # player
            try:  # handGesture 에서 queue를 이용해 값 가져오기
                recieve = queue_cam2game.get_nowait()

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

                if recieve["gesture"]:
                    print(recieve["gesture"])
                if recieve["gesture"] in (1, 2, 3, 4, 5, 7):  # 7은 jax손
                    if recieve["gesture"] == 7:
                        recieve["gesture"] = 3
                    now_select = recieve["gesture"]-1 + turn * 5

                if recieve["gesture"] == 6:  # 권총 손가락 --> 뒤로가기
                    if ask_exit(window, queue_cam2game, contents["fontObj"]):
                        game_main(queue_cam2game, queue_game2cam)

            except Exception:
                pass

            events = pygame.event.get()
            """now_select = select_stone(events, now_select, turn)  # 돌 결정
            if now_select == -111:  # 종료
                break
            elif now_select == 123:
                game_main(queue_cam2game, queue_game2cam)"""

            if stones[now_select].is_dead():
                now_select += 1
                if now_select == 5 or now_select == 10:
                    now_select -= 5

            prev_select[turn] = now_select

        elif stones[prev_select[1]].vel < 10:  # ai
            com_stone = random.randint(0, 4)
            while stones[com_stone].is_dead():
                com_stone = com_stone - 4 if target == 4 else com_stone + 1
            target = random.randint(5, 9)
            while stones[target].is_dead():
                target = target - 4 if target == 9 else target + 1

            stones[com_stone].angle = stones[com_stone].arrow_angle = (
                angle_0to5(stones[target], stones[com_stone]) + 180
            ) % 360
            print(stones[com_stone].angle)
            stones[com_stone].vel = random.randint(500, 1200)
            newturn = 1 - turn
            turn_changed = True
            prev_select[turn] = com_stone

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
            game_main(queue_cam2game, queue_game2cam)

        clock.tick(FPS)


def multi_game(queue_cam2game, queue_game2cam):
    turn = 0
    turn_changed = False
    now_select = 0  # 현재 선택된 돌의 번호
    window.blit(contents["board_img"], (150, 50))  # 바둑판 위치
    clock = pygame.time.Clock()
    while True:
        try:  # handGesture 에서 queue를 이용해 값 가져오기
            recieve = queue_cam2game.get_nowait()
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

            if recieve["gesture"] in (1, 2, 3, 4, 5, 7):  # 7은 jax손
                if recieve["gesture"] == 7:
                    recieve["gesture"] = 3
                now_select = recieve["gesture"]-1 + turn * 5

            if recieve["gesture"] == 6:  # 권총 손가락
                if ask_exit(window, queue_cam2game, contents["fontObj"]):
                    game_main(queue_cam2game, queue_game2cam)
        except Exception:
            pass

        events = pygame.event.get()
        """now_select = select_stone(events, now_select, turn)  # 돌 결정
        if now_select == -111:  # 종료
            break
        elif now_select == 123:
            game_main(queue_cam2game, queue_game2cam)"""

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
            game_main(queue_cam2game, queue_game2cam)

        clock.tick(FPS)


def game_main(queue_cam2game, queue_game2cam):
    """turn = 0
    turn_changed = False
    now_select = 0  # 현재 선택된 돌의 번호"""

    init_window()
    queue_game2cam.put(True)
    mode = start_screen(queue_cam2game)
    queue_game2cam.put(False)
    """pygame.mixer.music.load("assets/stage.mp3")
    pygame.mixer.music.play(-1)"""
    if mode == 1:
        single_game(queue_cam2game, queue_game2cam)
    elif mode == 2:
        multi_game(queue_cam2game, queue_game2cam)

    pygame.display.update()
    pygame.quit()
    sys.exit()
