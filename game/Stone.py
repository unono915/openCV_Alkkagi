import pygame
from math import *

elasticity = 1  # 충돌 시 속력 감소


class Stone:  # 처음 돌을 놓는 위치와 레벨을 전달받고, 반지름 질량은 기본값을 설정
    # x, y, radius
    def __init__(self, start_x=10, start_y=10, radius=15, mass=1, surface=None, team=None, visible=1, bycon=-1):
        self.radius = radius
        self.x = start_x
        self.y = start_y
        self.prev_x = start_x
        self.prev_y = start_y
        self.next_x = start_x
        self.next_y = start_y
        self.mass = mass

        self.color = (128, 128, 128) if team else (255, 255, 255)

        self.isalive = True
        self.angle = 0
        self.arrow_angle = 0
        self.vel = 0
        self.surface = surface
        self.team = team
        self.hidvel = 0
        self.hidang = 0
        self.visible = visible
        self.bycon = bycon

    def set_next_xy(self, dt):
        self.next_x = self.x + dt * self.vel * cos(radians(self.angle))
        self.next_y = self.y + dt * self.vel * sin(radians(self.angle))

    def check_collision(self):
        dx = self.next_x - self.x
        dy = self.next_y - self.y
        dist = hypot(dx, dy)

        if dist == 0:  # 그냥 안 움직인거
            return False

        return dist < self.radius * 2

    def move(self, dt):  # 전달받은 시간 간격에 속력을 곱해 돌의 위치를 이동시킨다. 속력은 0.95배로 계속 줄어든다.
        # self.prev_x = self.x
        # self.prev_y = self.y

        self.x += dt * self.vel * cos(radians(self.angle))
        self.y += dt * self.vel * sin(radians(self.angle))

        if self.x > 550 or self.y > 550 or self.x < 50 or self.y < 50:
            self.visible = 0
            self.vel = 0
            self.x = 0
            self.y = 0
            print("%d died by out of range" % (self.mass + 1))

        self.vel *= 0.95  # 속도의 감소
        if abs(self.vel) < 10:  # TODO 정지하도록하는 threshold 조정
            self.vel = 0

    def reduce_vel(self):
        self.vel *= 0.95  # 속도의 감소
        if abs(self.vel) < 10:  # TODO 정지하도록하는 threshold 조정
            self.vel = 0

    def draw(self):  # 스크린에 돌을 그린다.
        pygame.draw.circle(self.surface, self.color, (int(self.x), int(self.y)), int(self.radius), 0)

    def is_dead(self):
        return not self.visible

    def collide(self, p):
        elasticity = 1  # 충돌 시 속력 감소
        m1, m2 = 1, 1  # p1, p2의 질량. 일단 상수로 하드코딩해두었음. 추후에 Stone 클래스에 질량 속성을 추가하면 m1,m2 대신 사용.
        dx = p.x - self.x
        dy = p.y - self.y

        dist = hypot(dx, dy)
        if dist <= self.radius + self.radius:

            self.bycon = p.mass
            p.bycon = self.mass

            if dx == 0:
                tangent_line_angle = 90 if dy > 0 else -90
            else:
                tangent_line_angle = atan(dy / dx) / pi * 180

            # tangent_line_angle = atan(dy / dx) / pi * 180 if dx else 90

            angle1_transform = self.angle - tangent_line_angle
            angle2_transform = p.angle - tangent_line_angle

            vel1_y = self.vel * sin(radians(angle1_transform))
            vel2_y = p.vel * sin(radians(angle2_transform))

            vel1_x = self.vel * cos(radians(angle1_transform))
            vel2_x = p.vel * cos(radians(angle2_transform))

            vel1_x_new = (1 - (1 + elasticity) * m2 / (m1 + m2)) * vel1_x + (1 + elasticity) * m2 / (m1 + m2) * vel2_x
            vel2_x_new = (1 - (1 + elasticity) * m1 / (m1 + m2)) * vel2_x + (1 + elasticity) * m1 / (m1 + m2) * vel1_x

            self.vel = hypot(vel1_x_new, vel1_y)
            p.vel = hypot(vel2_x_new, vel2_y)

            if vel1_x_new == 0:
                print(self.mass, " angle:", self.angle, " / ", p.mass, " angle:", p.angle, "\n")
                if vel1_y >= 0:
                    self.angle = (90 + tangent_line_angle) % 360
                else:
                    self.angle = (-90 + tangent_line_angle) % 360
            else:
                self.angle = (atan(vel1_y / vel1_x_new) / pi * 180 + tangent_line_angle) % 360
                if vel1_x_new < 0:
                    self.angle += 180
                    self.angle %= 360
            if vel2_x_new == 0:
                print(self.mass, " angle:", self.angle, " / ", p.mass, " angle:", p.angle, "\n")
                if vel2_y >= 0:
                    p.angle = (90 + tangent_line_angle) % 360
                else:
                    p.angle = (-90 + tangent_line_angle) % 360
            else:
                p.angle = (atan(vel2_y / vel2_x_new) / pi * 180 + tangent_line_angle) % 360
                if vel2_x_new < 0:
                    p.angle += 180
                    p.angle %= 360

            gap = self.radius - dist / 2 + 1
            self.x += gap * cos(radians(self.angle))
            self.y += gap * sin(radians(self.angle))
