import pygame
from math import *
from pygame.locals import *


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

########################################################################################
# 그리기 관련
class Screen:  # 스크린을 선언하고 display.set_caption까지 호출함
    def __init__(self, name, width=900, height=600, color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.color = color
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(name)
        self.screen.fill(self.color)


def textprint(window, fontObj, printobj, xcord=400, ycord=30, txtcolor=WHITE, bg=BLACK):
    textSurfaceObj = fontObj.render(str(printobj), True, txtcolor, bg)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (xcord, ycord)
    window.blit(textSurfaceObj, textRectObj)


def all_stones_stop(stones):
    for i in range(10):
        if stones[i].vel:
            return False
    return True


def team_alive(team, stones):
    for i in range(team * 5, team * 5 + 5):
        if stones[i].visible:
            return True
    return False


def print_end(window, win_team, fontObj):
    if win_team == 0:
        bg = WHITE
        txtcolor = BLACK
        txt = "하얀색 돌이 이겼습니다!"
    elif win_team == 1:
        bg = BLACK
        txtcolor = WHITE
        txt = "검은색 돌이 이겼습니다!"
    else:
        bg = YELLOW
        txtcolor = BLUE
        txt = "비겼습니다."

    end_window = pygame.Surface((400, 150))
    end_window.fill(bg)
    textprint(end_window, fontObj, txt, 200, 75, txtcolor=txtcolor, bg=bg)
    window.blit(end_window, (200, 200))
    pygame.display.flip()
    pygame.time.delay(5000)


def arrow(window, arrow_angle, pivot, arrow_img, arrow_offset, dotline_img, dotline_offset):

    rotated_dotline = pygame.transform.rotozoom(dotline_img, -arrow_angle, 1)  # Rotate the image.
    rotated_dotline_offset = dotline_offset.rotate(arrow_angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.

    rect1 = rotated_dotline.get_rect(center=pivot + rotated_dotline_offset)
    window.blit(rotated_dotline, rect1)  # Blit the rotated image.

    rotated_arrow = pygame.transform.rotozoom(arrow_img, -arrow_angle, 1)  # Rotate the image.
    rotated_arrow_offset = arrow_offset.rotate(arrow_angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.

    rect2 = rotated_arrow.get_rect(center=pivot + rotated_arrow_offset)
    window.blit(rotated_arrow, rect2)  # Blit the rotated image.


def new_move(stones, dt=1 / 60):
    for p in stones:
        if not p.visible:
            continue
        p.move(dt)  # 보일 때만 움직임
        for q in stones:
            if p == q or not q.visible:
                continue
            p.collide(q)


# 돌 클래스에서 게임판을 전달받았으므로 draw에서 surface안써줘도됨
def new_draw(window, contents, now_select, turn, is_ready):
    fontObj = pygame.font.Font("assets/DungGeunMo.ttf", 40)
    stones = contents["stones"]
    fn_images = contents["fn_images"]

    window.fill((0, 0, 0))
    window.blit(contents["board_img"], (50, 50))

    arrow(
        window,
        stones[now_select].arrow_angle,
        (stones[now_select].x, stones[now_select].y),
        contents["arrow_img"],
        contents["arrow_offset"],
        contents["dotline_img"],
        contents["dotline_offset"],
    )

    for stone in stones:  # 바둑 돌
        if stone.visible:
            stone.draw()

    txt = "GRAY TURN ↓" if turn else "WHITE TURN ↑"

    select_surface = pygame.Surface((350, 200))
    select_surface.fill(BLACK)
    select_surface.convert_alpha()

    ready_surface = pygame.Surface((350, 250))
    ready_surface.fill(BLACK)
    ready_surface.convert_alpha()

    if not is_ready:
        pygame.draw.rect(select_surface, GREEN, (0, 0, 350, 200), 5)
        textprint(select_surface, fontObj, f"알 선택:   {now_select%5+1}", 150, 40, GREEN)

        textprint(ready_surface, fontObj, "슈팅 모드", 120, 40, (90, 0, 0))

    else:
        pygame.draw.rect(ready_surface, RED, (0, 0, 350, 250), 5)
        textprint(select_surface, fontObj, f"알 선택:   {now_select%5+1}", 150, 40, (0, 90, 0))

        textprint(ready_surface, fontObj, "슈팅 모드", 120, 40, RED)

    for i in range(5):  # 손가락 5개
        if now_select == i + turn * 5:
            pygame.draw.rect(select_surface, GREEN, (10 + i * 65, 95, 70, 70), 3)
        if stones[i + turn * 5].visible:
            select_surface.blit(fn_images[i], (15 + i * 65, 100))

    # ready_surface.blit(contents["okay_img"], (250, 10))  # 오케이
    ready_surface.blit(contents["okay_img"], (30, 100))  # 오케이
    textprint(ready_surface, pygame.font.Font("assets/DungGeunMo.ttf", 20), "튕기면 슛!", 90, 220)
    ready_surface.blit(contents["rock_img"], (200, 100))  # 취소(주먹)
    textprint(ready_surface, pygame.font.Font("assets/DungGeunMo.ttf", 20), "슈팅모드 해제", 260, 220)

    window.blit(contents["back_img"], (0, 0))  # 뒤로가기(권총)
    textprint(window, pygame.font.Font("assets/DungGeunMo.ttf", 20), "시작화면으로", 120, 25)
    textprint(window, fontObj, txt, 775, 60)

    window.blit(select_surface, (600, 100))
    window.blit(ready_surface, (600, 300))

    pygame.display.flip()


def ask_exit(window, queue_cam2game, fontObj):  # 게임중 손가락으로 3 하면 여기 들어옴
    ask_window = pygame.Surface((400, 150))
    ask_window.fill(WHITE)
    textprint(ask_window, fontObj, "시작화면으로 나가시겠습니까?", 200, 50, BLACK, WHITE)
    textprint(ask_window, fontObj, "1. 나가기", 100, 100, BLACK, WHITE)
    textprint(ask_window, fontObj, "2. 계속하기", 250, 100, BLACK, WHITE)
    window.blit(ask_window, (200, 200))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            pass

        try:  # handGesture 에서 queue를 이용해 값 가져오기
            recieve = queue_cam2game.get_nowait()
            if recieve["gesture"] == 1:
                print("exit")
                return True
            if recieve["gesture"] == 2:
                print("return to game")
                return False

        except Exception:
            pass


def select_stone(events, now_select, turn):
    for event in events:  # 키보드 입력을 받는다.
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return -111

            if K_1 <= event.key <= K_5:  # 1,2,3,4,5로 돌 선택
                now_select = (event.key - K_1) + turn * 5

            elif event.key == K_r:  # r로 다음 돌 선택
                return 123

        if event.type == QUIT:
            return -111

    return now_select


def collide(p1, p2):
    elasticity = 1  # 충돌 시 속력 감소

    m1, m2 = 1, 1  # p1, p2의 질량. 일단 상수로 하드코딩해두었음. 추후에 Stone 클래스에 질량 속성을 추가하면 m1,m2 대신 사용.
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    dist = hypot(dx, dy)
    if dist - 3 <= p1.radius + p2.radius:
        p1.bycon = p2.mass
        p2.bycon = p1.mass

        if dx == 0:
            tangent_line_angle = 90 if dy > 0 else -90
        else:
            tangent_line_angle = atan(dy / dx) / pi * 180

        # tangent_line_angle = atan(dy / dx) / pi * 180 if dx else 90

        angle1_transform = p1.angle - tangent_line_angle
        angle2_transform = p2.angle - tangent_line_angle

        vel1_y = p1.vel * sin(radians(angle1_transform))
        vel2_y = p2.vel * sin(radians(angle2_transform))

        vel1_x = p1.vel * cos(radians(angle1_transform))
        vel2_x = p2.vel * cos(radians(angle2_transform))

        vel1_x_new = (1 - (1 + elasticity) * m2 / (m1 + m2)) * vel1_x + (1 + elasticity) * m2 / (m1 + m2) * vel2_x
        vel2_x_new = (1 - (1 + elasticity) * m1 / (m1 + m2)) * vel2_x + (1 + elasticity) * m1 / (m1 + m2) * vel1_x

        p1.vel = hypot(vel1_x_new, vel1_y)
        p2.vel = hypot(vel2_x_new, vel2_y)

        if vel1_x_new == 0:
            print(p1.mass, " angle:", p1.angle, " / ", p2.mass, " angle:", p2.angle, "\n")
            if vel1_y >= 0:
                p1.angle = (90 + tangent_line_angle) % 360
            else:
                p1.angle = (-90 + tangent_line_angle) % 360
        else:
            p1.angle = atan(vel1_y / vel1_x_new) / pi * 180 + tangent_line_angle
            p1.angle %= 360

            if vel1_x_new < 0:
                p1.angle += 180
                p1.angle %= 360
        if vel2_x_new == 0:
            print(p1.mass, " angle:", p1.angle, " / ", p2.mass, " angle:", p2.angle, "\n")
            if vel2_y >= 0:
                p2.angle = (90 + tangent_line_angle) % 360
            else:
                p2.angle = (-90 + tangent_line_angle) % 360
        else:
            p2.angle = atan(vel2_y / vel2_x_new) / pi * 180 + tangent_line_angle
            p2.angle %= 360

            if vel2_x_new < 0:
                p2.angle += 180
                p2.angle %= 360
