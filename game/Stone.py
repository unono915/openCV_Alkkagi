import pygame
from math import *

elasticity = 1  # 충돌 시 속력 감소


class Stone:  # 처음 돌을 놓는 위치와 레벨을 전달받고, 반지름 질량은 기본값을 설정
    # x, y, radius
    def __init__(self, start_x=10, start_y=10, radius=15, mass=1, surface=None, team=None, visible=1, bycon=-1):
        self.radius = radius
        self.x = start_x
        self.y = start_y
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

    def move(self, dt):  # 전달받은 시간 간격에 속력을 곱해 돌의 위치를 이동시킨다. 속력은 0.95배로 계속 줄어든다.
        self.x += dt * self.vel * cos(radians(self.angle))
        self.y += dt * self.vel * sin(radians(self.angle))

        if self.x > 550 or self.y > 550 or self.x < 50 or self.y < 50:
            self.visible = 0
            self.vel = 0
            print("%d died by out of range" % (self.mass + 1))

        self.vel *= 0.95  # 속도의 감소
        if abs(self.vel) < 10:  # TODO 정지하도록하는 threshold 조정
            self.vel = 0

    def draw(self):  # 스크린에 돌을 그린다.
        pygame.draw.circle(self.surface, self.color, (int(self.x), int(self.y)), int(self.radius), 0)

    def is_dead(self):
        return not self.visible
