__author__ = 'justinarmstrong'

# tools.py 파일 : 게임 프로그램의 전반적인 설정과 상태(States)를 세팅하는 파일.
import os, random
import pygame as pg
from . import constants as c

# Control(object) 클래스 : 게임의 전체적인 작동 방식(루프, 이벤트 발생, 상태 변환)들을 제어하는 클래스
class Control(object):
    
    """
    Control class for entire project.  Contains the game loop, and contains
    the event_loop which passes events to States as needed.  Logic for flipping
    states is also found here.
    """

    # init(self, caption) 메소드 : 객체 인스턴스(화면, 시간, 프레임, 상태 딕셔너리) 생성
    def __init__(self, caption):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.caption = caption
        self.fps = 60
        self.show_fps = False
        self.current_time = 0.0
        self.keys = pg.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None

    # setup_states(self, state_dict, start_state) 메소드 : 게임의 상태와 음악을 초기 설정하는 메소드
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.set_music()

    # update(self) 메소드 : 실시간 시간 흐름, 게임 내 상태를 설정하는 메소드
    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys, self.current_time)

    # flip_state(self) 메소드 : 게임 내에서 이전 창으로 돌아갔을 때 게임 내 설정을 이전 버전으로 되돌리는 메소드
    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        previous_music = self.state.music_title
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.previous = previous
        self.state.previous_music = previous_music
        self.state.startup(self.current_time, persist)
        self.set_music()

    # set_music(self) 메소드 : 다음 창으로 넘어갔을 때 음악을 새로 로드하는 메소드
    def set_music(self):
        """
        Set music for the new state.
        """
        if self.state.music_title == self.state.previous_music:
            pass
        elif self.state.music:
            pg.mixer.music.load(self.state.music)
            pg.mixer.music.set_volume(self.state.volume)
            pg.mixer.music.play(-1)

    # event_loop(self) 메소드 : 게임 내 이벤트들을 계속해서 발생시키도록 루프를 일으키는 메소드
    def event_loop(self):
        self.events = pg.event.get()

        for event in self.events:
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
                self.state.get_event(event)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
                self.state.get_event(event)

    # toggle_show_fps(self, key) 메소드 : 게임의 프레임을 화면에 보여주는 메소드
    def toggle_show_fps(self, key):
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)

    # main(self) 메소드 : Control 클래스의 메소드들을 총 제어하고 실행하는 메소드
    def main(self):
        """Main loop for entire program"""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)

# _State(object) 클래스 : 게임 전체의 설정과 상태를 지정하는 클래스
class _State(object):
    """Base class for all game states"""
    # __init__(self) 메소드 : 객체 인스턴스(시간, 데이터, 상태, 음악) 생성
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.game_data = {}
        self.music = None
        self.music_title = None
        self.previous_music = None

    def get_event(self, event):
        pass

    # startup(self, current_time, game_data) 메소드 : 게임을 시작할 때 초기 변수 값을 지정하는 메소드
    def startup(self, current_time, game_data):
        self.game_data = game_data
        self.start_time = current_time

    # cleanup(self) 메소드 : 게임 데이터를 반환하는 메소드
    def cleanup(self):
        self.done = False
        return self.game_data

    def update(self, surface, keys, current_time):
        pass

# load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', 'jpg', 'bmp')) 메소드 : 게임의 그래픽 요소를 반환하는 메소드
def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', 'jpg', 'bmp')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics

# load_all_music(directory, accept=('.wav', '.mp3', '.ogg', '.mdi')) 메소드 : 게임의 음악 요소를 반환하는 메소드
def load_all_music(directory, accept=('.wav', '.mp3', '.ogg', '.mdi')):
    songs = {}
    for song in os.listdir(directory):
        name, ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(directory, song)
    return songs

# load_all_fonts(directory, accept=('.ttf')) 메소드 : 게임의 폰트 요소를 반환하는 메소드
def load_all_fonts(directory, accept=('.ttf')):
    return load_all_music(directory, accept)

# load_all_tmx(directory, accept=('.tmx')) : 게임의 tmx(Pygame의 맵 로더) 요소를 반환하는 메소드
def load_all_tmx(directory, accept=('.tmx')):
    return load_all_music(directory, accept)

# load_all_sfx(directory, accept=('.wav','.mp3','.ogg','.mdi')) 메소드 : 게임의 효과(이펙트) 요소를 반환하는 메소드
def load_all_sfx(directory, accept=('.wav','.mp3','.ogg','.mdi')):
    effects = {}
    for fx in os.listdir(directory):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, fx))
    return effects

# get_image(x, y, width, height, sprite_sheet) 메소드 : 게임의 이미지 파일을 추출하여 반환하는 메소드
def get_image(x, y, width, height, sprite_sheet):
    """Extracts image from sprite sheet"""
    image = pg.Surface([width, height])
    rect = image.get_rect()

    image.blit(sprite_sheet, (0, 0), (x, y, width, height))
    image.set_colorkey(c.BLACK)

    return image

# get_tile(x, y, tileset, width=16, height=16, scale=1) 메소드 : 맵의 면적을 계산하여 반환하는 메소드
def get_tile(x, y, tileset, width=16, height=16, scale=1):
    """Gets the surface and rect for a tile"""
    surface = get_image(x, y, width, height, tileset)
    surface = pg.transform.scale(surface, (int(width*scale), int(height*scale)))
    rect = surface.get_rect()

    tile_dict = {'surface': surface,
                 'rect': rect}

    return tile_dict

# notify_observers(self, event) 메소드 : 발생한 이벤트들을 Observer에 전달하는 메소드
def notify_observers(self, event):
    """
    Notify all observers of events.
    """
    for each_observer in self.observers:
        each_observer.on_notify(event)

# create_game_data_dict() 메소드 : 게임 내 모든 요소(데이터)에 대한 딕셔너리를 생성하여 반환하는 메소드
def create_game_data_dict():
    """Create a dictionary of persistant values the player
    carries between states"""

    player_items = {'GOLD': dict([('quantity',100),
                                  ('value',0)]),
                    'Healing Potion': dict([('quantity',2),
                                            ('value',15), ('index',5)]), #스테이터스창에서 5번째 인덱스에 해당하는 아이템
                    'Ether Potion': dict([('quantity',1),
                                          ('value', 15),('index',4)]), #스테이터스창에서 4번째 인덱스에 해당하는 아이템
                    'Rapier': dict([('quantity', 1),
                                    ('value', 50),
                                    ('power', 9),
                                    ('index', 0)]), #스테이터스창에서 0번째 인덱스에 해당하는 아이템
                    'equipped weapon': 'Rapier',
                    'equipped armor': []}

    player_health = {'current': 70,
                     'maximum': 70}

    player_magic = {'current': 70,
                    'maximum': 70}

    player_stats = {'health': player_health,
                    'Level': 1,
                    'experience to next level': 30,
                    'magic': player_magic,
                    'attack points': 10,
                    'Defense Points': 10}


    data_dict = {'last location': None,
                 'last state': None,
                 'last direction': 'down',
                 'king item': 'GOLD',
                 'old man item': {'ELIXIR': dict([('value',1000),
                                                  ('quantity',1)])},
                 'player inventory': player_items,
                 'player stats': player_stats,
                 'battle counter': 50,
                 'treasure1': True,
                 'treasure2': True,
                 'treasure3': True,
                 'treasure4': True,
                 'treasure5': True,
                 'start of game': True,
                 'talked to king': False,
                 'brother quest complete': False,
                 'talked to sick brother': False,
                 'has brother elixir': False,
                 'elixir received': False,
                 'old man gift': '',
                 'battle type': '',
                 'crown quest': False,
                 'delivered crown': False,
                 'brother item': 'ELIXIR'
    }

    return data_dict







