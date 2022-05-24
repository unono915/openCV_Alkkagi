import pygame
from math import *
from pygame.locals import *


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

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


def print_end(window, game_result):
    # 게임 오버 메시지
    game_font = pygame.font.Font(None, 40)
    msg = game_font.render(game_result, True, YELLOW)  # 노란색
    msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    window.blit(msg, msg_rect)
    pygame.time.delay(2000)


def score_text(stones, now_select):
    scored = dict()
    for stone in stones:
        scored.setdefault(stone.team, 0)
        sum = stone.visible
        scored[stone.team] = scored[stone.team] + sum

    if scored[0] == 0:
        return "GRAY WIN"
    elif scored[1] == 0:
        return "WHITE WIN"
    else:
        return "White : " + str(scored[0]) + " vs Gray : " + str(scored[1]) + " " + "Selection :" + str(now_select + 1)


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
        if p.visible:
            p.move(dt)  # 보일 때만 움직임
        for q in stones:
            if p == q:
                continue
            collide(p, q)


# 돌 클래스에서 게임판을 전달받았으므로 draw에서 surface안써줘도됨
def new_draw(window, contents, now_select, turn):
    fontObj = contents["fontObj"]
    stones = contents["stones"]

    window.fill((0, 0, 0))
    window.blit(contents["board_img"], (150, 50))

    arrow(
        window,
        stones[now_select].arrow_angle,
        (stones[now_select].x, stones[now_select].y),
        contents["arrow_img"],
        contents["arrow_offset"],
        contents["dotline_img"],
        contents["dotline_offset"],
    )
    # arrow(window, arrow_img, stones[now_select].arrow_angle, (stones[now_select].x, stones[now_select].y), offset)
    for stone in stones:  # 바둑 돌
        if stone.visible:
            stone.draw()
    textprint(window, fontObj, score_text(stones, now_select))
    if turn == 0:
        textprint(window, fontObj, "WHITE TURN", 800, 500)
    else:
        textprint(window, fontObj, "GRAY TURN", 800, 500)

    for stone in stones:
        if stone.mass == 0:
            textprint(
                window, fontObj, "------- WHITE -------", 800, 120 + stone.mass * 30 + (stone.mass // 5) * 30 - 30
            )
        if stone.mass == 5:
            textprint(
                window, fontObj, "-------  GRAY -------", 800, 120 + stone.mass * 30 + (stone.mass // 5) * 30 - 30
            )
        if not stone.visible:
            textprint(
                window, fontObj, "%d 은 죽었습니다." % (stone.mass + 1), 800, 120 + stone.mass * 30 + (stone.mass // 5) * 30
            )
        else:
            textprint(
                window, fontObj, "%d 은 살아있습니다." % (stone.mass + 1), 800, 120 + stone.mass * 30 + (stone.mass // 5) * 30
            )

    pygame.display.flip()


def ask_exit(window, queue_cam2game, fontObj):  # 게임중 손가락으로 3 하면 여기 들어옴
    ask_window = pygame.Surface((400, 150))
    ask_window.fill(WHITE)
    textprint(ask_window, fontObj, "시작화면으로 나가시겠습니까?", 200, 50, BLACK, WHITE)
    textprint(ask_window, fontObj, "1. 나가기", 100, 100, BLACK, WHITE)
    textprint(ask_window, fontObj, "2. 계속하기", 250, 100, BLACK, WHITE)
    window.blit(ask_window, (300, 250))
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
            # print(p1.mass, " angle:", p1.angle, " / ", p2.mass, " angle:", p2.angle, "\n")
            if vel1_y >= 0:
                p1.angle = 90 + tangent_line_angle
            else:
                p1.angle = -90 + tangent_line_angle
        else:
            p1.angle = atan(vel1_y / vel1_x_new) / pi * 180 + tangent_line_angle
            if vel1_x_new < 0:
                p1.angle += 180
        if vel2_x_new == 0:
            # print(p1.mass, " angle:", p1.angle, " / ", p2.mass, " angle:", p2.angle, "\n")
            if vel2_y >= 0:
                p2.angle = 90 + tangent_line_angle
            else:
                p2.angle = -90 + tangent_line_angle
        else:
            p2.angle = atan(vel2_y / vel2_x_new) / pi * 180 + tangent_line_angle
            if vel2_x_new < 0:
                p2.angle += 180
