import pygame
from math import *

elasticity = 1  # 충돌 시 속력 감소


class Stone:  # 처음 돌을 놓는 위치와 레벨을 전달받고, 반지름 질량은 기본값을 설정
    # x, y, radius
    def __init__(self, start_x=10, start_y=10, radius=10, mass=1, surface=None, team=None, visible=1, bycon=-1):
        self.radius = radius
        self.x = start_x
        self.y = start_y
        self.mass = mass

        self.color = (128, 128, 128) if team else (255, 255, 255)

        self.isalive = True
        self.angle = 0
        self.vel = 0
        self.surface = surface
        self.team = team
        self.hidvel = 0
        self.hidang = 0
        self.visible = visible
        self.bycon = bycon

    def move(self, dt):  # 전달받은 시간 간격에 속력을 곱해 돌의 위치를 이동시킨다. 속력은 0.95배로 계속 줄어든다.
        self.x += dt * self.vel * cos(radians(self.angle))
        self.y += dt * self.vel * sin(radians(self.angle))

        if self.x > 650 or self.y > 550 or self.x < 150 or self.y < 50:
            self.visible = 0
            print("%d died by out of range" % (self.mass + 1))

        """if self.x > 650:
            self.angle = 180 - self.angle
            self.vel += 1
        if self.y > 550:
            self.visible = 0
            print("%d died by out of range" % (self.mass + 1))
        if self.x < 150:
            self.angle = 180 - self.angle
            self.vel += 1
        if self.y < 50:
            self.visible = 0
            print("%d died by out of range" % (self.mass + 1))"""

        self.vel *= 0.95  # 속도의 감소
        if abs(self.vel) < 0.1: # TODO 정지하도록하는 threshold 조정
            self.vel = 0

    def draw(self):  # 스크린에 돌을 그린다.
        pygame.draw.circle(self.surface, self.color, (int(self.x), int(self.y)), int(self.radius), 0)

    def is_dead(self):
        return not self.visible

    def check_alive(self, index):
        temp = abs(self.bycon // 5 - self.mass // 5)  # 서로 다른 팀이 부딪힘
        # print(self.mass+1, self.bycon, temp)
        if temp == 1 and self.mass % 5 < self.bycon % 5 and self.bycon != -1:
            print("%d died by contact miss" % (self.mass + 1))
            print(self.mass + 1, self.bycon + 1, index + 1)

            self.visible = 0
            self.x = 800
            self.radius = 0

            self.vel = 0
            self.angle = 0
            self.bycon = -1

    """def clicked(self):
        pos = pygame.mouse.get_pos()
        clicked_x, clicked_y = pos
        distance = hypot(clicked_x - self.x, clicked_y - self.y)
        if distance <= self.radius:
            self.radius = self.radius // 2"""


def collide(p1, p2):
    m1, m2 = 1, 1 # p1, p2의 질량. 일단 상수로 하드코딩해두었음. 추후에 Stone 클래스에 질량 속성을 추가하면 m1,m2 대신 사용.
    dx = p2.x - p1.x
    dy = p2.y - p1.y

    dist = hypot(dx, dy)
    if dist-1 <= p1.radius + p2.radius:
        p1.bycon = p2.mass
        p2.bycon = p1.mass

        tangent_line_angle = atan(dy/dx)/pi*180

        angle1_transform = p1.angle - tangent_line_angle
        angle2_transform = p2.angle - tangent_line_angle

        vel1_y = p1.vel * sin(radians(angle1_transform))
        vel2_y = p2.vel * sin(radians(angle2_transform))
        
        vel1_x = p1.vel * cos(radians(angle1_transform))
        vel2_x = p2.vel * cos(radians(angle2_transform))
        vel1_x_new = (1-(1+elasticity)*m2/(m1+m2))*vel1_x + (1+elasticity)*m2/(m1+m2)*vel2_x
        vel2_x_new = (1-(1+elasticity)*m1/(m1+m2))*vel2_x + (1+elasticity)*m1/(m1+m2)*vel1_x

        p1.vel = hypot(vel1_x_new, vel1_y)
        p2.vel = hypot(vel2_x_new, vel2_y)
        
        if vel1_x_new == 0:
            if vel1_y >=0:
                p1.angle = 90+tangent_line_angle
            else:
                p1.angle = -90+tangent_line_angle
        else:
            p1.angle = atan(vel1_y/vel1_x_new)/pi*180 + tangent_line_angle
            if vel1_x_new < 0:
                p1.angle += 180
        if vel2_x_new ==0:
            if vel2_y >= 0:
                p2.angle = 90+tangent_line_angle
            else:
                p2.angle = -90+tangent_line_angle
        else:
            p2.angle = atan(vel2_y/vel2_x_new)/pi*180 + tangent_line_angle
            if vel2_x_new <0:
                p2.angle += 180
        




        # 복잡한 충돌은 이 게임에서 불가능하다.
