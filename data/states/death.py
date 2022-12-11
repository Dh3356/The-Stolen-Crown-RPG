import copy, pickle, sys, os
import pygame as pg
from .. import setup, tools
from .. import observer
from ..components import person
from .. import constants as c
import googletrans#구글 번역 API

#구글 번역 변수 translator.translate(문장, dest='ko').text 함수를 사용해 한글 문자열로 번역 가능
translator = googletrans.Translator()

#Python 2/3 compatibility.
if sys.version_info[0] == 2:
    import cPickle
    pickle = cPickle


class Arrow(pg.sprite.Sprite):
    """
    Arrow to select restart or saved gamed.
    죽었을 때 재시작할지 저장된 시점부터 다시 할지 선택할 화살표를 구현한다.
    """
    def __init__(self, x, y):
        #해당 객체에 대한 인스턴스를 생성한다
        super(Arrow, self).__init__()
        self.image = setup.GFX['smallarrow']
        self.rect = self.image.get_rect(x=x,
                                        y=y)
        self.index = 0
        self.pos_list = [y, y+34]
        self.allow_input = False
        self.observers = [observer.SoundEffects()]
       
    def notify(self, event):
        """
        Notify all observers of event.
        모든 옵저버에 이벤트가 일어났음을 알린다.
        """
        for observer in self.observers:
            observer.on_notify(event)

    def update(self, keys):
        """
        Update arrow position.
         화살표의 위치를 업데이트한다.
        """
        if self.allow_input:
            if keys[pg.K_DOWN] and not keys[pg.K_UP] and self.index == 0:
                self.index = 1
                self.allow_input = False
                self.notify(c.CLICK)
            elif keys[pg.K_UP] and not keys[pg.K_DOWN] and self.index == 1:
                self.index = 0
                self.allow_input = False
                self.notify(c.CLICK)

            self.rect.y = self.pos_list[self.index]

        if not keys[pg.K_DOWN] and not keys[pg.K_UP]:
            self.allow_input = True


class DeathScene(tools._State):
    """
    Scene when the player has died.
    플레이어가 죽었을 때 사망 시 장면을  출력한다.
    """
    def __init__(self):
        #해당 객체에 대한 인스턴스를 생성한다.
        super(DeathScene, self).__init__()
        self.next = c.TOWN
        self.music = setup.MUSIC['shop_theme']
        self.volume = 0.5
        self.music_title = 'shop_theme'

    def startup(self, current_time, game_data):
        #사망 시 장면이 나올 때 데이터를 초기화한다.
        self.game_data = game_data
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.background = pg.Surface(setup.SCREEN_RECT.size)
        self.background.fill(c.BLACK_BLUE)
        self.player = person.Player('down', self.game_data, 1, 1, 'resting', 1)
        self.player.image = pg.transform.scale2x(self.player.image)
        self.player.rect = self.player.image.get_rect()
        self.player.rect.center = setup.SCREEN_RECT.center
        self.message_box = self.make_message_box()
        self.arrow = Arrow(300, 532)
        self.state_dict = self.make_state_dict()
        self.state = c.TRANSITION_IN
        self.alpha = 255
        self.name = c.DEATH_SCENE
        self.transition_surface = pg.Surface(setup.SCREEN_RECT.size)
        self.transition_surface.fill(c.BLACK_BLUE)
        self.transition_surface.set_alpha(self.alpha)
        if not os.path.isfile("save.p"):
            game_data = tools.create_game_data_dict()
            pickle.dump(game_data, open("save.p", "wb"))
        self.observers = [observer.SoundEffects()]

    def notify(self, event):
        """
        Notify all observers of event.
        모든 옵저버에게 사망 이벤트가 나왔음을 알린다.
        """
        for observer in self.observers:
            observer.on_notify(event)

    def make_message_box(self):
        """
        Make the text box informing of death.
        죽음에 대한 정보를 보여줄 텍스트 박스를 만든다. 
        """
        box_image = setup.GFX['dialoguebox']
        box_rect = box_image.get_rect()
        text = translator.translate('You have died. Restart from last save point?', dest='ko').text
        text_render = self.font.render(text, True, c.NEAR_BLACK) 
        text_rect = text_render.get_rect(centerx=box_rect.centerx,
                                         y=30)
        text2 = translator.translate('Yes', dest='ko').text
        text2_render = self.font.render(text2, True, c.NEAR_BLACK)
        text2_rect = text2_render.get_rect(centerx=box_rect.centerx,
                                           y=70)

        text3 = translator.translate('No', dest='ko').text
        text3_render = self.font.render(text3, True, c.NEAR_BLACK)
        text3_rect = text3_render.get_rect(centerx=box_rect.centerx,
                                           y=105)

        temp_surf = pg.Surface(box_rect.size)
        temp_surf.set_colorkey(c.BLACK)
        temp_surf.blit(box_image, box_rect)
        temp_surf.blit(text_render, text_rect)
        temp_surf.blit(text2_render, text2_rect)
        temp_surf.blit(text3_render, text3_rect)
        
        box_sprite = pg.sprite.Sprite()
        box_sprite.image = temp_surf
        box_sprite.rect = temp_surf.get_rect(bottom=608)
        
        return box_sprite

    def make_state_dict(self):
        """
        Make the dicitonary of state methods for the scene.
        죽음 장면을 위한 상태 메소드 딕셔너리를 만든다.
        """
        state_dict = {c.TRANSITION_IN: self.transition_in,
                      c.TRANSITION_OUT: self.transition_out,
                      c.NORMAL: self.normal_update}

        return state_dict

    def update(self, surface, keys, *args):
        """
        Update scene.
        장면을 업데이트한다.
        """
        update_level = self.state_dict[self.state]
        update_level(keys)
        self.draw_level(surface)

    def transition_in(self, *args):
        """
        Transition into scene with a fade.
        페이드인 효과를 준다.
        """
        self.transition_surface.set_alpha(self.alpha)
        self.alpha -= c.TRANSITION_SPEED
        if self.alpha <= 0:
            self.alpha = 0
            self.state = c.NORMAL

    def transition_out(self, *args):
        """
        Transition out of scene with a fade.
        페이드아웃 효과를 준다.
        """
        self.transition_surface.set_alpha(self.alpha)
        self.alpha += c.TRANSITION_SPEED
        if self.alpha >= 255:
            self.done = True

    def normal_update(self, keys):
        #업데이트 해야할 항목들을 업데이트시킨다.
        self.arrow.update(keys)
        self.check_for_input(keys)

    def check_for_input(self, keys):
        """
        Check if player wants to restart from last save point
        or just start from the beginning of the game.
        플레이어가 재시작하는지 아니면 세이브 지점부터 다시 하는지를 체크한다.
        """
        if keys[pg.K_SPACE]:
            if self.arrow.index == 0:
                self.next = c.TOWN
                self.game_data = pickle.load(open("save.p", "rb"))
            elif self.arrow.index == 1:
                self.next = c.MAIN_MENU
            self.state = c.TRANSITION_OUT
            self.notify(c.CLICK2)

    def draw_level(self, surface):
        """
        Draw background, player, and message box.
         플레이어, 메시지 박스, 배경을 그린다.
        """
        surface.blit(self.background, (0, 0))
        surface.blit(self.player.image, self.player.rect)
        surface.blit(self.message_box.image, self.message_box.rect)
        surface.blit(self.arrow.image, self.arrow.rect)
        surface.blit(self.transition_surface, (0, 0))





        
