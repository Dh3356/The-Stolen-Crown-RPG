"""
This class is the parent class of all shop states.
This includes weapon, armour, magic and potion shops.
It also includes the inn.  These states are scaled
twice as big as a level state. The self.gui controls
all the textboxes.
"""

import copy
import pygame as pg
from .. import tools, setup, shopgui
from .. import constants as c

#모든 상점 상태들의 부모 클래스가 되는 클래스
#weapon 상점, armour상점, magic 상점, potion 상점의 부모 클래스(여관도 포함)
#다른 상태 대비 2배 확대된다.
#self.gui는 모든 텍스트박스들을 제어한다.
class Shop(tools._State):
    """Basic shop state"""
    
    #객체 멤버변수 초기화
    def __init__(self):
        super(Shop, self).__init__()
        self.key = None
        self.sell_items = None
        self.music = setup.MUSIC['shop_theme']
        self.volume = 0.4

    #상점 상태로 돌입할 때 셋업을 해주는 메소드
    def startup(self, current_time, game_data):
        """Startup state"""
        self.game_data = game_data
        self.current_time = current_time
        self.state_dict = self.make_state_dict()
        self.state = 'transition in'
        self.next = c.TOWN
        self.get_image = tools.get_image
        self.dialogue = self.make_dialogue()
        self.accept_dialogue = self.make_accept_dialogue()
        self.accept_sale_dialogue = self.make_accept_sale_dialogue()
        self.items = self.make_purchasable_items()
        self.background = self.make_background()
        self.gui = shopgui.Gui(self)
        self.transition_rect = setup.SCREEN.get_rect()
        self.transition_alpha = 255

    #모든 상태에 대한 딕셔너리를 구현하는 메소드
    def make_state_dict(self):
        """
        Make a dictionary for all state methods.
        """
        state_dict = {'normal': self.normal_update,
                      'transition in': self.transition_in,
                      'transition out': self.transition_out}

        return state_dict

    #대화 구문 리스트를 구현하는 명시적 메소드(내용x)
    def make_dialogue(self):
        """
        Make the list of dialogue phrases.
        """
        raise NotImplementedError

    #player가 아이템을 구매할 시 출력하는 구문을 반환하는 메소드
    def make_accept_dialogue(self):
        """
        Make the dialogue for when the player buys an item.
        """
        return ['Item purchased.']

    #player가 아이템을 판매할 시 출력하는 구문을 반환하는 메소드
    def make_accept_sale_dialogue(self):
        """
        Make the dialogue for when the player sells an item.
        """
        return ['Item sold.']

    #상점에서 구매할 수 있는 아이템 리스트를 구현하는 명시적 메소드(내용x)
    def make_purchasable_items(self):
        """
        Make the list of items to be bought at shop.
        """
        raise NotImplementedError

    #상점의 배경을 surface를 구현하는 메소드(player와 상점주인의 크기 증가, 배경 검정색)
    def make_background(self):
        """
        Make the level surface.
        """
        background = pg.sprite.Sprite()
        surface = pg.Surface(c.SCREEN_SIZE).convert()
        surface.fill(c.BLACK_BLUE)
        background.image = surface
        background.rect = background.image.get_rect()

        player = self.make_sprite('player', 96, 32, 150)
        shop_owner = self.make_sprite(self.key, 32, 32, 600)
        counter = self.make_counter()

        background.image.blit(player.image, player.rect)
        background.image.blit(shop_owner.image, shop_owner.rect)
        background.image.blit(counter.image, counter.rect)

        return background

    #player의 이미지를 가져오는 메소드(작은 surface 새로 구현)
    def make_sprite(self, key, coordx, coordy, x, y=304):
        """
        Get the image for the player.
        """
        spritesheet = setup.GFX[key]
        surface = pg.Surface((32, 32))
        surface.set_colorkey(c.BLACK)
        image = self.get_image(coordx, coordy, 32, 32, spritesheet)
        rect = image.get_rect()
        surface.blit(image, rect)

        surface = pg.transform.scale(surface, (96, 96))
        rect = surface.get_rect(left=x, centery=y)
        sprite = pg.sprite.Sprite()
        sprite.image = surface
        sprite.rect = rect

        return sprite

    #카운터 이미지를 구현하는 메소드
    def make_counter(self):
        """
        Make the counter to conduct business.
        """
        sprite_sheet = copy.copy(setup.GFX['house'])
        sprite = pg.sprite.Sprite()
        sprite.image = self.get_image(102, 64, 26, 82, sprite_sheet)
        sprite.image = pg.transform.scale2x(sprite.image)
        sprite.rect = sprite.image.get_rect(left=550, top=225)

        return sprite

    #현재 상태를 참조하여 장면을 업데이트하는 메소드
    def update(self, surface, keys, current_time):
        """
        Update scene.
        """
        state_function = self.state_dict[self.state]
        state_function(surface, keys, current_time)

    #상점에서 일련의 처리를 마친 후에 상태를 업데이트 하는 메소드
    def normal_update(self, surface, keys, current_time):
        """
        Update level normally.
        """
        self.gui.update(keys, current_time)
        self.draw_level(surface)

    #상점에 진입할 때 배경을 서서히변경하는 메소드(페이드인)
    def transition_in(self, surface, *args):
        """
        Transition into level.
        """
        transition_image = pg.Surface(self.transition_rect.size)
        transition_image.fill(c.TRANSITION_COLOR)
        transition_image.set_alpha(self.transition_alpha)
        self.draw_level(surface)
        surface.blit(transition_image, self.transition_rect)
        self.transition_alpha -= c.TRANSITION_SPEED 
        if self.transition_alpha <= 0:
            self.state = 'normal'
            self.transition_alpha = 0

    #상점에서 나올 때 배경을 서서히 변경하는 메소드(페이드 아웃)
    def transition_out(self, surface, *args):
        """
        Transition level to new scene.
        """
        transition_image = pg.Surface(self.transition_rect.size)
        transition_image.fill(c.TRANSITION_COLOR)
        transition_image.set_alpha(self.transition_alpha)
        self.draw_level(surface)
        surface.blit(transition_image, self.transition_rect)
        self.transition_alpha += c.TRANSITION_SPEED 
        if self.transition_alpha >= 255:
            self.done = True

    #surface에 배경 그림을 blit하는 메소드
    def draw_level(self, surface):
        """
        Blit graphics to game surface.
        """
        surface.blit(self.background.image, self.background.rect)
        self.gui.draw(surface)

#상점의 일종인 여관을 제어하는 클래스
class Inn(Shop):
    """
    Where our hero gets rest.
    """
    
    #객체 멤버변수 초기화
    def __init__(self):
        super(Inn, self).__init__()
        self.name = c.INN
        self.key = 'innman'

    #여관 진입 시 대화 구문을 반환하는 메소드
    def make_dialogue(self):
        """
        Make the list of dialogue phrases.
        """
        return ["Welcome to the " + self.name + "!",
                "Would you like a room to restore your health?"]

    #player가 아이템을 구매(휴식)하면 출력하는 구문 반환하는 메소드
    def make_accept_dialogue(self):
        """
        Make the dialogue for when the player buys an item.
        """
        return ['Your health has been replenished and your game saved!']

    #구매 가능한 아이템(휴식)과 관련된 값들을 딕셔너리 형태로 구현하는 메소드
    def make_purchasable_items(self):
        """Make list of items to be chosen"""
        dialogue = 'Rent a room (30 gold)'

        item = {'type': 'room',
                'price': 30,
                'quantity': 0,
                'power': None,
                'dialogue': dialogue}

        return [item]

#상점의 일종인 무기상점을 제어하는 클래스
class WeaponShop(Shop):
    """A place to buy weapons"""

    #객체 멤버변수 초기화
    def __init__(self):
        super(WeaponShop, self).__init__()
        self.name = c.WEAPON_SHOP
        self.key = 'weaponman'
        self.sell_items = ['Long Sword', 'Rapier']


    #대화 구문 리스트를 구현하여 반환하는 메소드
    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "What weapon would you like to buy?"]


    #구매 가능한 아이템과 관련 정보를 딕셔너리로 구현하여 반환하는 메소드
    def make_purchasable_items(self):
        """Make list of items to be chosen"""
        longsword_dialogue = 'Long Sword (150 gold)'
        rapier_dialogue = 'Rapier (50 gold)'

        item2 = {'type': 'Long Sword',
                'price': 150,
                'quantity': 1,
                'power': 11,
                'dialogue': longsword_dialogue,
                'index':1}

        item1 = {'type': 'Rapier',
                 'price': 50,
                 'quantity': 1,
                 'power': 9,
                 'dialogue': rapier_dialogue,
                 'index':0}

        return [item1, item2]


#상점의 일종인 방어구 상점을 제어하는 클래스
class ArmorShop(Shop):
    """A place to buy armor"""

    #객체 멤버변수 초기화
    def __init__(self):
        super(ArmorShop, self).__init__()
        self.name = c.ARMOR_SHOP
        self.key = 'armorman'
        self.sell_items = ['Chain Mail', 'Wooden Shield']

    #대화 구문을 반환하는 메소드
    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "Would piece of armor would you like to buy?"]

    #구매 가능한 아이템과 관련 정보를 딕셔너리로 구현하여 반환하는 메소드
    def make_purchasable_items(self):
        """Make list of items to be chosen"""
        chainmail_dialogue = 'Chain Mail (50 gold)'
        shield_dialogue = 'Wooden Shield (75 gold)'

        item = {'type': 'Chain Mail',
                'price': 50,
                'quantity': 1,
                'power': 2,
                'dialogue': chainmail_dialogue,
                'index':2}

        item2 = {'type': 'Wooden Shield',
                 'price': 75,
                 'quantity': 1,
                 'power': 3,
                 'dialogue': shield_dialogue,
                 'index':3}

        return [item, item2]

#상점의 일종인 마법상점을 제어하는 클래스
class MagicShop(Shop):
    """A place to buy magic"""
    #객체 멤버변수 초기화
    def __init__(self):
        super(MagicShop, self).__init__()
        self.name = c.MAGIC_SHOP
        self.key = 'magiclady'

    #대화 구문을 반환하는 메소드
    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "Would magic spell would you like to buy?"]

    #구매 가능한 아이템과 관련 정보를 딕셔너리로 구현하여 반환하는 메소드
    def make_purchasable_items(self):
        """Make list of items to be chosen"""
        fire_dialogue = 'Fire Blast (150 gold)'
        cure_dialogue = 'Cure (50 gold)'

        item1 = {'type': 'Cure',
                 'price': 50,
                 'quantity': 1,
                 'magic points': 25,
                 'power': 50,
                 'dialogue': cure_dialogue}

        item2 = {'type': 'Fire Blast',
                'price': 150,
                'quantity': 1,
                'magic points': 40,
                'power': 15,
                'dialogue': fire_dialogue}

        return [item1, item2]

#상점의 일종인 포션상점을 제어하는 클래스
class PotionShop(Shop):
    """A place to buy potions"""
    
    #객체 멤버변수 초기화
    def __init__(self):
        super(PotionShop, self).__init__()
        self.name = c.POTION_SHOP
        self.key = 'potionlady'
        self.sell_items = 'Healing Potion'

    #대화 구문을 반환하는 메소드
    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "What potion would you like to buy?"]

    #구매 가능한 아이템과 관련 정보를 딕셔너리로 구현하여 반환하는 메소드
    def make_purchasable_items(self):
        """Make list of items to be chosen"""
        healing_dialogue = 'Healing Potion (15 gold)'
        ether_dialogue = 'Ether Potion (15 gold)'


        item = {'type': 'Healing Potion',
                'price': 15,
                'quantity': 1,
                'power': None,
                'dialogue': healing_dialogue,
                'index': 5}

        item2 = {'type': 'Ether Potion',
                 'price': 15,
                 'quantity': 1,
                 'power': None,
                 'dialogue': ether_dialogue,
                 'index': 4}

        return [item, item2]

