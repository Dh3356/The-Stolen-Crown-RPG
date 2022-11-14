"""
This is a test of using the pytmx library with Tiled.
"""

# tilerender.py 파일 : pytmx(파이썬 기반 게임의 맵 로더)를 이용하여 사선 격자 형태의 월드맵을 구현하는 파일.

# 모듈: pygame, pytmx
import pygame as pg
from . import pytmx

# Renderer(object) 클래스 : 사선 격자 형태의 월드맵을 구현하여 렌더링 하는 클래스.
class Renderer(object):
    """
    This object renders tile maps from Tiled
    """

    # init(self, filename) 메소드 : 객체 인스턴스(pygame 로드, 맵 사이즈) 생성
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm

    # render(self, surface) 메소드 : 맵을 구성하고 화면에 렌더링하는 메소드
    def render(self, surface):

        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        gt = self.tmx_data.getTileImageByGid

        if self.tmx_data.background_color:
            surface.fill(self.tmx_data.background_color)

        for layer in self.tmx_data.visibleLayers:
            if isinstance(layer, pytmx.TiledLayer):
                for x, y, gid in layer:
                    tile = gt(gid)
                    if tile:
                        surface.blit(tile, (x * tw, y * th))

            elif isinstance(layer, pytmx.TiledObjectGroup):
                pass

            elif isinstance(layer, pytmx.TiledImageLayer):
                image = gt(layer.gid)
                if image:
                    surface.blit(image, (0, 0))

    # make_2x_map(self) 메소드 : 2배 크기의 맵을 렌더링하는 메소드
    def make_2x_map(self):
        temp_surface = pg.Surface(self.size)
        self.render(temp_surface)
        temp_surface = pg.transform.scale2x(temp_surface)
        return temp_surface