from __future__ import division
import itertools
import math, random, copy, sys
import pygame as pg
from data import setup, observer
from data import constants as c

#Python 2/3 compatibility.
if sys.version_info[0] == 2:
    range = xrange

#게임에 등장하는 모든 ai캐릭터들을 컨트롤하기 위한 클래스(pg.sprite.Sprite 상속)
class Person(pg.sprite.Sprite):
    """Base class for all world characters
    controlled by the computer"""

    #객체 멤버변수 초기화
    def __init__(self, sheet_key, x, y, direction='down', state='resting', index=0):
        super(Person, self).__init__()
        self.alpha = 255
        self.name = sheet_key
        self.get_image = setup.tools.get_image
        self.spritesheet_dict = self.create_spritesheet_dict(sheet_key)
        self.animation_dict = self.create_animation_dict()
        self.index = index
        self.direction = direction
        self.image_list = self.animation_dict[self.direction]
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect(left=x, top=y)
        self.origin_pos = self.rect.topleft
        self.state_dict = self.create_state_dict()
        self.vector_dict = self.create_vector_dict()
        self.x_vel = 0
        self.y_vel = 0
        self.timer = 0.0
        self.move_timer = 0.0
        self.current_time = 0.0
        self.state = state
        self.blockers = self.set_blockers()
        self.location = self.get_tile_location()
        self.dialogue = ['Location: ' + str(self.location)]
        self.default_direction = direction
        self.item = None
        self.wander_box = self.make_wander_box()
        self.observers = [observer.SoundEffects()]
        self.health = 0
        self.death_image = pg.transform.scale2x(self.image)
        self.battle = None

    #sprite sheet에서 필요한 이미지들을 모아둔 딕셔너리 생성하여 반환
    def create_spritesheet_dict(self, sheet_key):
        """
        Make a dictionary of images from sprite sheet.
        """
        image_list = []
        image_dict = {}
        sheet = setup.GFX[sheet_key]
    
        image_keys = ['facing up 1', 'facing up 2',
                      'facing down 1', 'facing down 2',
                      'facing left 1', 'facing left 2',
                      'facing right 1', 'facing right 2']
    
        for row in range(2):
            for column in range(4):
                image_list.append(
                    self.get_image(column*32, row*32, 32, 32, sheet))
    
        for key, image in izip(image_keys, image_list):
            image_dict[key] = image
    
        return image_dict

    #걷는 애니메이션 구현에 필요한 이미지 리스트의 딕셔너리를 구현하여 반환
    #좌,우,위,아래 방향 이미지들을 각각 2개씩 가짐(걷는 모션 구현)
    def create_animation_dict(self):
        """
        Return a dictionary of image lists for animation.
        """
        image_dict = self.spritesheet_dict

        left_list = [image_dict['facing left 1'], image_dict['facing left 2']]
        right_list = [image_dict['facing right 1'], image_dict['facing right 2']]
        up_list = [image_dict['facing up 1'], image_dict['facing up 2']]
        down_list = [image_dict['facing down 1'], image_dict['facing down 2']]

        direction_dict = {'left': left_list,
                          'right': right_list,
                          'up': up_list,
                          'down': down_list}

        return direction_dict

    #모든 상태 메소드들을 모아놓은 딕셔너리 구현(resting(대기),moving(이동),animated resting(),...)
    def create_state_dict(self):
        """
        Return a dictionary of all state methods.
        """
        state_dict = {'resting': self.resting,
                      'moving': self.moving,
                      'animated resting': self.animated_resting,
                      'autoresting': self.auto_resting,
                      'automoving': self.auto_moving,
                      'battle resting': self.battle_resting,
                      'attack': self.attack,
                      'enemy attack': self.enemy_attack,
                      c.RUN_AWAY: self.run_away,
                      c.VICTORY_DANCE: self.victory_dance,
                      c.KNOCK_BACK: self.knock_back,
                      c.FADE_DEATH: self.fade_death}

        return state_dict

    #이동 시 필요한 각 방향의 벡터값을 저장한 딕셔너리 구현
    def create_vector_dict(self):
        """
        Return a dictionary of x and y velocities set to
        direction keys.
        """
        vector_dict = {'up': (0, -1),
                       'down': (0, 1),
                       'left': (-1, 0),
                       'right': (1, 0)}

        return vector_dict

    #sprite를 현재 상태를 참조하여 업데이트하는 메소드
    def update(self, current_time, *args):
        """
        Update sprite.
        """
        self.blockers = self.set_blockers()
        self.current_time = current_time
        self.image_list = self.animation_dict[self.direction]
        state_function = self.state_dict[self.state]
        state_function()
        self.location = self.get_tile_location()

    #스프라이트들(캐릭터들)끼리의 충돌을 막기 위하여 각 캐릭터들의 현재 rect의 위치를 저장하는 메소드
    def set_blockers(self):
        """
        Sets blockers to prevent collision with other sprites.
        """
        blockers = []

        if self.state == 'resting' or self.state == 'autoresting':
            blockers.append(pg.Rect(self.rect.x, self.rect.y, 32, 32))

        elif self.state == 'moving' or self.state == 'automoving':
            if self.rect.x % 32 == 0:
                tile_float = self.rect.y / float(32)
                tile1 = (self.rect.x, math.ceil(tile_float)*32)
                tile2 = (self.rect.x, math.floor(tile_float)*32)
                tile_rect1 = pg.Rect(tile1[0], tile1[1], 32, 32)
                tile_rect2 = pg.Rect(tile2[0], tile2[1], 32, 32)
                blockers.extend([tile_rect1, tile_rect2])

            elif self.rect.y % 32 == 0:
                tile_float = self.rect.x / float(32)
                tile1 = (math.ceil(tile_float)*32, self.rect.y)
                tile2 = (math.floor(tile_float)*32, self.rect.y)
                tile_rect1 = pg.Rect(tile1[0], tile1[1], 32, 32)
                tile_rect2 = pg.Rect(tile2[0], tile2[1], 32, 32)
                blockers.extend([tile_rect1, tile_rect2])

        return blockers

    #캐릭터의 위치를 pygame의 rect값에서 게임 내의 타일의 위치로 변환해주는 메소드
    def get_tile_location(self):
        """
        Convert pygame coordinates into tile coordinates.
        """
        if self.rect.x == 0:
            tile_x = 0
        elif self.rect.x % 32 == 0:
            tile_x = (self.rect.x / 32)
        else:
            tile_x = 0

        if self.rect.y == 0:
            tile_y = 0
        elif self.rect.y % 32 == 0:
            tile_y = (self.rect.y / 32)
        else:
            tile_y = 0

        return [tile_x, tile_y]

    #스프라이트(ai캐릭터)의 이동반경을 제한할 때 사용하는 클래스
    def make_wander_box(self):
        """
        Make a list of rects that surround the initial location
        of a sprite to limit his/her wandering.
        """
        x = int(self.location[0])
        y = int(self.location[1])
        box_list = []
        box_rects = []

        for i in range(x-3, x+4):
            box_list.append([i, y-3])
            box_list.append([i, y+3])

        for i in range(y-2, y+3):
            box_list.append([x-3, i])
            box_list.append([x+3, i])

        for box in box_list:
            left = box[0]*32
            top = box[1]*32
            box_rects.append(pg.Rect(left, top, 32, 32))

        return box_rects

    #player가 타일들 사이에서 움직이지 않을 때 타일의 중앙으로 이동(correct_Position 호출) 시켜주는 메소드
    def resting(self):
        """
        When the Person is not moving between tiles.
        Checks if the player is centered on a tile.
        """
        self.image = self.image_list[self.index]

        if self.rect.y % 32 != 0:
            self.correct_position(self.rect.y)
        if self.rect.x % 32 != 0:
            self.correct_position(self.rect.x)

    #animation함수를 호출하고, 스프라이트가 타일의 가운데에 있는지 확인하여 아니면 예외 출력 
    def moving(self):
        """
        Increment index and set self.image for animation.
        """
        self.animation()
        assert(self.rect.x % 32 == 0 or self.rect.y % 32 == 0), \
            'Not centered on tile'

    #ai캐릭터가 이동 후 멈출 때 이용하는 메소드(frequency 값을 500으로 주어 animation 함수 호출)
    def animated_resting(self):
        self.animation(500)

    #캐릭터의 움직임 애니메이션 표현에 필요한 메소드(index값 +1, 애니메이션이 끝나면 0으로 초기화)
    def animation(self, freq=100):
        """
        Adjust sprite image frame based on timer.
        """
        if (self.current_time - self.timer) > freq:
            if self.index < (len(self.image_list) - 1):
                self.index += 1
            else:
                self.index = 0
            self.timer = self.current_time

        self.image = self.image_list[self.index]

    #player을 'moving'(움직이는)상태로 변경해주는 메소드
    def begin_moving(self, direction):
        """
        Transition the player into the 'moving' state.
        """
        self.direction = direction
        self.image_list = self.animation_dict[direction]
        self.timer = self.current_time
        self.move_timer = self.current_time
        self.state = 'moving'

        if self.rect.x % 32 == 0:
            self.y_vel = self.vector_dict[self.direction][1]
        if self.rect.y % 32 == 0:
            self.x_vel = self.vector_dict[self.direction][0]

    #player을 resting(대기)상태로 변경해주는 메소드
    def begin_resting(self):
        """
        Transition the player into the 'resting' state.
        """
        self.state = 'resting'
        self.index = 1
        self.x_vel = self.y_vel = 0

    #ai캐릭터를 'auto moving'(자동 움직임)상태로 변경해주는 메소드
    def begin_auto_moving(self, direction):
        """
        Transition sprite to a automatic moving state.
        """
        self.direction = direction
        self.image_list = self.animation_dict[direction]
        self.state = 'automoving'
        self.x_vel = self.vector_dict[direction][0]
        self.y_vel = self.vector_dict[direction][1]
        self.move_timer = self.current_time

    #ai캐릭터를 'autoresting'(자동 대기)상태로 만들어주는 메소드
    def begin_auto_resting(self):
        """
        Transition sprite to an automatic resting state.
        """
        self.state = 'autoresting'
        self.index = 1
        self.x_vel = self.y_vel = 0
        self.move_timer = self.current_time

    #ai캐릭터를 대기 상태에서 움직임 상태로 바꿔줄 때 랜덤 방향과 타이밍을 결정해주는 메소드
    def auto_resting(self):
        """
        Determine when to move a sprite from resting to moving in a random
        direction.
        """
        self.image_list = self.animation_dict[self.direction]
        self.image = self.image_list[self.index]

        if self.rect.y % 32 != 0:
            self.correct_position(self.rect.y)
        if self.rect.x % 32 != 0:
            self.correct_position(self.rect.x)

        if (self.current_time - self.move_timer) > 2000:
            direction_list = ['up', 'down', 'left', 'right']
            random.shuffle(direction_list)
            direction = direction_list[0]
            self.begin_auto_moving(direction)
            self.move_timer = self.current_time

    #캐릭터의 위치를 타일의 중앙으로 옮겨주는 메소드
    def correct_position(self, rect_pos):
        """
        Adjust sprite position to be centered on tile.
        """
        diff = rect_pos % 32
        if diff <= 16:
            rect_pos - diff
        else:
            rect_pos + diff
 
    #player가 배틀 중 어택시를 제외한 대기상태를 나타내는 메소드(내용 x) 
    def battle_resting(self):
        """
        Player stays still during battle state unless he attacks.
        """
        pass
    
    #player를 attack_state(공격 상태)로 바꿔주는 메소드.
    def enter_attack_state(self, enemy):
        """
        Set values for attack state.
        """
        self.notify(c.SWORD)
        self.attacked_enemy = enemy
        self.x_vel = -5
        self.state = 'attack'


    #player가 'attack'선택 시 공격 애니메이션을 구현하는 메소드(앞으로 5, 뒤로 5)
    def attack(self):
        """
        Player does an attack animation.
        """
        FAST_FORWARD = -5
        FAST_BACK = 5

        self.rect.x += self.x_vel

        if self.x_vel == FAST_FORWARD:
            self.image = self.spritesheet_dict['facing left 1']
            self.image = pg.transform.scale2x(self.image)
            if self.rect.x <= self.origin_pos[0] - 110:
                self.x_vel = FAST_BACK
                self.notify(c.ENEMY_DAMAGED)
        else:
            if self.rect.x >= self.origin_pos[0]:
                self.rect.x = self.origin_pos[0]
                self.x_vel = 0
                self.state = 'battle resting'
                self.image = self.spritesheet_dict['facing left 2']
                self.image = pg.transform.scale2x(self.image)
                self.notify(c.PLAYER_FINISHED_ATTACK)

    #적(ai캐릭터)를 attack_state(공격 상태)로 바꿔주는 메소드
    def enter_enemy_attack_state(self):
        """
        Set values for enemy attack state.
        """
        self.x_vel = -5
        self.state = 'enemy attack'
        self.origin_pos = self.rect.topleft
        self.move_counter = 0

    #적의 공격 애니메이션을 구현하는 메소드.(player의 반대)
    def enemy_attack(self):
        """
        Enemy does an attack animation.
        """
        FAST_LEFT = -5
        FAST_RIGHT = 5
        STARTX = self.origin_pos[0]

        self.rect.x += self.x_vel

        if self.move_counter == 3:
            self.x_vel = 0
            self.state = 'battle resting'
            self.rect.x = STARTX
            self.notify(c.PLAYER_DAMAGED)

        elif self.x_vel == FAST_LEFT:
            if self.rect.x <= (STARTX - 15):
                self.x_vel = FAST_RIGHT
        elif self.x_vel == FAST_RIGHT:
            if self.rect.x >= (STARTX + 15):
                self.move_counter += 1
                self.x_vel = FAST_LEFT

    #ai캐릭터의 움직임을 실행(animation() 호출)하고 잘 멈췄는지 확인하는 메소드(타일의 중앙에 있는지)
    def auto_moving(self):
        """
        Animate sprite and check to stop.
        """
        self.animation()

        assert(self.rect.x % 32 == 0 or self.rect.y % 32 == 0), \
            'Not centered on tile'

    #모든 observer들에게 이벤트(피격,이동 등)를 전달하는 함수
    def notify(self, event):
        """
        Notify all observers of events.
        """
        for observer in self.observers:
            observer.on_notify(event)

    #피격의 데미지를 attack stats를 참조하여 계산하는 메소드.(최소 0 ~ 최대 (대상의 레벨*5 - 방어구 수치))
    def calculate_hit(self, armor_list, inventory):
        """
        Calculate hit strength based on attack stats.
        """
        armor_power = 0
        for armor in armor_list:
            armor_power += inventory[armor]['power']
        max_strength = max(1, (self.level * 5) - armor_power)
        min_strength = 0
        return random.randint(min_strength, max_strength)

    #전투에서 run 선택 시 전투에서 벗어나는 상태로 전환해주는 메소드
    def run_away(self):
        """
        Run away from battle state.
        """
        X_VEL = 5
        self.rect.x += X_VEL
        self.direction = 'right'
        self.small_image_list = self.animation_dict[self.direction]
        self.image_list = []
        for image in self.small_image_list:
            self.image_list.append(pg.transform.scale2x(image))
        self.animation()

    #player가 전투 승리 시 춤을 추는 상태로 전환해주는 메소드
    def victory_dance(self):
        """
        Post Victory Dance.
        """
        self.small_image_list = self.animation_dict[self.direction]
        self.image_list = []
        for image in self.small_image_list:
            self.image_list.append(pg.transform.scale2x(image))
        self.animation(500)

    #대상이 피격 시 뒤로 넉백되는 애니메이션 구현하는 메소드(앞으로 -2만큼 이동 후 원위치)
    def knock_back(self):
        """
        Knock back when hit.
        """
        FORWARD_VEL = -2

        self.rect.x += self.x_vel

        if self.name == 'player':
            if self.rect.x >= (self.origin_pos[0] + 10):
                self.x_vel = FORWARD_VEL
            elif self.rect.x <= self.origin_pos[0]:
                self.rect.x = self.origin_pos[0]
                self.state = 'battle resting'
                self.x_vel = 0
        else:
            if self.rect.x <= (self.origin_pos[0] - 10):
                self.x_vel = 2
            elif self.rect.x >= self.origin_pos[0]:
                self.rect.x = self.origin_pos[0]
                self.state = 'battle resting'
                self.x_vel = 0

    #캐릭터가 사망 시 투명하게 만드는 애니메이션을 구현한 메소드(alpha값을 8씩 감소시키며 0 이하가 되면 제거(kill 호출))
    def fade_death(self):
        """
        Make character become transparent in death.
        """
        self.image = pg.Surface((64, 64)).convert()
        self.image.set_colorkey(c.BLACK)
        self.image.set_alpha(self.alpha)
        self.image.blit(self.death_image, (0, 0))
        self.alpha -= 8
        if self.alpha <= 0:
            self.kill()
            self.notify(c.ENEMY_DEAD)


    #캐릭터가 피격 시 넉백 상태로 전환해주는 메소드(사망 시 x)(player일 시 앞으로 4만큼, 적이라면 -4만큼 이동 후 원위치)
    def enter_knock_back_state(self):
        """
        Set values for entry to knock back state.
        """
        if self.name == 'player':
            self.x_vel = 4
        else:
            self.x_vel = -4

        self.state = c.KNOCK_BACK
        self.origin_pos = self.rect.topleft

#player(주인공)을 컨트롤하기 위한 클래스(Person 클래스 상속)
class Player(Person):
    """
    User controlled character.
    """

    #객체 멤버변수 초기화()
    def __init__(self, direction, game_data, x=0, y=0, state='resting', index=0):
        super(Player, self).__init__('player', x, y, direction, state, index)
        self.damaged = False
        self.healing = False
        self.damage_alpha = 0
        self.healing_alpha = 0
        self.fade_in = True
        self.game_data = game_data
        self.index = 1
        self.image = self.image_list[self.index]

    #플레이어의 레벨값을 game_data에서 호출하여 반환해주는 메소드
    @property
    def level(self):
        """
        Make level property equal to player level in game_data.
        """
        return self.game_data['player stats']['Level']


    #플레이어의 이동에 필요한 벡터값을 구현하는 메소드(플레이어는 2칸 씩 이동)
    def create_vector_dict(self):
        """Return a dictionary of x and y velocities set to
        direction keys."""
        vector_dict = {'up': (0, -2),
                       'down': (0, 2),
                       'left': (-2, 0),
                       'right': (2, 0)}

        return vector_dict

    #player의 행동을 지정해주는 메소드
    def update(self, keys, current_time):
        """Updates player behavior"""
        self.current_time = current_time
        self.damage_animation()
        self.healing_animation()
        self.blockers = self.set_blockers()
        self.keys = keys
        self.check_for_input()
        state_function = self.state_dict[self.state]
        state_function()
        self.location = self.get_tile_location()

    #player가 피격 시 붉게 변하는 애니메이션을 구현한 메소드
    def damage_animation(self):
        """
        Put a red overlay over sprite to indicate damage.
        """
        if self.damaged:
            self.image = copy.copy(self.spritesheet_dict['facing left 2'])
            self.image = pg.transform.scale2x(self.image).convert_alpha()
            damage_image = copy.copy(self.image).convert_alpha()
            damage_image.fill((255, 0, 0, self.damage_alpha), special_flags=pg.BLEND_RGBA_MULT)
            self.image.blit(damage_image, (0, 0))
            if self.fade_in:
                self.damage_alpha += 25
                if self.damage_alpha >= 255:
                    self.fade_in = False
                    self.damage_alpha = 255
            elif not self.fade_in:
                self.damage_alpha -= 25
                if self.damage_alpha <= 0:
                    self.damage_alpha = 0
                    self.damaged = False
                    self.fade_in = True
                    self.image = self.spritesheet_dict['facing left 2']
                    self.image = pg.transform.scale2x(self.image)

    #player가 힐링포션 사용 시 초록색으로 변하는 애니메이션을 구현한 메소드
    def healing_animation(self):
        """
        Put a green overlay over sprite to indicate healing.
        """
        if self.healing:
            self.image = copy.copy(self.spritesheet_dict['facing left 2'])
            self.image = pg.transform.scale2x(self.image).convert_alpha()
            healing_image = copy.copy(self.image).convert_alpha()
            healing_image.fill((0, 255, 0, self.healing_alpha), special_flags=pg.BLEND_RGBA_MULT)
            self.image.blit(healing_image, (0, 0))
            if self.fade_in:
                self.healing_alpha += 25
                if self.healing_alpha >= 255:
                    self.fade_in = False
                    self.healing_alpha = 255
            elif not self.fade_in:
                self.healing_alpha -= 25
                if self.healing_alpha <= 0:
                    self.healing_alpha = 0
                    self.healing = False
                    self.fade_in = True
                    self.image = self.spritesheet_dict['facing left 2']
                    self.image = pg.transform.scale2x(self.image)

    #player가 대기 상태일 때 사용자의 입력을 받는 메소드(위 키, 아래 키, 왼쪽 키, 오른쪽 키)
    def check_for_input(self):
        """Checks for player input"""
        if self.state == 'resting':
            if self.keys[pg.K_UP]:
                self.begin_moving('up')
            elif self.keys[pg.K_DOWN]:
                self.begin_moving('down')
            elif self.keys[pg.K_LEFT]:
                self.begin_moving('left')
            elif self.keys[pg.K_RIGHT]:
                self.begin_moving('right')

    #player가 공격 시 데미지를 game_data의 weapon 키들을 참조하여 계산하여 반환하는 메소드(최대 착용 중인 무기의 power ~ 최소 최대값의 -7)
    def calculate_hit(self):
        """
        Calculate hit strength based on attack stats.
        """
        weapon = self.game_data['player inventory']['equipped weapon']
        weapon_power = self.game_data['player inventory'][weapon]['power']
        max_strength = weapon_power 
        min_strength = max_strength - 7
        return random.randint(min_strength, max_strength)

#적의 행동을 제어하기 위한 클래스(Person 클래스 상속)
class Enemy(Person):
    """
    Enemy sprite.
    """

    #객체 멤버변수 초기화
    def __init__(self, sheet_key, x, y, direction='down', state='resting', index=0):
        super(Enemy, self).__init__(sheet_key, x, y, direction, state, index)
        self.level = 1
        self.type = 'enemy'

#아이템이 들어있는 상자를 제어하기 위한 클래스(Person 클래스 상속)
class Chest(Person):
    """
    Treasure chest that contains items to collect.
    """
    #객체 멤버변수 초기화
    def __init__(self, x, y, id):
        super(Chest, self).__init__('treasurechest', x, y)
        self.spritesheet_dict = self.make_image_dict()
        self.image_list = self.make_image_list()
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect(x=x, y=y)
        self.id = id
    
    #상자가 닫힌 이미지와 열린 이미지가 저장된 딕셔너리를 구현하여 반환하는 메소드
    def make_image_dict(self):
        """
        Make a dictionary for the sprite's images.
        """
        sprite_sheet = setup.GFX['treasurechest']
        image_dict = {'closed': self.get_image(0, 0, 32, 32, sprite_sheet),
                      'opened': self.get_image(32, 0, 32, 32, sprite_sheet)}

        return image_dict

    #위에서 구현한 이미지 딕셔너리를 배열로 변환하는 메소드
    def make_image_list(self):
        """
        Make the list of two images for the chest.
        """
        image_list = [self.spritesheet_dict['closed'],
                      self.spritesheet_dict['opened']]

        return image_list

    #상자의 상태를 지정해주는 메소드
    def update(self, current_time, *args):
        """Implemented by inheriting classes"""
        self.blockers = self.set_blockers()
        self.current_time = current_time
        state_function = self.state_dict[self.state]
        state_function()
        self.location = self.get_tile_location()




