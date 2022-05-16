import pygame
from pygame.locals import *


def stoneshooting(stone, selectstone, turn):
    plus_vel = 250  # 한번의 클릭으로 더해지는 속도
    # plus_ang = -10  # 한번의 클릭으로 생겨나는 각도
    now_select = selectstone
    # stone = STONE

    for event in pygame.event.get():  # 키보드 입력을 받는다.
        if event.type == QUIT:
            return -111, -111, turn
        if event.type == KEYDOWN:
            # ESC 종료 키
            if event.key == K_ESCAPE:
                return -111, -111, turn

            
            # 돌 선택
            if event.key == K_1:  # K_0 == 48 ~
                now_select = 0 + turn * 5
            elif event.key == K_2:
                now_select = 1 + turn * 5
            elif event.key == K_3:
                now_select = 2 + turn * 5
            elif event.key == K_4:
                now_select = 3 + turn * 5
            elif event.key == K_5:
                now_select = 4 + turn * 5
            elif event.key == K_r:
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
            elif event.key == K_SPACE and stone.vel == 0:
                a = stone.hidvel
                stone.hidvel = 0
                stone.bycon = -1
                turn = 1 - turn
                return a, now_select, turn

            # 방향 조절
            """key_event = pygame.key.get_pressed()
            if key_event[pygame.K_LEFT]:
                stone.angle += plus_ang

            elif key_event[pygame.K_RIGHT]:
                stone.angle -= plus_ang"""
    return 0, now_select, turn
