# -*- coding: utf-8 -*-

"""
This class controls all the GUI for the player menu screen.
이 클래스는 플레이어 메뉴 화면의 모든 GUI를 제어합니다.
"""
import sys
import pygame as pg
from . import setup, observer
from . import constants as c
from . import tools
import googletrans#구글 번역 API

#구글 번역 변수 translator.translate(문장, dest='ko').text 함수를 사용해 한글 문자열로 번역 가능
translator = googletrans.Translator()

#Python 2/3 compatibility.
#Python 2/3 호환성.
if sys.version_info[0] == 2:
    range = xrange


class SmallArrow(pg.sprite.Sprite):
    """
    Small arrow for menu.
    메뉴의 작은 화살표
    """
    def __init__(self, info_box, inventory): 
        super(SmallArrow, self).__init__()
        self.image = setup.GFX['smallarrow']
        self.rect = self.image.get_rect()
        self.state = 'selectmenu'
        self.state_dict = self.make_state_dict()
        self.slots = info_box.slots
        self.inventory = inventory  #현재 가지고 있는 아이템에 따른 아이템창 제어를 위한 인벤토리값.
        self.pos_list = []

    def make_state_dict(self):
        """
        Make state dictionary.
        상태 사전 만들기
        """
        state_dict = {'selectmenu': self.navigate_select_menu,
                      'itemsubmenu': self.navigate_item_submenu,
                      'magicsubmenu': self.navigate_magic_submenu}

        return state_dict

    def navigate_select_menu(self, pos_index):
        """
        Nav the select menu.
        선택 메뉴를 탐색합니다.
        """
        self.pos_list = self.make_select_menu_pos_list()
        self.rect.topleft = self.pos_list[pos_index]

    def navigate_item_submenu(self, pos_index):
        """
        Nav the item submenu
        항목 하위 메뉴 탐색
        """
        self.pos_list = self.make_item_menu_pos_list()
        self.rect.topleft = self.pos_list[pos_index]

    def navigate_magic_submenu(self, pos_index):
        """
        Nav the magic submenu.
        마법 하위 메뉴를 탐색
        """
        self.pos_list = self.make_magic_menu_pos_list()
        self.rect.topleft = self.pos_list[pos_index]

    def make_magic_menu_pos_list(self):
        """
        Make the list of possible arrow positions for magic submenu.
        마법 하위 메뉴에 사용할 수 있는 화살표 위치 목록을 만듭니다.
        """
        pos_list = [(310, 119),
                    (310, 169)]

        return pos_list

    def make_select_menu_pos_list(self):
        """
        Make the list of possible arrow positions.
        가능한 화살표 위치 목록을 작성합니다.
        """
        pos_list = []

        for i in range(3):
            pos = (35, 443 + (i * 45))
            pos_list.append(pos)

        return pos_list

    def make_item_menu_pos_list(self):
        """
        Make the list of arrow positions in the item submenu.
        항목 하위 메뉴에서 화살표 위치 목록을 만듭니다.
        """
        temp_list = [(300, 173),
                    (300, 223),
                    (300, 323),
                    (300, 373),
                    (300, 478),
                    (300, 528),
                    (535, 478),
                    (535, 528)]
        
        pos_list = []
    
        for i in self.inventory.index:
            pos_list.append[temp_list[i]]       #가지고 있는 아이템의 인덱스값에 따라 pos_list에 append.
        

        return pos_list

    def update(self, pos_index):
        """
        Update arrow position.
        화살표 위치를 업데이트
        """
        state_function = self.state_dict[self.state]
        state_function(pos_index)

    def draw(self, surface):
        """
        Draw to surface
        화면(표면) 그리기
        """
        surface.blit(self.image, self.rect)


class QuickStats(pg.sprite.Sprite):
    def __init__(self, game_data):
        self.inventory = game_data['player inventory']
        self.game_data = game_data
        self.health = game_data['player stats']['health']
        self.stats = self.game_data['player stats']
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.small_font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 18)
        self.image, self.rect = self.make_image()

    def make_image(self):
        """
        Make the surface for the gold box.
        골드 상자의 표면을 만들어라.
        """
        stat_list = ['GOLD', 'health', 'magic'] 
        magic_health_list  = ['health', 'magic']
        image = setup.GFX['goldbox']
        rect = image.get_rect(left=10, top=244)

        surface = pg.Surface(rect.size)
        surface.set_colorkey(c.BLACK)
        surface.blit(image, (0, 0))

        for i, stat in enumerate(stat_list):
            first_letter = stat[0].upper()
            rest_of_letters = stat[1:]
            if stat in magic_health_list:
                current = self.stats[stat]['current']
                max = self.stats[stat]['maximum']
                text = translator = translator.translate("{}{}: {}/{}".format(first_letter, rest_of_letters, current, max), dest='ko').text
            elif stat == 'GOLD':
                text = translator.translate("Gold: {}".format(self.inventory[stat]['quantity']), dest='ko').text
            render = self.small_font.render(text, True, c.NEAR_BLACK)
            x = 26
            y = 45 + (i*30)
            text_rect = render.get_rect(x=x,
                                        centery=y)
            surface.blit(render, text_rect)

        if self.game_data['crown quest']:
            crown = setup.GFX['crown']
            crown_rect = crown.get_rect(x=178, y=40)
            surface.blit(crown, crown_rect)
        
        return surface, rect

    def update(self):
        """
        Update gold.
        골드 업데이트
        """
        self.image, self.rect = self.make_image()

    def draw(self, surface):
        """
        Draw to surface.
        표면(화면) 그리기
        """
        surface.blit(self.image, self.rect)

#정보 박스 클래스
class InfoBox(pg.sprite.Sprite):
    def __init__(self, inventory, player_stats):
        super(InfoBox, self).__init__()
        self.inventory = inventory
        self.player_stats = player_stats
        self.attack_power = self.get_attack_power()
        self.defense_power = self.get_defense_power()
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.big_font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 24)
        self.title_font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 28)
        self.title_font.set_underline(True)
        self.get_tile = tools.get_tile
        self.sword = self.get_tile(48, 0, setup.GFX['shopsigns'], 16, 16, 2)
        self.shield = self.get_tile(32, 0, setup.GFX['shopsigns'], 16, 16, 2)
        self.potion = self.get_tile(16, 0, setup.GFX['shopsigns'], 16, 16, 2)
        self.possible_potions = [translator.translate('Healing Potion', dest='ko').text, translator.translate('ELIXIR', dest='ko').text, translator.translate('Ether Potion', dest='ko').text]
        self.possible_armor = [translator.translate('Wooden Shield', dest='ko').text, translator.translate('Chain Mail', dest='ko').text]
        self.possible_weapons = [translator.translate('Long Sword', dest='ko').text, translator.translate('Rapier', dest='ko').text]
        self.possible_magic = [translator.translate('Fire Blast', dest='ko').text, translator.translate('Cure', dest='ko').text]
        self.quantity_items = [translator.translate('Healing Potion', dest='ko').text, translator.translate('ELIXIR', dest='ko').text, translator.translate('Ether Potion', dest='ko').text]
        self.slots = {}
        self.state = 'invisible'
        self.state_dict = self.make_state_dict()
        self.print_slots = True

    def get_attack_power(self):
        """
        Calculate the current attack power based on equipped weapons.
        장비된 무기를 바탕으로 현재의 공격력을 계산합니다.
        """
        weapon = self.inventory['equipped weapon']
        return self.inventory[weapon]['power']

    def get_defense_power(self):
        """
        Calculate the current defense power based on equipped weapons.
        장비된 무기를 기반으로 현재의 방어력을 계산합니다.
        """
        defense_power = 0
        for armor in self.inventory['equipped armor']:
            defense_power += self.inventory[armor]['power']

        return defense_power

    def make_state_dict(self):
        """
        Make the dictionary of state methods
        상태 방법 사전 만들기
        """
        state_dict = {'stats': self.show_player_stats,
                      'items': self.show_items,
                      'magic': self.show_magic,
                      'invisible': self.show_nothing}

        return state_dict


    def show_player_stats(self):
        """
        Show the player's main stats
        플레이어의 기본 통계 표시
        """
        title = 'STATS'
        stat_list = [translator.translate('Level', dest='ko').text, translator.translate('experience to next level', dest='ko').text,
                     translator.translate('health', dest='ko').text, translator.translate('magic', dest='ko').text, translator.translate('Attack Power', dest='ko').text, 
                     translator.translate('Defense Power', dest='ko').text, translator.translate('gold', dest='ko').text]
        attack_power = 5
        surface, rect = self.make_blank_info_box(title)

        for i, stat in enumerate(stat_list):
            if stat == translator.translate('health', dest='ko').text or stat == translator.translate('magic', dest='ko').text:
                text = translator.translate("{}{}: {} / {}".format(stat[0].upper(),
                                              stat[1:],
                                              str(self.player_stats[stat]['current']),
                                              str(self.player_stats[stat]['maximum'])), dest='ko').text
            elif stat == translator.translate('experience to next level', dest='ko').text:
                text = translator.translate("{}{}: {}".format(stat[0].upper(),
                                         stat[1:],
                                         self.player_stats[stat]), dest='ko').text
            elif stat == translator.translate('Attack Power', dest='ko').text:
                text = translator.translate("{}: {}".format(stat, self.get_attack_power()), dest='ko').text
            elif stat == translator.translate('Defense Power', dest='ko').text:
                text = translator.translate("{}: {}".format(stat, self.get_defense_power()), dest='ko').text
            elif stat == translator.translate('gold', dest='ko').text:
                text = translator.translate("Gold: {}".format(self.inventory['GOLD']['quantity']), dest='ko').text
            else:
                text = translator.translate("{}: {}".format(stat, str(self.player_stats[stat])), dest='ko').text
            text_image = self.font.render(text, True, c.NEAR_BLACK)
            text_rect = text_image.get_rect(x=50, y=80+(i*50))
            surface.blit(text_image, text_rect)

        self.image = surface
        self.rect = rect


    def show_items(self):
        """
        Show list of items the player has
        플레이어가 가지고 있는 항목 목록 표시
        """
        title = 'ITEMS'
        potions = ['POTIONS']
        weapons = ['WEAPONS']
        armor = ['ARMOR']
        for i, item in enumerate(self.inventory):
            if item in self.possible_weapons:
                if item == self.inventory['equipped weapon']:
                    item += " (E)"
                weapons.append(item)
            elif item in self.possible_armor:
                if item in self.inventory['equipped armor']:
                    item += " (E)"
                armor.append(item)
            elif item in self.possible_potions:
                potions.append(item)

        self.slots = {}
        self.assign_slots(weapons, 85)
        self.assign_slots(armor, 235)
        self.assign_slots(potions, 390)

        surface, rect = self.make_blank_info_box(title)

        self.blit_item_lists(surface)

        self.sword['rect'].topleft = 40, 80
        self.shield['rect'].topleft = 40, 230
        self.potion['rect'].topleft = 40, 385
        surface.blit(self.sword['surface'], self.sword['rect'])
        surface.blit(self.shield['surface'], self.shield['rect'])
        surface.blit(self.potion['surface'], self.potion['rect'])

        self.image = surface
        self.rect = rect


    def assign_slots(self, item_list, starty, weapon_or_armor=False):
        """
        Assign each item to a slot in the menu
        메뉴의 슬롯에 각 항목 할당
        """
        if len(item_list) > 3:
            for i, item in enumerate(item_list[:3]):
                posx = 80
                posy = starty + (i * 50)
                self.slots[(posx, posy)] = item
            for i, item in enumerate(item_list[3:]):
                posx = 315
                posy = (starty + 50) + (i * 5)
                self.slots[(posx, posy)] = item
        else:
            for i, item in enumerate(item_list):
                posx = 80
                posy = starty + (i * 50)
                self.slots[(posx, posy)] = item

    def assign_magic_slots(self, magic_list, starty):
        """
        Assign each magic spell to a slot in the menu.
        각 마법 주문을 메뉴의 슬롯에 할당합니다.
        """
        for i, spell in enumerate(magic_list):
            posx = 120
            posy = starty + (i * 50)
            self.slots[(posx, posy)] = spell

    def blit_item_lists(self, surface):
        """
        Blit item list to info box surface
        항목 목록을 정보 상자 표면에 만들기
        """
        for coord in self.slots:
            item = self.slots[coord]

            if item in self.possible_potions:
                text = "{}: {}".format(self.slots[coord],
                                       self.inventory[item]['quantity'])
            else:
                text = "{}".format(self.slots[coord])
            text_image = self.font.render(text, True, c.NEAR_BLACK)
            text_rect = text_image.get_rect(topleft=coord)
            surface.blit(text_image, text_rect)

    def show_magic(self):
        """
        Show list of magic spells the player knows
        플레이어가 알고 있는 마법 주문 목록 표시
        """
        title = 'MAGIC'
        item_list = []
        for item in self.inventory:
            if item in self.possible_magic:
                item_list.append(item)
                item_list = sorted(item_list)

        self.slots = {}
        self.assign_magic_slots(item_list, 80)

        surface, rect = self.make_blank_info_box(title)

        for i, item in enumerate(item_list):
            text_image = self.font.render(item, True, c.NEAR_BLACK)
            text_rect = text_image.get_rect(x=100, y=80+(i*50))
            surface.blit(text_image, text_rect)

        self.image = surface
        self.rect = rect

    def show_nothing(self):
        """
        Show nothing when the menu is opened from a level.
        라벨에서 메뉴를 열 때 아무것도 표시하지 않습니다.
        """
        self.image = pg.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.image.fill(c.BLACK_BLUE)

    def make_blank_info_box(self, title):
        """
        Make an info box with title, otherwise blank
        제목을 사용하여 정보 상자 만들기, 그렇지 않으면 빈칸 만들기
        """
        image = setup.GFX['playerstatsbox']
        rect = image.get_rect(left=285, top=35)
        centerx = rect.width / 2

        surface = pg.Surface(rect.size)
        surface.set_colorkey(c.BLACK)
        surface.blit(image, (0,0))

        title_image = self.title_font.render(title, True, c.NEAR_BLACK)
        title_rect = title_image.get_rect(centerx=centerx, y=30)
        surface.blit(title_image, title_rect)

        return surface, rect


    def update(self):
        """
        state 업데이트하기
        """
        state_function = self.state_dict[self.state]
        state_function()


    def draw(self, surface):
        """
        Draw to surface
        표면(화면) 그리기
        """
        surface.blit(self.image, self.rect)


# 선택된 박스 클래스
class SelectionBox(pg.sprite.Sprite):
    def __init__(self):
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.image, self.rect = self.make_image()

    # 이미지 만들기 메소드
    def make_image(self):
        choices = [translator.translate('Items', dest='ko').text, translator.translate('Magic', dest='ko').text, translator.translate('Stats', dest='ko').text]   #선택할 수 있는 항목 item, magic, stats
        image = setup.GFX['goldbox']            #goldbox 이미지 가져오기
        rect = image.get_rect(left=10, top=425)

        surface = pg.Surface(rect.size)
        surface.set_colorkey(c.BLACK)
        surface.blit(image, (0, 0))

        for i, choice in enumerate(choices):
            choice_image = self.font.render(choice, True, c.NEAR_BLACK)
            choice_rect = choice_image.get_rect(x=100, y=(15 + (i * 45)))
            surface.blit(choice_image, choice_rect)

        return surface, rect

    def draw(self, surface):
        """
        Draw to surface
        표면(화면)그리기
        """
        surface.blit(self.image, self.rect)

# 메뉴 GUI 클래스
class MenuGui(object):
    def __init__(self, level, inventory, stats):
        self.level = level
        self.game_data = self.level.game_data
        self.sfx_observer = observer.SoundEffects()
        self.observers = [self.sfx_observer]
        self.inventory = inventory
        self.stats = stats
        self.info_box = InfoBox(inventory, stats)
        self.gold_box = QuickStats(self.game_data)
        self.selection_box = SelectionBox()
        self.arrow = SmallArrow(self.info_box,self.inventory)
        self.arrow_index = 0
        self.allow_input = False

    def check_for_input(self, keys):
        """
        Check for input
        입력 확인
        """
        if self.allow_input:
            if keys[pg.K_DOWN]:         #방향키 아래
                if self.arrow_index < len(self.arrow.pos_list) - 1:
                    self.notify(c.CLICK)
                    self.arrow_index += 1
                    self.allow_input = False
            elif keys[pg.K_UP]:         #방향키 위
                if self.arrow_index > 0:
                    self.notify(c.CLICK)
                    self.arrow_index -= 1
                    self.allow_input = False
            elif keys[pg.K_RIGHT]:      #방향키 오른쪽
                if self.info_box.state == 'items':
                    if not self.arrow.state == 'itemsubmenu':
                        self.notify(c.CLICK)
                        self.arrow_index = 0
                    self.arrow.state = 'itemsubmenu'
                elif self.info_box.state == 'magic':    
                    if not self.arrow.state == 'magicsubmenu':
                        self.notify(c.CLICK)
                        self.arrow_index = 0
                    self.arrow.state = 'magicsubmenu'
                self.allow_input = False

            elif keys[pg.K_LEFT]:   #방향키 왼쪽
                self.notify(c.CLICK)
                self.arrow.state = 'selectmenu'
                self.arrow_index = 0
                self.allow_input = False
            elif keys[pg.K_SPACE]:  # 방향키 스페이스바
                self.notify(c.CLICK2)
                if self.arrow.state == 'selectmenu':
                    if self.arrow_index == 0:
                        self.info_box.state = 'items'
                        self.arrow.state = 'itemsubmenu'
                        self.arrow_index = 0
                    elif self.arrow_index == 1:
                        self.info_box.state = 'magic'
                        self.arrow.state = 'magicsubmenu'
                        self.arrow_index = 0
                    elif self.arrow_index == 2:
                        self.info_box.state = 'stats'
                elif self.arrow.state == 'itemsubmenu':
                    self.select_item()
                elif self.arrow.state == 'magicsubmenu':
                    self.select_magic()

                self.allow_input = False
            elif keys[pg.K_RETURN]:     # return 키
                self.level.state = 'normal'
                self.info_box.state = 'invisible'
                self.allow_input = False
                self.arrow_index = 0
                self.arrow.state = 'selectmenu'

        if (not keys[pg.K_DOWN]     # 모든 키가 아닐 때
                and not keys[pg.K_UP]
                and not keys[pg.K_RETURN]
                and not keys[pg.K_SPACE]
                and not keys[pg.K_RIGHT]
                and not keys[pg.K_LEFT]):
            self.allow_input = True

    def notify(self, event):
        """
        Notify all observers of event.
        모든 관찰자에게 이벤트를 알립니다.
        """
        for observer in self.observers:
            observer.on_notify(event)

    def select_item(self):
        """
        Select item from item menu.
        아이템 메뉴에서 아이템 선택
        """
        health = self.game_data['player stats']['health']
        posx = self.arrow.rect.x - 220
        posy = self.arrow.rect.y - 38

        if (posx, posy) in self.info_box.slots:
            if self.info_box.slots[(posx, posy)][:7] == translator.translate('Healing', dest='ko').text:
                potion = translator.translate('Healing Potion', dest='ko').text
                value = 30
                self.drink_potion(potion, health, value)
            elif self.info_box.slots[(posx, posy)][:5] == translator.translate('Ether', dest='ko').text:
                potion = translator.translate('Ether Potion', dest='ko').text
                stat = self.game_data['player stats']['magic']
                value = 30
                self.drink_potion(potion, stat, value)
            elif self.info_box.slots[(posx, posy)][:10] == translator.translate('Long Sword', dest='ko').text:
                self.inventory['equipped weapon'] = translator.translate('Long Sword', dest='ko').text
            elif self.info_box.slots[(posx, posy)][:6] == translator.translate('Rapier', dest='ko').text:
                self.inventory['equipped weapon'] = translator.translate('Rapier', dest='ko').text
            elif self.info_box.slots[(posx, posy)][:13] == translator.translate('Wooden Shield', dest='ko').text:
                if translator.translate('Wooden Shield', dest='ko').text in self.inventory['equipped armor']:
                    self.inventory['equipped armor'].remove(translator.translate('Wooden Shield', dest='ko').text)
                else:
                    self.inventory['equipped armor'].append(translator.translate('Wooden Shield', dest='ko').text)
            elif self.info_box.slots[(posx, posy)][:10] == translator.translate('Chain Mail', dest='ko').text:
                if 'Chain Mail' in self.inventory['equipped armor']:
                    self.inventory['equipped armor'].remove(translator.translate('Chain Mail', dest='ko').text)
                else:
                    self.inventory['equipped armor'].append(translator.translate('Chain Mail', dest='ko').text)

    def select_magic(self):
        """
        Select spell from magic menu.
        마법 메뉴에서 spell(사용할 마법) 선택
        """
        health = self.game_data['player stats']['health']
        magic = self.game_data['player stats']['magic']
        posx = self.arrow.rect.x - 190
        posy = self.arrow.rect.y - 39

        if (posx, posy) in self.info_box.slots:
            if self.info_box.slots[(posx, posy)][:4] == translator.translate('Cure', dest='ko').text: # cure(치료) 마법 선택시
               self.use_cure_spell()

    def use_cure_spell(self):
        """
        Use cure spell to heal player.
        치료 마법을 사용하여 플레이어를 치료합니다.
        """
        health = self.game_data['player stats']['health']
        magic = self.game_data['player stats']['magic']
        inventory = self.game_data['player inventory']

        if health['current'] != health['maximum']:  # 현재 체력이 최대 체력이 아니라면
            if magic['current'] >= inventory['Cure']['magic points']:   #현재 마법 포인트가 치료할 수 있는 마법 포인트보다 클 떄
                self.notify(c.POWERUP)
                magic['current'] -= inventory['Cure']['magic points']
                health['current'] += inventory['Cure']['power']
                if health['current'] > health['maximum']:   # 현재 체력이 최대 체력보다 높게 추가되었다면
                    health['current'] = health['maximum']

    def drink_potion(self, potion, stat, value):
        """
        Drink potion and change player stats.
        물약을 마시고 플레이어 상태를 변경한다.
        """
        if stat['current'] != stat['maximum']:  #현재 상태가 최대 상태가 아닐 때
            self.notify(c.POWERUP)
            self.inventory[potion]['quantity'] -= 1 # 물약 갯수 -1
            stat['current'] += value                # 현재 상태에 value만큼 더하기
            if stat['current'] > stat['maximum']:   #현재 상태가 최대 상태보다 크게 더해졌을 때
                stat['current'] = stat['maximum']   # 현재 상태를 최대 상태와 동일하게 변경
            if not self.inventory[potion]['quantity']: # 보관함에 있는 포션의 양이 없다면
                del self.inventory[potion]              # 보관함에서 포션 삭제.

    def update(self, keys):
        """
        업데이트
        """
        self.info_box.update()
        self.gold_box.update()
        self.arrow.update(self.arrow_index)
        self.check_for_input(keys)


    def draw(self, surface):
        """
        그리기 메소드
        """
        self.gold_box.draw(surface)
        self.info_box.draw(surface)
        self.selection_box.draw(surface)
        self.arrow.draw(surface)
