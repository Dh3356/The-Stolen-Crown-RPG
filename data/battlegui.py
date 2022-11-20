"""
GUI components for battle states.
전투 상태에 대한 GUI 구성 요소를 나타내는 파일
"""
import sys
import pygame as pg
from . import setup, observer
from . import constants as c

#Python 2/3 compatibility.
if sys.version_info[0] == 2:
    range = xrange

class InfoBox(object):
    """
    Info box that describes attack damage and other battle related information.
    공격 피해 및 기타 전투 관련 정보를 설명하는 클래스
    """
    def __init__(self, game_data, experience, gold):        # 게임 데이터, 경험치, 골드 받아오기
        self.game_data = game_data                          # 게임 데이터 저장
        self.enemy_damage = 0                               # 적의 피해 0 초기화
        self.player_damage = 0                              # 플레이어 피해 0        
        self.state = c.SELECT_ACTION
        self.title_font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)    # 제목 글씨체 폰트 설정
        self.title_font.set_underline(True)                             # 제목 글씨 밑줄 추가
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 18)          # 기본 글씨체는 제목 글씨체와 동일, 크기만 작음
        self.experience_points = experience                             # 받아온 경험치 저장
        self.gold_earned = gold                                         # 받아온 골드 저장
        self.state_dict = self.make_state_dict()                        # 상태창(사전) 만드는 함수 호출
        self.image = self.make_image()
        self.rect = self.image.get_rect(bottom=608)
        self.item_text_list = self.make_item_text()[1:]
        self.magic_text_list = self.make_magic_text()[1:]

    def make_state_dict(self):
        """
        Make dictionary of states Battle info can be in.
        전투 정보가 들어갈 수 있는 상태 사전을 만듭니다.
        """
        state_dict   = {c.SELECT_ACTION: 'Select an action.',
                        c.SELECT_MAGIC: 'Select a magic spell.',
                        c.SELECT_ITEM: 'Select an item.',
                        c.SELECT_ENEMY: 'Select an enemy.',
                        c.ENEMY_ATTACK: 'Enemy attacks player!',
                        c.PLAYER_ATTACK: 'Player attacks enemy! ',
                        c.RUN_AWAY: 'RUN AWAY!!!',
                        c.ENEMY_DAMAGED: self.enemy_damaged(),
                        c.ENEMY_DEAD: 'Enemy killed.',
                        c.PLAYER_DAMAGED: self.player_hit(),
                        c.DRINK_HEALING_POTION: 'Player healed.',
                        c.DRINK_ETHER_POTION: 'Magic Points Increased.',
                        c.FIRE_SPELL: 'FIRE BLAST!',
                        c.BATTLE_WON: 'Battle won!',
                        c.SHOW_EXPERIENCE: self.show_experience(),
                        c.LEVEL_UP: self.level_up(),
                        c.TWO_ACTIONS: 'Two actions per turn mode is now available.',
                        c.SHOW_GOLD: self.show_gold()}

        return state_dict

    def enemy_damaged(self):
        """
        Return text of enemy being hit using calculated damage.
        계산된 데미지를 사용하여 적에게 명중하는 텍스트를 반환
        """
        return "Enemy hit with {} damage.".format(self.enemy_damage)

    def make_item_text(self):
        """
        Make the text for when the player selects items.
        플레이어가 항목을 선택할 때 사용할 텍스트를 만듭니다
        """
        inventory = self.game_data['player inventory']  #사용자의 보관함 가져와 저장
        allowed_item_list = ['Healing Potion', 'Ether Potion']  
        title = 'SELECT ITEM'
        item_text_list = [title]

        for item in allowed_item_list:
            if item in inventory:
                text = item + ": " + str(inventory[item]['quantity'])
                item_text_list.append(text)

        item_text_list.append('BACK')

        return item_text_list

    def make_magic_text(self):
        """
        Make the text for when the player selects magic.
        플레이어가 마법을 선택할 때 사용할 텍스트를 만듭니다
        """
        inventory = self.game_data['player inventory']
        allowed_item_list = ['Fire Blast', 'Cure']
        title = 'SELECT MAGIC SPELL'
        magic_text_list = [title]
        spell_list = [item for item in inventory if item in allowed_item_list]
        magic_text_list.extend(spell_list)
        magic_text_list.append('BACK')

        return magic_text_list

    def make_text_sprites(self, text_list):
        """
        Make sprites out of text.
        텍스트로  스프라이트 만들기
        (여기서 sprite란 게임에서 나타내는 모든 캐릭터, 장애물등을 표현할 때 사용하는 Surface)
        (sprite 그룹을 만들어서 모두 한꺼번에 움직이게 하거나 Sprite들 끼리의 충돌을 알아낼 수 있다.)
        """
        sprite_group = pg.sprite.Group()

        for i, text in enumerate(text_list):    # enumerate는 입력받은 list를 열거하는 함수(0부터 index와 함께)
            sprite = pg.sprite.Sprite()

            if i == 0:  # index가 0일때(첫번째 배열일 때)
                x = 195
                y = 10
                surface = self.title_font.render(text, True, c.NEAR_BLACK)
                rect = surface.get_rect(x=x, y=y)
            else:       # 첫번째가 아닐 때
                x = 100
                y = (i * 30) + 20
                surface = self.font.render(text, True, c.NEAR_BLACK)
                rect = surface.get_rect(x=x, y=y)
            sprite.image = surface
            sprite.rect = rect
            sprite_group.add(sprite)

        return sprite_group

    def make_image(self):
        """
        Make image out of box and message.
        상자와 메시지로 이미지를 만듭니다.
        """
        image = setup.GFX['shopbox']        # 상자 외형 설정
        rect = image.get_rect(bottom=608)
        surface = pg.Surface(rect.size)
        surface.set_colorkey(c.BLACK)
        surface.blit(image, (0, 0))

        if self.state == c.SELECT_ITEM:     # 상태에서 item을 골랐을 때
            text_sprites = self.make_text_sprites(self.make_item_text())
            text_sprites.draw(surface)
        elif self.state == c.SELECT_MAGIC:  # 상태에서 magic을 골랐을 때
            text_sprites = self.make_text_sprites(self.make_magic_text())
            text_sprites.draw(surface)
        else:                               # 
            text_surface = self.font.render(self.state_dict[self.state], True, c.NEAR_BLACK)
            text_rect = text_surface.get_rect(x=50, y=50)
            surface.blit(text_surface, text_rect)

        return surface

    def set_enemy_damage(self, enemy_damage):
        """
        Set enemy damage in state dictionary.
        상태창에 적의 피해를 설정합니다.
        """
        self.enemy_damage = enemy_damage
        self.state_dict[c.ENEMY_DAMAGED] = self.enemy_damaged()

    def set_player_damage(self, player_damage):
        """
        Set player damage in state dictionary.
        상태창에 플레이어의 피해를 설정합니다.
        """
        self.player_damage = player_damage
        self.state_dict[c.PLAYER_DAMAGED] = self.player_hit()

    # 플레이어가 공격을 받았을 때
    def player_hit(self):
        if self.player_damage:  # 공격 성공시
            return "Player hit with {} damage".format(self.player_damage)
        else:                   # 공격 실패시
            return "Enemy missed!"

    def update(self):
        """
        Updates info box
        정보 창 업데이트
        """
        self.image = self.make_image()

    def show_experience(self):
        """
        Show how much experience the player earned.
        플레이어가 배틀에서 얻은 경험치 반환
        """
        return "You earned {} experience points this battle!".format(self.experience_points)

    def show_gold(self):
        """
        Show how much gold the player earned.
        플레이어가 배틀에서 얻은 골드 반환
        """
        return "You found {} gold.".format(self.gold_earned)

    def level_up(self):
        """
        Return message indicating a level up for player.
        플레이어의 레벨없을 나타내는 메시지 반환
        """
        return "You leveled up to Level {}!".format(self.game_data['player stats']['Level'])

    # 레벨 업 메시지 상태창에 저장
    def reset_level_up_message(self):
        self.state_dict[c.LEVEL_UP] = self.level_up()



class SelectBox(object):
    """
    Box to select whether to attack, use item, use magic or run away.
    공격할지, 아이템을 사용할지, 마법을 사용할지, 도망칠지 선택하는 상자
    """
    def __init__(self):
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.slots = self.make_slots()
        self.image = self.make_image()
        self.rect = self.image.get_rect(bottom=608,
                                        right=800)

    def make_image(self):
        """
        Make the box image for
        상자 이미지 만들기
        """
        image = setup.GFX['goldbox']
        rect = image.get_rect(bottom=608)
        surface = pg.Surface(rect.size)
        surface.set_colorkey(c.BLACK)
        surface.blit(image, (0, 0))

        for text in self.slots: #slot들 안에 있는 text들 반복문 (공격, 아이템, 마법, 도망)
            text_surface = self.font.render(text, True, c.NEAR_BLACK)
            text_rect = text_surface.get_rect(x=self.slots[text]['x'],
                                              y=self.slots[text]['y'])
            surface.blit(text_surface, text_rect)   

        return surface

    def make_slots(self):
        """
        Make the slots that hold the text selections, and locations.
        텍스트 선택 항목과 위치가 들어 있느 슬롯을 만듭니다.
        """
        slot_dict = {}
        selections = ['Attack', 'Items', 'Magic', 'Run']

        for i, text in enumerate(selections): # 각 선택지들의 위치 설정
            slot_dict[text] = {'x': 150,
                               'y': (i*34)+10}  # y축 아래로 열거

        return slot_dict


class SelectArrow(object):
    """
    Small arrow for menu
    메뉴의 작은 화살표 (선택할 때 사용)
    """
    def __init__(self, enemy_pos_list, info_box):
        self.info_box = info_box
        self.image = setup.GFX['smallarrow']
        self.rect = self.image.get_rect()
        self.state = 'select action'
        self.state_dict = self.make_state_dict()
        self.pos_list = self.make_select_action_pos_list()
        self.index = 0
        self.rect.topleft = self.pos_list[self.index]
        self.allow_input = False
        self.enemy_pos_list = enemy_pos_list
        self.observers = [observer.SoundEffects()]

    def notify(self, event):
        """
        Notify all observers of events.
        모든 관찰자에게 이벤트를 알림
        """
        for observer in self.observers:
            observer.on_notify(event)

    def make_state_dict(self):
        """
        Make state dictionary
        상태창 사전 만들기
        """
        state_dict = {'select action': self.select_action,
                      'select enemy': self.select_enemy,
                      'select item': self.select_item,
                      'select magic': self.select_magic,
                      'invisible': self.become_invisible_surface}

        return state_dict

    def select_action(self, keys):
        """
        Select what action the player should take.
        플레이어가 수행할 작업 선택
        """
        self.pos_list = self.make_select_action_pos_list()
        if self.index > (len(self.pos_list) - 1):   # 마지막 index를 넘어갈 때
            print (self.pos_list, self.index)
        self.rect.topleft = self.pos_list[self.index]

        self.check_input(keys)

    def make_select_action_pos_list(self):
        """
        Make the list of positions the arrow can be in.
        화살표가 위치할 수 있는 위치 목록을 만듭니다.
        """
        pos_list = []

        for i in range(4):
            x = 590
            y = (i * 34) + 472
            pos_list.append((x, y))

        return pos_list

    def select_enemy(self, keys):
        """
        Select what enemy you want to take action on.
        수행할 적을 선택합니다.
        """
        self.pos_list = self.enemy_pos_list

        if self.pos_list:
            pos = self.pos_list[self.index]
            self.rect.x = pos[0] - 60
            self.rect.y = pos[1] + 20

        self.check_input(keys)

    # 체크 입력
    def check_input(self, keys):
        if self.allow_input:
            if keys[pg.K_DOWN] and self.index < (len(self.pos_list) - 1):   # 방향키 아래고 마지막 index가 아닐 때
                self.notify(c.CLICK)
                self.index += 1
                self.allow_input = False    # 체크표시 초기화
            elif keys[pg.K_UP] and self.index > 0:      # 방향키 위고 첫번째 index가 아닐 떄
                self.notify(c.CLICK)
                self.index -= 1
                self.allow_input = False    # 체크표시 초기화


        if keys[pg.K_DOWN] == False and keys[pg.K_UP] == False \
                and keys[pg.K_RIGHT] == False and keys[pg.K_LEFT] == False:
            self.allow_input = True

    def select_item(self, keys):
        """
        Select item to use.
        사용할 아이템 선택
        """
        self.pos_list = self.make_select_item_pos_list()

        pos = self.pos_list[self.index]
        self.rect.x = pos[0] - 60
        self.rect.y = pos[1] + 20

        self.check_input(keys)

    def make_select_item_pos_list(self):
        """
        Make the coordinates for the arrow for the item select screen.
        아이템 항목 선택 화면의 화살표 좌표를 만듭니다
        """
        pos_list = []
        text_list = self.info_box.make_item_text()
        text_list = text_list[1:]

        for i in range(len(text_list)):
            left = 90
            top = (i * 29) + 488
            pos_list.append((left, top))

        return pos_list

    def select_magic(self, keys):
        """
        Select magic to use.
        사용할 마법을 선택합니다.
        """
        self.pos_list = self.make_select_magic_pos_list()

        pos = self.pos_list[self.index]
        self.rect.x = pos[0] - 60
        self.rect.y = pos[1] + 20

        self.check_input(keys)

    def make_select_magic_pos_list(self):
        """
        Make the coordinates for the arrow for the magic select screen.
        Magic Select 화면의 화살표 좌표를 만듭니다.
        """
        pos_list = []
        text_list = self.info_box.make_magic_text()
        text_list = text_list[1:]

        for i in range(len(text_list)):
            left = 90
            top = (i * 29) + 488
            pos_list.append((left, top))

        return pos_list


    def become_invisible_surface(self, *args):
        """
        Make image attribute an invisible surface.
        이미지 속성을 보이지 않는 표면으로 만듭니다
        """
        self.image = pg.Surface(self.rect.size)
        self.image.set_colorkey(c.BLACK)

    # 선택된 아이템으로 만들기
    def become_select_item_state(self):
        self.index = 0
        self.state = c.SELECT_ITEM

    # 선택된 마법으로 만들기
    def become_select_magic_state(self):
        self.index = 0
        self.state = c.SELECT_MAGIC

    def enter_select_action(self):
        """
        Assign values for the select action state.
        선택한 활동(공격,마법 등) 상태에 대한 값을 할당합니다.
        """
        pass

    def enter_select_enemy(self):
        """
        Assign values for the select enemy state.
        공격하려고 선택한 적 상태에 대한 값 할당
        """
        pass

    def update(self, keys):
        """
        Update arrow position.
        화살표 위치 업데이트
        """
        self.image = setup.GFX['smallarrow']
        state_function = self.state_dict[self.state]
        state_function(keys)

    def draw(self, surface):
        """
        Draw to surface.
        표면(배경) 그리기
        """
        surface.blit(self.image, self.rect)
    
    # 
    def remove_pos(self, enemy):
        enemy_list = self.enemy_pos_list
        enemy_pos = list(enemy.rect.topleft)

        self.enemy_pos_list = [pos for pos in enemy_list if pos != enemy_pos]


class PlayerHealth(object):
    """
    Basic health meter for player.
    플레이어의 기본 체력 측정기입니다.
    """
    def __init__(self, select_box_rect, game_data):
        self.health_stats = game_data['player stats']['health']
        self.magic_stats = game_data['player stats']['magic']
        self.title_font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.posx = select_box_rect.centerx
        self.posy = select_box_rect.y - 5

    @property
    def image(self):
        """
        Make the image surface for the player
        플레이어의 이미지 표면 만들기
        """
        current_health = str(self.health_stats['current'])
        max_health = str(self.health_stats['maximum'])
        if len(current_health) == 2:
            buffer = '  '
        elif len(current_health) == 1:
            buffer = '    '
        else:
            buffer = ''
        health_string = "Health: {}{}/{}".format(buffer, current_health, max_health)
        health_surface =  self.title_font.render(health_string, True, c.NEAR_BLACK)
        health_rect = health_surface.get_rect(x=20, y=9)

        current_magic = str(self.magic_stats['current'])
        if len(current_magic) == 2:
            buffer = '  '
        elif len(current_magic) == 1:
            buffer = '    '
        else:
            buffer = ''
        max_magic = str(self.magic_stats['maximum'])
        magic_string = "Magic:  {}{}/{}".format(buffer, current_magic, max_magic)
        magic_surface = self.title_font.render(magic_string, True, c.NEAR_BLACK)
        magic_rect = magic_surface.get_rect(x=20, top=health_rect.bottom)

        box_surface = setup.GFX['battlestatbox']
        box_rect = box_surface.get_rect()

        parent_surface = pg.Surface(box_rect.size)
        parent_surface.blit(box_surface, box_rect)
        parent_surface.blit(health_surface, health_rect)
        parent_surface.blit(magic_surface, magic_rect)

        return parent_surface

    @property
    def rect(self):
        """
        Make the rect object for image surface.
        이미지에 적합한 둥금 정도를 가진 객체 만들기
        """
        return self.image.get_rect(centerx=self.posx, bottom=self.posy)

    def draw(self, surface):
        """
        Draw health to surface.
        체력을 화면에 그리기
        """
        surface.blit(self.image, self.rect)
