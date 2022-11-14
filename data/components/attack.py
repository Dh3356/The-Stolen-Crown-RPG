"""
Sprites for attacks.
"""
import sys
import pygame as pg
from .. import setup, tools

#Python 2/3 compatibility.
if sys.version_info[0] == 2:
    range = xrange

#fire 클래스: fire 마법에 필요한 애니메이션 구현
class Fire(pg.sprite.Sprite):
    """
    Fire animation for attacks.
    """
    #생성자(객체 멤버변수 초기화: 애니메이션에 사용할 이미지, 현재 사용되는 이미지, 이미지와 관련된 정보, 타이머)
    def __init__(self, x, y):
        super(Fire, self).__init__()
        self.spritesheet = setup.GFX['explosion']
        self.get_image = tools.get_image
        self.image_list = self.make_image_list()
        self.index = 0
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect(left=x, top=y)
        self.timer = 0.0

    #fire 마법 애니메이션에 사용할 이미지 리스트 구현
    def make_image_list(self):
        """
        Make a list of images to cycle through for the
        animation.
        """
        image_list = []

        for row in range(8):
            for column in range(8):
                posx = column * 128
                posy = row * 128
                new_image = self.get_image(posx, posy, 128, 128,
                                           self.spritesheet)
                image_list.append(new_image)

        return image_list

    #인덱스를 증가시키며 이미지를 업데이트시키는 메소드
    def update(self):
        """
        Update fire explosion.
        """
        if self.index < (len(self.image_list) - 1):
            self.index += 1
            self.image = self.image_list[self.index]
        elif self.index == (len(self.image_list) - 1):
            self.kill()
