__author__ = 'justinarmstrong'

"""
This module initializes the display and
creates dictionaries of resources.
"""

# setup.py 파일 : 게임의 기본 세팅을 설정한다.

# 모듈: os, pygame, tools,constants
import os
import pygame as pg
from . import tools
from . import constants as c

# 변수 GAME : 게임 시작을 위한 변수 선언
GAME = 'BEGIN GAME'

# 변수 ORIGINAL_CAPTION : 게임 타이틀을 위한 변수 선언
ORIGINAL_CAPTION = 'The Stolen Crown'

# Pygame 초기 설정(초기화, 방향키 설정, 화면 해상도)
os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode((800, 608))
SCREEN_RECT = SCREEN.get_rect()

# 폰트, 음악, 그래픽 설정
FONTS = tools.load_all_fonts(os.path.join('resources', 'fonts'))
MUSIC = tools.load_all_music(os.path.join('resources', 'music'))
GFX = tools.load_all_gfx(os.path.join('resources', 'graphics'))
SFX = tools.load_all_sfx(os.path.join('resources', 'sound'))
TMX = tools.load_all_tmx(os.path.join('resources', 'tmx'))

FONT = pg.font.Font(FONTS['Fixedsys500c'], 20)



