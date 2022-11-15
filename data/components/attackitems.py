"""
Attack equipment for battles.
"""
import copy
import pygame as pg
from .. import tools, setup
from .. import constants as c

#일반공격에 사용되는 검 이미지 애니메이션에 사용하는 클래스
class Sword(object):
    """
    Sword that appears during regular attacks.
    """
    
    #생성자(객체 멤버변수 초기화: player의 sprite sheet, 현재 사용되는 이미지, 이미지와 관련된 정보, 타이머)
    def __init__(self, player):
        self.player = player
        self.sprite_sheet = setup.GFX['shopsigns']
        self.image_list = self.make_image_list()
        self.index = 0
        self.timer = 0.0

    #sword2 이미지로 이미지 리스트를 생성.
    def make_image_list(self):
        """
        Make the list of two images for animation.
        """
        image_list = [tools.get_image(48, 0, 16, 16, self.sprite_sheet),
                      tools.get_image(0, 0, 22, 16, setup.GFX['sword2'])]
        return image_list

    #해당 객체의 index 멤버변수를 참조하여 이미지리스트에서 이미지를 반환.
    @property
    def image(self):
        new_image = self.image_list[self.index]
        return pg.transform.scale2x(new_image)

    #플레이어의 rect값을 얕은복사하여 bottom, right값 수정하여 반환(검의 위치 지정)
    @property
    def rect(self):
        new_rect = copy.copy(self.player.rect)
        new_rect.bottom += 17
        new_rect.right -= 16
        return new_rect

    #timer값에 따라 index값을 변경(0 혹은 1)
    def update(self, current_time):
        if (current_time - self.timer) > 60:
            self.timer = current_time
            if self.index == 0:
                self.index += 1
            else:
                self.index -= 1
    #surface에 sprite를 그리는 메소드. 게임 내에서 attack 선택시 surface에 blit하여 보여준다.
    def draw(self, surface):
        """
        Draw sprite to surface.
        """
        if self.player.state == 'attack':
            surface.blit(self.image, self.rect)

#피격, 타격 혹은 힐링포션 사용 시 체력 변화 수치를 보여주는 공간 구현에 사용하는 클래스
class HealthPoints(pg.sprite.Sprite):
    """
    A sprite that shows how much damage an attack inflicted.
    """
    #객체 멤버변수 초기화(데미지 표시 구현에 필요한 변수들)
    def __init__(self, points, topleft_pos, damage=True, ether=False):
        super(HealthPoints, self).__init__()
        self.ether = ether
        self.damage = damage
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 27)
        self.text_image = self.make_surface(points)
        self.rect = self.text_image.get_rect(x=topleft_pos[0]+20,
                                             bottom=topleft_pos[1]+10)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.set_colorkey(c.BLACK)
        self.alpha = 255
        self.image.set_alpha(self.alpha)
        self.image.blit(self.text_image, (0, 0))
        self.start_posy = self.rect.y
        self.y_vel = -1
        self.fade_out = False

    #데미지창을 표시하는 surface 구현하여 반환
    #damge,points 값 참조하여 -데미지, +힐, Miss 표시
    def make_surface(self, points):
        """
        Make the surface for the sprite.
        """
        if self.damage:
            if points > 0:
                text = "-{}".format(str(points))
                surface = self.font.render(text, True, c.RED)
                return surface
            else:
                return self.font.render('Miss', True, c.WHITE).convert_alpha()
        else:
            text = "+{}".format(str(points))
            if self.ether:
                surface = self.font.render(text, True, c.PINK)
            else:
                surface = self.font.render(text, True, c.GREEN)

            return surface

    #스프라이트의 포지션을 업데이트하고 필요없는 스프라이트를 삭제하는 메소드
    #fade_animation 메소드 참조, 점점 흐려지는 애니메이션 구현.
    def update(self):
        """
        Update sprite position or delete if necessary.
        """
        self.fade_animation()
        self.rect.y += self.y_vel
        if self.rect.y < (self.start_posy - 29):
            self.fade_out = True

    #fade_out값을 참조하여 true일 시 alpha값을 15씩 감소시키며 fade 애니메이션 구현.
    #alpha값(투명도 값)이 0 이하일 시 sprite kill.
    def fade_animation(self):
        """
        Fade score in and out.
        """
        if self.fade_out:
            self.image = pg.Surface(self.rect.size).convert()
            self.image.set_colorkey(c.BLACK)
            self.image.set_alpha(self.alpha)
            self.image.blit(self.text_image, (0, 0))
            self.alpha -= 15
            if self.alpha <= 0:
                self.kill()









