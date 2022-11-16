import random
import pygame as pg
from . import constants as c

class CollisionHandler(object):
    """
    Handles collisions between the user, blockers and computer characters
    사용자, 차단기 및 컴퓨터 문자 간의 충돌을 처리합니다.
    """
    def __init__(self, player, blockers, sprites, portals, level):
        self.player = player
        self.static_blockers = blockers
        self.blockers = self.make_blocker_list(blockers, sprites)
        self.sprites = sprites
        self.portals = portals
        self.level = level

    def make_blocker_list(self, blockers, sprites):
        """
        Return a combined list of sprite blockers and object blockers.
        스프라이트 차단기 및 객체 차단기의 결합된 목록을 반환
        """
        blocker_list = []

        for blocker in blockers:
            blocker_list.append(blocker)

        for sprite in sprites:
            blocker_list.extend(sprite.blockers)

        return blocker_list

    def update(self, keys, current_time):
        """
        Check for collisions between game objects.
        게임 개체 간의 충돌을 확인합니다.
        """
        self.blockers = self.make_blocker_list(self.static_blockers,
                                               self.sprites)
        self.player.rect.move_ip(self.player.x_vel, self.player.y_vel)
        self.check_for_blockers()

        for sprite in self.sprites:
            sprite.rect.move_ip(sprite.x_vel, sprite.y_vel)
        self.check_for_blockers()

        if self.player.rect.x % 32 == 0 and self.player.rect.y % 32 == 0:
            if not self.player.state == 'resting':
                self.check_for_portal()
                self.check_for_battle()
            self.player.begin_resting()

        for sprite in self.sprites:
            if sprite.state == 'automoving':
                if sprite.rect.x % 32 == 0 and sprite.rect.y % 32 == 0:
                    sprite.begin_auto_resting()

    def check_for_portal(self):
        """
        Check for a portal to change level scene.
        레벨 화면을을 변경할 포털 확인
        """
        portal = pg.sprite.spritecollideany(self.player, self.portals)

        if portal:
            self.level.use_portal = True
            self.level.portal = portal.name

    def check_for_blockers(self):
        """
        Checks for collisions with blocker rects.
        차단기 수정과의 충돌을 확인합니다.
        """
        player_collided = False
        sprite_collided_list = []

        for blocker in self.blockers:
            if self.player.rect.colliderect(blocker):
                player_collided = True

        if player_collided: 
            self.reset_after_collision(self.player)
            self.player.begin_resting()

        for sprite in self.sprites:
            for blocker in self.static_blockers:
                if sprite.rect.colliderect(blocker):
                    sprite_collided_list.append(sprite)
            if sprite.rect.colliderect(self.player.rect):
                sprite_collided_list.append(sprite)
            sprite.kill()
            if pg.sprite.spritecollideany(sprite, self.sprites):
                sprite_collided_list.append(sprite)
            self.sprites.add(sprite)
            for blocker in sprite.wander_box:
                if sprite.rect.colliderect(blocker):
                    sprite_collided_list.append(sprite)


        for sprite in sprite_collided_list:
            self.reset_after_collision(sprite)
            sprite.begin_auto_resting()

    def reset_after_collision(self, sprite):
        """
        Put player back to original position
        플레이어를 원래 위치로 되돌립니다.
        """
        if sprite.x_vel != 0:
                sprite.rect.x -= sprite.x_vel
        else:
            sprite.rect.y -= sprite.y_vel

    def check_for_battle(self):
        """
        Switch scene to battle 1/5 times if battles are allowed.
        전투가 허용되는 경우 장면을 1/5로 전투로 전환합니다.
        """
        if self.level.allow_battles:
            self.level.game_data['battle counter'] -= 5
            if self.level.game_data['battle counter'] <= 0:
                self.level.switch_to_battle = True



