__author__ = 'justinarmstrong'
import pygame as pg
from data import constants as c

#장소를 변경할 때 사용하는 클래스
class Portal(pg.sprite.Sprite):
    """Used to change level state"""
    #클래스 멤버변수 초기화
    def __init__(self, x, y, name):
        super(Portal, self).__init__()
        self.image = pg.Surface((32, 32))
        self.image.fill(c.BLACK)
        self.rect = pg.Rect(x, y, 32, 32)
        self.name = name
