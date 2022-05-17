import pygame
from math import *
from pygame.locals import *


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Screen:  # 스크린을 선언하고 display.set_caption까지 호출함
    def __init__(self, name, width=900, height=600, color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.color = color
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(name)
        self.screen.fill(self.color)


def textprint(window, fontObj, printobj, xcord=400, ycord=30):
    textSurfaceObj = fontObj.render(str(printobj), True, WHITE, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (xcord, ycord)
    window.blit(textSurfaceObj, textRectObj)


def score(stones, now_select):
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
        return "White : " + str(scored[0]) + " vs Gray :" + str(scored[1]) + "\n" + "Selection :" + str(now_select + 1)


def arrow(window, surface, arrow_angle, pivot, offset):

    rotated_image = pygame.transform.rotozoom(surface, -arrow_angle, 1)  # Rotate the image.
    rotated_offset = offset.rotate(arrow_angle)  # Rotate the offset vector.
    # Add the offset vector to the center/pivot point to shift the rect.

    rect = rotated_image.get_rect(center=pivot + rotated_offset)
    window.blit(rotated_image, rect)  # Blit the rotated image.
    pygame.draw.circle(window, (30, 250, 70), pivot, 3)  # Pivot point.


def new_move(stones, dt=1 / 60):
    for p in stones:
        if p.visible:
            p.move(dt)  # 보일 때만 움직임
        for q in stones:
            if p == q:
                continue
            collide(p, q)


# 돌 클래스에서 게임판을 전달받았으므로 draw에서 surface안써줘도됨
def new_draw(window, stones, now_select, board_img, arrow_img, fontObj, turn, offset):
    window.fill((0, 0, 0))
    window.blit(board_img, (150, 50))

    arrow(window, arrow_img, stones[now_select].arrow_angle, (stones[now_select].x, stones[now_select].y), offset)
    for stone in stones:  # 바둑 돌
        if stone.visible:
            stone.draw()
    textprint(window, fontObj, score(stones, now_select))
    if turn == 0:
        textprint(window, fontObj, "WHITE TURN", 800, 400)
    else:
        textprint(window, fontObj, "GRAY TURN", 800, 400)

    for stone in stones:
        if stone.mass == 0:
            textprint(window, fontObj, "------- WHITE -------", 800, 100)
        if stone.mass == 5:
            textprint(window, fontObj, "-------  GRAY -------", 800, 230)
        if not stone.visible:
            textprint(
                window, fontObj, "%d 은 죽었습니다." % (stone.mass + 1), 800, 120 + stone.mass * 20 + (stone.mass // 5) * 30
            )
        else:
            textprint(
                window, fontObj, "%d 은 살아있습니다." % (stone.mass + 1), 800, 120 + stone.mass * 20 + (stone.mass // 5) * 30
            )

    pygame.display.flip()


def stoneshooting(stone, selectstone, turn):
    plus_vel = 250  # 한번의 클릭으로 더해지는 속도
    # plus_ang = -10  # 한번의 클릭으로 생겨나는 각도
    now_select = selectstone
    # stone = STONE

    for event in pygame.event.get():  # 키보드 입력을 받는다.
        if event.type == QUIT:
            return -111, -111, turn
        if event.type == KEYDOWN:
            # ESC 누르면 종료
            if event.key == K_ESCAPE:
                return -111, -111, turn

            # 돌 선택
            if K_1 <= event.key <= K_5:  # 1,2,3,4,5로 돌 선택
                now_select = (event.key - K_1) + turn * 5

            elif event.key == K_r:  # r로 다음 돌 선택
                now_select += 1
                now_select %= 5
                now_select += turn * 5

            elif event.key == K_UP:  # 세기 증가
                if stone.hidvel < 1000:
                    stone.hidvel += plus_vel

            elif event.key == K_DOWN:  # 세기 감소
                if stone.hidvel > 0:
                    stone.hidvel -= plus_vel

            # 스페이스바를 입력받았을 때 진행하고 있는 상태라면 설정한 속도를 저장한 후 돌의 속도와 각도를 다시 0으로 초기화한다.
            elif event.key == K_SPACE:
                stone.angle = stone.arrow_angle
                a = stone.hidvel
                stone.hidvel = 0
                stone.bycon = -1
                turn = 1 - turn
                return a, now_select, turn

    return 0, now_select, turn


def collide(p1, p2):
    elasticity = 1  # 충돌 시 속력 감소

    m1, m2 = 1, 1  # p1, p2의 질량. 일단 상수로 하드코딩해두었음. 추후에 Stone 클래스에 질량 속성을 추가하면 m1,m2 대신 사용.
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    dist = hypot(dx, dy)
    if dist + 1 <= p1.radius + p2.radius:
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

        """if vel1_x_new == 0 and vel2_x_new == 0:
            print(p1.mass, p1.vel, p2.mass, p2.vel)
            p1.divide(p2)
            return"""

        if vel1_x_new == 0:
            print(p1.mass, " angle:", p1.angle, " / ", p2.mass, " angle:", p2.angle, "\n")
            if vel1_y >= 0:
                p1.angle = 90 + tangent_line_angle
            else:
                p1.angle = -90 + tangent_line_angle
        else:
            p1.angle = atan(vel1_y / vel1_x_new) / pi * 180 + tangent_line_angle
            if vel1_x_new < 0:
                p1.angle += 180
        if vel2_x_new == 0:
            print(p1.mass, " angle:", p1.angle, " / ", p2.mass, " angle:", p2.angle, "\n")
            if vel2_y >= 0:
                p2.angle = 90 + tangent_line_angle
            else:
                p2.angle = -90 + tangent_line_angle
        else:
            p2.angle = atan(vel2_y / vel2_x_new) / pi * 180 + tangent_line_angle
            if vel2_x_new < 0:
                p2.angle += 180

        # 복잡한 충돌은 이 게임에서 불가능하다.
