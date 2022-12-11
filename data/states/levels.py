"""
This is the base class for all level states (i.e. states
where the player can move around the screen).  Levels are
differentiated by self.name and self.tmx_map.
This class inherits from the generic state class
found in the tools.py module.
"""
import copy, sys
import pygame as pg
from .. import tools, collision
from .. import constants as c
from .. components import person, textbox, portal
from . import player_menu
from .. import tilerender
from .. import setup
import googletrans#구글 번역 API

#구글 번역 변수 translator.translate(문장, dest='ko').text 함수를 사용해 한글 문자열로 번역 가능
translator = googletrans.Translator()


#Python 2/3 compatibility.
if sys.version_info[0] == 2:
    range = xrange


class LevelState(tools._State):
    #해당 객체에 대한 인스턴스를 생성한다.
    def __init__(self, name, battles=False):
        super(LevelState, self).__init__()
        self.name = name
        self.tmx_map = setup.TMX[name]
        self.allow_battles = battles
        self.music_title = None
        self.previous_music = None
        self.music = None
        self.volume = None
        self.portal = None

    def startup(self, current_time, game_data):
        """
        Call when the State object is flipped to.
        상태 객체가 화면 전환일시 호출한다.
        """
        self.game_data = game_data
        self.music, self.volume = self.set_music()
        self.current_time = current_time
        self.state = 'transition_in'
        self.reset_dialogue = ()
        self.switch_to_battle = False
        self.use_portal = False
        self.allow_input = False
        self.cut_off_bottom_map = ['castle', 'town', 'dungeon']
        self.renderer = tilerender.Renderer(self.tmx_map)
        self.map_image = self.renderer.make_2x_map()

        self.viewport = self.make_viewport(self.map_image)
        self.level_surface = self.make_level_surface(self.map_image)
        self.level_rect = self.level_surface.get_rect()
        self.portals = self.make_level_portals()
        self.player = self.make_player()
        self.blockers = self.make_blockers()
        self.sprites = self.make_sprites()

        self.collision_handler = collision.CollisionHandler(self.player,
                                                            self.blockers,
                                                            self.sprites,
                                                            self.portals,
                                                            self)
        self.dialogue_handler = textbox.TextHandler(self)
        self.state_dict = self.make_state_dict()
        self.menu_screen = player_menu.Player_Menu(game_data, self)
        self.transition_rect = setup.SCREEN.get_rect()
        self.transition_alpha = 255

    def set_music(self):
        """
        Set music based on name.
        이름을 이용해 음악을 선택한다.
        """
        music_dict = {c.TOWN: ('town_theme', .4),
                      c.OVERWORLD: ('overworld', .4),
                      c.CASTLE: ('town_theme', .4),
                      c.DUNGEON: ('dungeon_theme', .4),
                      c.DUNGEON2: ('dungeon_theme', .4),
                      c.DUNGEON3: ('dungeon_theme', .4),
                      c.DUNGEON4: ('dungeon_theme', .4),
                      c.DUNGEON5: ('dungeon_theme', .4),
                      c.HOUSE: ('pleasant_creek', .1),
                      c.BROTHER_HOUSE: ('pleasant_creek', .1)}

        if self.game_data['crown quest'] and (self.name == c.TOWN or self.name == c.CASTLE):
            self.music_title = 'kings_theme'
            return setup.MUSIC['kings_theme'], .4
        elif self.name in music_dict:
            music = music_dict[self.name][0]
            volume = music_dict[self.name][1]
            self.music_title = music
            return setup.MUSIC[music], volume
        else:
            return None, None

    def make_viewport(self, map_image):
        """
        Create the viewport to view the level through.
        게임 화면을 그릴 창을 만든다.
        """
        map_rect = map_image.get_rect()
        return setup.SCREEN.get_rect(bottom=map_rect.bottom)

    def make_level_surface(self, map_image):
        """
        Create the surface all images are blitted to.
        지표면을 만들기 위한 이미지를 모두 만든다.
        """
        map_rect = map_image.get_rect()
        map_width = map_rect.width
        if self.name in self.cut_off_bottom_map:
            map_height = map_rect.height - 32
        else:
            map_height = map_rect.height
        size = map_width, map_height

        return pg.Surface(size).convert()

    def make_player(self):
        """
        Make the player and sets location.
        플레이어를 만들고 위치를 설정한다.
        """
        last_state = self.previous

        if last_state == 'battle':
            player = person.Player(self.game_data['last direction'], self.game_data)
            player.rect.x = self.game_data['last location'][0] * 32
            player.rect.y = self.game_data['last location'][1] * 32

        else:
            for object in self.renderer.tmx_data.getObjects():
                properties = object.__dict__
                if properties['name'] == 'start point':
                    if last_state == properties['state']:
                        posx = properties['x'] * 2
                        posy = (properties['y'] * 2) - 32
                        player = person.Player(properties['direction'],
                                               self.game_data)
                        player.rect.x = posx
                        player.rect.y = posy

        return player

    def make_blockers(self):
        """
        Make the blockers for the level.
        차단벽을 만든다.
        """
        blockers = []

        for object in self.renderer.tmx_data.getObjects():
            properties = object.__dict__
            if properties['name'] == 'blocker':
                left = properties['x'] * 2
                top = ((properties['y']) * 2) - 32
                blocker = pg.Rect(left, top, 32, 32)
                blockers.append(blocker)

        return blockers

    def make_sprites(self):
        """
        Make any sprites for the level as needed.
        각 지역에 필요한 스프라이트들을 만든다
        """
        sprites = pg.sprite.Group()

        for object in self.renderer.tmx_data.getObjects():
            properties = object.__dict__
            if properties['name'] == 'sprite':
                if 'direction' in properties:
                    direction = properties['direction']
                else:
                    direction = 'down'

                if properties['type'] == 'soldier' and direction == 'left':
                    index = 1
                else:
                    index = 0

                if 'item' in properties:
                    item = properties['item']
                else:
                    item = None

                if 'id' in properties:
                    id = properties['id']
                else:
                    id = None

                if 'battle' in properties:
                    battle = properties['battle']
                else:
                    battle = None

                if 'state' in properties:
                    sprite_state = properties['state']
                else:
                    sprite_state = None


                x = properties['x'] * 2
                y = ((properties['y']) * 2) - 32

                sprite_dict = {'oldman': person.Person('oldman',
                                                       x, y, direction),
                               'bluedressgirl': person.Person('femalevillager',
                                                              x, y, direction,
                                                              'resting', 1),
                               'femalewarrior': person.Person('femvillager2',
                                                              x, y, direction,
                                                              'autoresting'),
                               'devil': person.Person('devil', x, y,
                                                      'down', 'autoresting'),
                               'oldmanbrother': person.Person('oldmanbrother',
                                                              x, y, direction),
                               'soldier': person.Person('soldier',
                                                        x, y, direction,
                                                        'resting', index),
                               'king': person.Person('king', x, y, direction),
                               'evilwizard': person.Person('evilwizard', x, y, direction),
                               'treasurechest': person.Chest(x, y, id)}

                sprite = sprite_dict[properties['type']]
                if sprite_state:
                    sprite.state = sprite_state

                if sprite.name == 'oldman':
                    if self.game_data['old man gift'] and not self.game_data['elixir received']:
                        sprite.item = self.game_data['old man gift']
                    else:
                        sprite.item = item
                elif sprite.name == 'king':
                    if not self.game_data['talked to king']:
                        sprite.item = self.game_data['king item']
                else:
                    sprite.item = item
                sprite.battle = battle
                self.assign_dialogue(sprite, properties)
                self.check_for_opened_chest(sprite)
                if sprite.name == 'evilwizard' and self.game_data['crown quest']:
                    pass
                else:
                    sprites.add(sprite)

        return sprites

    def assign_dialogue(self, sprite, property_dict):
        """
        Assign dialogue from object property dictionaries in tmx maps to sprites.
        스프라이트(npc)와의 대화 내용을 설정한다.
        """
        dialogue_list = []
        for i in range(int(property_dict['dialogue length'])):
            dialogue_list.append(property_dict['dialogue'+str(i)])
            sprite.dialogue = dialogue_list

        if sprite.name == 'oldman':
            quest_in_process_dialogue = [translator.translate('Hurry to the NorthEast Shores!', dest='ko').text,
                                         translator.translate('I do not have much time left.', dest='ko').text]

            if self.game_data['has brother elixir']:
                if self.game_data['elixir received']:
                    sprite.dialogue = [translator.translate('My good health is thanks to you.', dest='ko').text,
                                       translator.translate('I will be forever in your debt.', dest='ko').text]
                else:
                    sprite.dialogue = [translator.translate('Thank you for reaching my brother.', dest='ko').text,
                                       translator.translate('This ELIXIR will cure my ailment.', dest='ko').text,
                                       translator.translate('As a reward, I will teach you a magic spell.', dest='ko').text,
                                       translator.translate('Use it wisely.', dest='ko').text,
                                       translator.translate('You learned FIRE BLAST.', dest='ko').text]

            elif self.game_data['talked to sick brother']:
                sprite.dialogue = quest_in_process_dialogue

            elif not self.game_data['talked to sick brother']:
                self.reset_dialogue = (sprite, quest_in_process_dialogue)
        elif sprite.name == 'oldmanbrother':
            if self.game_data['has brother elixir']:
                if self.game_data['elixir received']:
                    sprite.dialogue = [translator.translate('I am glad my brother is doing well.', dest='ko').text,
                                       translator.translate('You have a wise and generous spirit.', dest='ko').text]
                else:
                    sprite.dialogue = [translator.translate('Hurry! There is precious little time.', dest='ko').text]
            elif self.game_data[translator.translate('talked to sick brother', dest='ko').text]:
                sprite.dialogue = [translator.translate('My brother is sick?!?', dest='ko').text,
                                   translator.translate('I have not seen him in years.  I had no idea he was not well.', dest='ko').text,
                                   translator.translate('Quick, take this ELIXIR to him immediately.', dest='ko').text]
        elif sprite.name == 'king':
            retrieved_crown_dialogue = [translator.translate('My crown! You recovered my stolen crown!!!', dest='ko').text,
                                        translator.translate('I can not believe what I see before my eyes.', dest='ko').text,
                                        translator.translate('You are truly a brave and noble warrior.', dest='ko').text,
                                        translator.translate('Henceforth, I name thee Grand Protector of this Town!', dest='ko').text,
                                        translator.translate('You are the greatest warrior this world has ever known.', dest='ko').text]
            thank_you_dialogue = [translator.translate('Thank you for retrieving my crown.', dest='ko').text,
                                  translator.translate('My kingdom is forever in your debt.', dest='ko').text]

            if self.game_data['crown quest'] and not self.game_data['delivered crown']:
                sprite.dialogue = retrieved_crown_dialogue
                self.reset_dialogue = (sprite, thank_you_dialogue)
            elif self.game_data['delivered crown']:
                sprite.dialogue = thank_you_dialogue


    def check_for_opened_chest(self, sprite):
        #상자가 이미 연 상자인지 검사한다.
        if sprite.name == 'treasurechest':
            if not self.game_data['treasure{}'.format(sprite.id)]:
                sprite.dialogue = [translator.translate('Empty.', dest='ko').text]
                sprite.item = None
                sprite.index = 1

    def make_state_dict(self):
        """
        Make a dictionary of states the level can be in.
        상태 딕셔너리를 만든다.
        """
        state_dict = {'normal': self.running_normally,
                      'dialogue': self.handling_dialogue,
                      'menu': self.goto_menu,
                      'transition_in': self.transition_in,
                      'transition_out': self.transition_out,
                      'slow transition out': self.slow_fade_out}

        return state_dict

    def make_level_portals(self):
        """
        Make the portals to switch state.
        다른 지역으로 이동하는 포탈을 만든다.
        """
        portal_group = pg.sprite.Group()

        for object in self.renderer.tmx_data.getObjects():
            properties = object.__dict__
            if properties['name'] == 'portal':
                posx = properties['x'] * 2
                posy = (properties['y'] * 2) - 32
                new_state = properties['type']
                portal_group.add(portal.Portal(posx, posy, new_state))


        return portal_group

    def running_normally(self, surface, keys, current_time):
        """
        Update level normally.
        움직일 때 지역을 움직이게 한다.
        """
        self.check_for_dialogue()
        self.player.update(keys, current_time)
        self.sprites.update(current_time)
        self.collision_handler.update(keys, current_time)
        self.check_for_battle()
        self.check_for_portals()
        self.check_for_end_of_game()
        self.dialogue_handler.update(keys, current_time)
        self.check_for_menu(keys)
        self.viewport_update()
        self.draw_level(surface)

    def check_for_portals(self):
        """
        Check if the player walks into a door, requiring a level change.
        플레이어가 다른 지역으로 이동하는지 검사하고, 필요 시 지역을 바꾼다.
        """
        if self.use_portal and not self.done:
            self.player.location = self.player.get_tile_location()
            self.update_game_data()
            self.next = self.portal
            self.state = 'transition_out'

    def check_for_battle(self):
        """
        Check if the flag has been made true, indicating
        to switch state to a battle.
        전투가 일어나는 것을 검사하고 전투 상태로 전환한다.
        """
        if self.switch_to_battle and self.allow_battles and not self.done:
            self.player.location = self.player.get_tile_location()
            self.update_game_data()
            self.next = 'battle'
            self.state = 'transition_out'

    def check_for_menu(self, keys):
        """
        Check if player hits enter to go to menu.
        플레이어가 메뉴로 들어갔는지 검사한다.
        """
        if keys[pg.K_RETURN] and self.allow_input:
            if self.player.state == 'resting':
                self.state = 'menu'
                self.allow_input = False

        if not keys[pg.K_RETURN]:
            self.allow_input = True


    def update_game_data(self):
        """
        Update the persistant game data dictionary.
        지속적인 게임 데이터 딕셔너리를 검사한다.
        """
        self.game_data['last location'] = self.player.location
        self.game_data['last direction'] = self.player.direction
        self.game_data['last state'] = self.name
        self.set_new_start_pos()

    def check_for_end_of_game(self):
        """
        Switch scene to credits if main quest is complete.
        게임의 메인 퀘스트를 클리어 할 시 엔딩 크레딧으로 전환한다.
        """
        if self.game_data['delivered crown']:
            self.next = c.CREDITS
            self.state = 'slow transition out'

    def set_new_start_pos(self):
        """
        Set new start position based on previous state.
        이전 스테이지에 기반하여 새로운 시작지점을 설정한다.
        """
        location = copy.deepcopy(self.game_data['last location'])
        direction = self.game_data['last direction']

        if self.next == 'player menu':
            pass
        elif direction == 'up':
            location[1] += 1
        elif direction == 'down':
            location[1] -= 1
        elif direction == 'left':
            location[0] += 1
        elif direction == 'right':
            location[0] -= 1

    def handling_dialogue(self, surface, keys, current_time):
        """
        Update only dialogue boxes.
        대화 상자를 업데이트한다.
        """
        self.dialogue_handler.update(keys, current_time)
        self.draw_level(surface)

    def goto_menu(self, surface, keys, *args):
        """
        Go to menu screen.
        메뉴로 이동한다.
        """
        self.menu_screen.update(surface, keys)
        self.menu_screen.draw(surface)

    def check_for_dialogue(self):
        """
        Check if the level needs to freeze.
        대화 중 멈출 필요가 있을 시 멈추게 한다.
        """
        if self.dialogue_handler.textbox:
            self.state = 'dialogue'

    def transition_out(self, surface, *args):
        """
        Transition level to new scene.
         페이드 아웃 효과
        """
        transition_image = pg.Surface(self.transition_rect.size)
        transition_image.fill(c.TRANSITION_COLOR)
        transition_image.set_alpha(self.transition_alpha)
        self.draw_level(surface)
        surface.blit(transition_image, self.transition_rect)
        self.transition_alpha += c.TRANSITION_SPEED
        if self.transition_alpha >= 255:
            self.transition_alpha = 255
            self.done = True

    def slow_fade_out(self, surface, *args):
        """
        Transition level to new scene.
        느린 페이드 효과
        """
        transition_image = pg.Surface(self.transition_rect.size)
        transition_image.fill(c.TRANSITION_COLOR)
        transition_image.set_alpha(self.transition_alpha)
        self.draw_level(surface)
        surface.blit(transition_image, self.transition_rect)
        self.transition_alpha += 2
        if self.transition_alpha >= 255:
            self.transition_alpha = 255
            self.done = True

    def transition_in(self, surface, *args):
        """
        Transition into level.
        페이드 인 효과
        """
        self.viewport_update()
        transition_image = pg.Surface(self.transition_rect.size)
        transition_image.fill(c.TRANSITION_COLOR)
        transition_image.set_alpha(self.transition_alpha)
        self.draw_level(surface)
        surface.blit(transition_image, self.transition_rect)
        self.transition_alpha -= c.TRANSITION_SPEED 
        if self.transition_alpha <= 0:
            self.state = 'normal'
            self.transition_alpha = 0

    def update(self, surface, keys, current_time):
        """
        Update state.
        스테이지를 업데이트한다.
        """
        state_function = self.state_dict[self.state]
        state_function(surface, keys, current_time)

    def viewport_update(self):
        """
        Update viewport so it stays centered on character,
        unless at edge of map.
        화면을 업데이트한다.
        """
        self.viewport.center = self.player.rect.center
        self.viewport.clamp_ip(self.level_rect)

    def draw_level(self, surface):
        """
        Blit all images to screen.
        지역을 그린다.
        """
        self.level_surface.blit(self.map_image, self.viewport, self.viewport)
        self.level_surface.blit(self.player.image, self.player.rect)
        self.sprites.draw(self.level_surface)

        surface.blit(self.level_surface, (0, 0), self.viewport)
        self.dialogue_handler.draw(surface)
















