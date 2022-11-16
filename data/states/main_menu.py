import pickle, sys, os
import pygame as pg
from .. import setup, tools, tilerender
from .. import observer
from .. import constants as c
import death
 

#Python 2/3 compatibility.
#파이썬 버전이 2.xx 이면 cPickle을 import한다
if sys.version_info[0] == 2:
    import cPickle
    pickle = cPickle 

# 게임 전체의 설정과 상태를 지정하는 클래스(tools.py의 _State클래스를 상속받는다)
class Menu(tools._State):
    #초기화. 부모 클래스의 초기화 함수 실행해서 시간, 데이터, 상태, 음악등을 초기화하고 추가로 music, music_title, volume 등을 초기화한다
    def __init__(self):
        super(Menu, self).__init__()
        self.music = setup.MUSIC['kings_theme']
        self.music_title = 'kings_theme'
        self.volume = 0.4
        self.next = c.INSTRUCTIONS
        self.tmx_map = setup.TMX['title']
        self.name = c.MAIN_MENU
        self.startup(0, 0)
    
    #그래픽적 요소들(map_image, map_rect, viewport)을 초기화한다
    def startup(self, *args):
        self.renderer = tilerender.Renderer(self.tmx_map)
        self.map_image = self.renderer.make_2x_map()
        self.map_rect = self.map_image.get_rect()
        self.viewport = self.make_viewport(self.map_image)
        self.level_surface = pg.Surface(self.map_rect.size)
        self.title_box = setup.GFX['title_box']
        self.title_rect = self.title_box.get_rect()
        self.title_rect.midbottom = self.viewport.midbottom
        self.title_rect.y -= 30
        self.state_dict = self.make_state_dict()
        self.state = c.TRANSITION_IN
        self.alpha = 255
        self.transition_surface = pg.Surface(setup.SCREEN_RECT.size)
        self.transition_surface.fill(c.BLACK_BLUE)
        self.transition_surface.set_alpha(self.alpha)

    #level을 볼 수 있는 뷰포트를 생성한다.
    def make_viewport(self, map_image):
        """
        Create the viewport to view the level through.
        """
        map_rect = map_image.get_rect()
        return setup.SCREEN.get_rect(bottomright=map_rect.bottomright)

    #state메소드들의 딕셔너리를 만들어 반환한다
    def make_state_dict(self):
        """
        Make the dictionary of state methods for the level.
        """
        state_dict = {c.TRANSITION_IN: self.transition_in, c.TRANSITION_OUT: self.transition_out, c.NORMAL: self.normal_update}

        return state_dict
        
    #scene을 update한다
    def update(self, surface, *args):
        """
        Update scene.
        """
        update_level = self.state_dict[self.state]
        update_level()
        self.draw_level(surface)
        
    #tmx 맵과 title box를 화면에 표시합니다
    def draw_level(self, surface):
        """
        Blit tmx map and title box onto screen.
        """
        self.level_surface.blit(self.map_image, self.viewport, self.viewport)
        self.level_surface.blit(self.title_box, self.title_rect)
        surface.blit(self.level_surface, (0,0), self.viewport)
        surface.blit(self.transition_surface, (0,0))
        
    #이벤트를 받는다
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.state = c.TRANSITION_OUT

    #fade를 주면서 scene으로 전환한다
    def transition_in(self):
        """
        Transition into scene with a fade.
        """
        self.transition_surface.set_alpha(self.alpha)
        self.alpha -= c.TRANSITION_SPEED
        if self.alpha <= 0:
            self.alpha = 0
            self.state = c.NORMAL
        
    #fade를 주면서 scene에서 나온다
    def transition_out(self):
        """
        Transition out of scene with a fade.
        """
        self.transition_surface.set_alpha(self.alpha)
        self.alpha += c.TRANSITION_SPEED
        if self.alpha >= 255:
            self.done = True

    #빈 메소드(내용: pass)
    def normal_update(self):
        pass

#Instructions page를 나타내는 클래스(tools.py의 _State클래스를 상속받는다)
class Instructions(tools._State):
    """
    Instructions page.
    """
    
    #초기화. 부모 클래스의 초기화 함수 실행해서 시간, 데이터, 상태, 음악등을 초기화하고 추가로 music, music_title, tmx_map을 초기화한다
    def __init__(self):
        super(Instructions, self).__init__()
        self.tmx_map = setup.TMX['title']
        self.music = None
        self.music_title = None
        
    #그래픽적 요소들(map_image, map_rect, viewport)을 초기화한다
    def startup(self, *args):
        self.renderer = tilerender.Renderer(self.tmx_map)
        self.map_image = self.renderer.make_2x_map()
        self.map_rect = self.map_image.get_rect()
        self.viewport = self.make_viewport(self.map_image)
        self.level_surface = pg.Surface(self.map_rect.size)
        self.title_box = self.set_image()
        self.title_rect = self.title_box.get_rect()
        self.title_rect.midbottom = self.viewport.midbottom
        self.title_rect.y -= 30
        self.game_data = tools.create_game_data_dict()
        self.next = self.set_next_scene()
        self.state_dict = self.make_state_dict()
        self.name = c.MAIN_MENU
        self.state = c.TRANSITION_IN
        self.alpha = 255
        self.transition_surface = pg.Surface(setup.SCREEN_RECT.size)
        self.transition_surface.fill(c.BLACK_BLUE)
        self.transition_surface.set_alpha(self.alpha)
        self.observers = [observer.SoundEffects()]

    #self.observers의 on_notify 함수에 event를 전달한다
    def notify(self, event):
        """
        Notify all observers of event.
        """
        for observer in self.observers:
            observer.on_notify(event)

    #saved된 game이 있는지 확인하고 saved된 game이 있으면 scene을 load하고 없으면 게임을 처음부터 시작한다
    def set_next_scene(self):
        """
        Check if there is a saved game. If not, start
        game at begining.  Otherwise go to load game scene.
        """
        if not os.path.isfile("save.p"):
            next_scene = c.OVERWORLD
        else:
            next_scene = c.LOADGAME

        return next_scene

    #message box에 이미지를 set한다
    def set_image(self):
        """
        Set image for message box.
        """
        return setup.GFX['instructions_box']

    #level을 볼 수 있는 뷰포트를 생성한다.
    def make_viewport(self, map_image):
        """
        Create the viewport to view the level through.
        """
        map_rect = map_image.get_rect()
        return setup.SCREEN.get_rect(bottomright=map_rect.bottomright)

    #state메소드들의 딕셔너리를 만들어 반환한다
    def make_state_dict(self):
        """
        Make the dictionary of state methods for the level.
        """
        state_dict = {c.TRANSITION_IN: self.transition_in, c.TRANSITION_OUT: self.transition_out, c.NORMAL: self.normal_update}

        return state_dict
        
    #scene을 update한다
    def update(self, surface, keys, *args):
        """
        Update scene.
        """
        update_level = self.state_dict[self.state]
        update_level(keys)
        self.draw_level(surface)

    #tmx 맵과 title box를 화면에 표시합니다
    def draw_level(self, surface):
        """
        Blit tmx map and title box onto screen.
        """
        self.level_surface.blit(self.map_image, self.viewport, self.viewport)
        self.level_surface.blit(self.title_box, self.title_rect)
        self.draw_arrow()
        surface.blit(self.level_surface, (0,0), self.viewport)
        surface.blit(self.transition_surface, (0,0))

    #빈 메소드(내용: pass)
    def draw_arrow(self):
        pass
        
    #이벤트를 받는다
    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.state = c.TRANSITION_OUT

    #fade를 주면서 scene으로 전환한다
    def transition_in(self, *args):
        """
        Transition into scene with a fade.
        """
        self.transition_surface.set_alpha(self.alpha)
        self.alpha -= c.TRANSITION_SPEED
        if self.alpha <= 0:
            self.alpha = 0
            self.state = c.NORMAL

    #fade를 주면서 scene에서 나온다
    def transition_out(self, *args):
        """
        Transition out of scene with a fade.
        """
        self.transition_surface.set_alpha(self.alpha)
        self.alpha += c.TRANSITION_SPEED
        if self.alpha >= 255:
            self.done = True

    #빈 메소드(내용: pass)
    def normal_update(self, *args):
        pass

#게임을 로드하는 클래스(Instructions 클래스를 상속받는다)
class LoadGame(Instructions):
    
    #부모 클래스의 초기화 함수 실행해서 시간, 데이터, 상태, 음악, music, music_title, tmx_map 등을 초기화하고 추가로 arrow들도 초기화한다
    def __init__(self):
        super(LoadGame, self).__init__()
        self.arrow = death.Arrow(200, 260)
        self.arrow.pos_list[1] += 34
        self.allow_input = False

    #message box에 이미지를 set한다
    def set_image(self):
        """
        Set image for message box.
        """
        return setup.GFX['loadgamebox']

    #arrow를 그린다
    def draw_arrow(self):
        self.level_surface.blit(self.arrow.image, self.arrow.rect)

    #빈 메소드(내용: pass)
    def get_event(self, event):
        pass
    
    #키를 눌렀을 때 업데이트한다
    def normal_update(self, keys):
        if self.allow_input:
            if keys[pg.K_DOWN] and self.arrow.index == 0:
                self.arrow.index = 1
                self.notify(c.CLICK)
                self.allow_input = False
            elif keys[pg.K_UP] and self.arrow.index == 1:
                self.arrow.index = 0
                self.notify(c.CLICK)
                self.allow_input = False
            elif keys[pg.K_SPACE]:
                if self.arrow.index == 0:
                    self.game_data = pickle.load(open("save.p", "rb"))
                    self.next = c.TOWN
                    self.state = c.TRANSITION_OUT
                else:
                    self.next = c.OVERWORLD
                    self.state = c.TRANSITION_OUT
                self.notify(c.CLICK2)

            self.arrow.rect.y = self.arrow.pos_list[self.arrow.index]  

        if not keys[pg.K_DOWN] and not keys[pg.K_UP]:
            self.allow_input = True

        


