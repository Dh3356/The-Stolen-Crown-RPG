__author__ = 'justinarmstrong'
import copy
import pygame as pg
from .. import setup, observer, tools
from .. import constants as c

#다음 페이지가 있다는 것을 알려주는 깜빡거리는 화살표를 구현하는 클래스
class NextArrow(pg.sprite.Sprite):
    """Flashing arrow indicating more dialogue"""
    #객체 맴버변수 초기화
    def __init__(self):
        super(NextArrow, self).__init__()
        self.image = setup.GFX['fancyarrow']
        self.rect = self.image.get_rect(right=780,
                                        bottom=135)

#대화 스크립트를 표시해주는 텍스트박스를 구현하는 클래스
class DialogueBox(object):
    """Text box used for dialogue"""
    #객체 멤버변수 초기화
    def __init__(self, dialogue, index=0, image_key='dialoguebox', item=None):
        self.item = item
        self.bground = setup.GFX[image_key]
        self.rect = self.bground.get_rect(centerx=400)
        self.arrow_timer = 0.0
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.dialogue_list = dialogue
        self.index = index
        self.image = self.make_dialogue_box_image()
        self.arrow = NextArrow()
        self.check_to_draw_arrow()
        self.done = False
        self.allow_input = False
        self.name = image_key
        self.observers = [observer.SoundEffects()]
        self.notify = tools.notify_observers
        self.notify(self, c.CLICK)

    #대화박스의 이미지를 가져와  텍스트와 함께 surface에 blit해주는 메소드
    def make_dialogue_box_image(self):
        """
        Make the image of the dialogue box.
        """
        image = pg.Surface(self.rect.size)
        image.set_colorkey(c.BLACK)
        image.blit(self.bground, (0, 0))

        dialogue_image = self.font.render(self.dialogue_list[self.index],
                                          True,
                                          c.NEAR_BLACK)
        dialogue_rect = dialogue_image.get_rect(left=50, top=50)
        image.blit(dialogue_image, dialogue_rect)

        return image

    #텍스트,텍스트 박스를 업데이트 해주는 메소드
    def update(self, keys, current_time):
        """Updates scrolling text"""
        self.current_time = current_time
        self.draw_box(current_time)
        self.terminate_check(keys)
    
    #다음 대화로 넘어갈 때 새로 텍스트박스와 텍스트를 그려주는 메소드(make_dialogue_box_image() 호출)
    #다음 페이지가 있는지 확인하여 화살표를 그릴지 결정한다.(check_to_draw_arrow() 호출)
    def draw_box(self, current_time, x=400):
        """Reveal dialogue on textbox"""
        self.image = self.make_dialogue_box_image()
        self.check_to_draw_arrow()

    #텍스트가 마지막인지 확인하는 메소드(TextHandler에서 활용하는 done, allow_input 값 변경)
    def terminate_check(self, keys):
        """Remove textbox from sprite group after 2 seconds"""
        if keys[pg.K_SPACE] and self.allow_input:
            self.done = True

        if not keys[pg.K_SPACE]:
            self.allow_input = True
    
    #다음 텍스트 페이지가 있는지 확인하여(dialouge_list, index 참조) 화살표를 그릴지 결정하는 메소드
    def check_to_draw_arrow(self):
        """
        Blink arrow if more text needs to be read.
        """
        if self.index < len(self.dialogue_list) - 1:
            self.image.blit(self.arrow.image, self.arrow.rect)

#대화박스를 생성하는데에 필요한 상호작용을 제어하기 위한 클래스
class TextHandler(object):
    """Handles interaction between sprites to create dialogue boxes"""

    #객체 매개변수 초기화
    def __init__(self, level):
        self.player = level.player
        self.sprites = level.sprites
        self.talking_sprite = None
        self.textbox = None
        self.allow_input = False
        self.level = level
        self.last_textbox_timer = 0.0
        self.game_data = level.game_data
        self.observers = [observer.SoundEffects()]
        self.notify = tools.notify_observers

    #대화 박스를 생성하기 위한 조건들을 체크하기 위한 메소드(done, allow_input 등 멤버 참조)
    def update(self, keys, current_time):
        """Checks for the creation of Dialogue boxes"""
        if keys[pg.K_SPACE] and not self.textbox and self.allow_input:
            for sprite in self.sprites:
                if (current_time - self.last_textbox_timer) > 300:
                    if self.player.state == 'resting':
                        self.allow_input = False
                        self.check_for_dialogue(sprite)

        if self.textbox:
            if self.talking_sprite.name == 'treasurechest':
                self.open_chest(self.talking_sprite)

            self.textbox.update(keys, current_time)

            if self.textbox.done:

                if self.textbox.index < (len(self.textbox.dialogue_list) - 1):
                    index = self.textbox.index + 1
                    dialogue = self.textbox.dialogue_list
                    if self.textbox.name == 'dialoguebox':
                        self.textbox = DialogueBox(dialogue, index)
                    elif self.textbox.name == 'infobox':
                        self.textbox = ItemBox(dialogue, index)
                elif self.talking_sprite.item:
                    self.check_for_item()
                elif self.talking_sprite.battle:
                    self.game_data['battle type'] = self.talking_sprite.battle
                    self.end_dialogue(current_time)
                    self.level.switch_to_battle = True
                elif self.talking_sprite.name == 'oldmanbrother' and \
                        self.game_data['talked to sick brother'] and \
                        not self.game_data['has brother elixir']:
                    self.talking_sprite.item = 'ELIXIR'
                    self.game_data['has brother elixir'] = True
                    self.check_for_item()
                    dialogue = ['Hurry! There is precious little time.']
                    self.talking_sprite.dialogue = dialogue
                elif self.talking_sprite.name == 'oldman':
                    if self.game_data['has brother elixir'] and \
                            not self.game_data['elixir received']:
                        del self.game_data['player inventory']['ELIXIR']
                        self.game_data['elixir received'] = True
                        dialogue = ['My good health is thanks to you.',
                                    'I will be forever in your debt.']
                        self.talking_sprite.dialogue = dialogue
                    elif not self.game_data['talked to sick brother']:
                        self.game_data['talked to sick brother'] = True
                         
                        dialogue = ['Hurry to the NorthEast Shores!',
                                    'I do not have much time left.']
                        self.talking_sprite.dialogue = dialogue
                    else:
                        self.end_dialogue(current_time)
                elif self.talking_sprite.name == 'king':
                     
                    if not self.game_data['talked to king']:
                        self.game_data['talked to king'] = True
                        new_dialogue = ['Hurry to the castle in the NorthWest!',
                                        'The sorceror who lives there has my crown.',
                                        'Please retrieve it for me.']
                        self.talking_sprite.dialogue = new_dialogue
                        self.end_dialogue(current_time)
                    elif self.game_data['crown quest']:
                        self.game_data['delivered crown'] = True
                        self.end_dialogue(current_time)
                    else:
                        self.end_dialogue(current_time)
                else:
                    self.end_dialogue(current_time)


        if not keys[pg.K_SPACE]:
            self.allow_input = True

    #대화 박스 상태를 종료하는 메소드
    def end_dialogue(self, current_time):
        """
        End dialogue state for level.
        """
        self.talking_sprite = None
        self.level.state = 'normal'
        self.textbox = None
        self.last_textbox_timer = current_time
        self.reset_sprite_direction()
        self.notify(self, c.CLICK)

    #ai캐릭터에 대화를 걸면 player를 바라보도록 하는 메소드
    def check_for_dialogue(self, sprite):
        """Checks if a sprite is in the correct location to give dialogue"""
        player = self.player
        tile_x, tile_y = player.location

        if player.direction == 'up':
            if sprite.location == [tile_x, tile_y - 1]:
                self.textbox = DialogueBox(sprite.dialogue)
                sprite.direction = 'down'
                self.talking_sprite = sprite
        elif player.direction == 'down':
            if sprite.location == [tile_x, tile_y + 1]:
                self.textbox = DialogueBox(sprite.dialogue)
                sprite.direction = 'up'
                self.talking_sprite = sprite
        elif player.direction == 'left':
            if sprite.location == [tile_x - 1, tile_y]:
                self.textbox = DialogueBox(sprite.dialogue)
                sprite.direction = 'right'
                self.talking_sprite = sprite
        elif player.direction == 'right':
            if sprite.location == [tile_x + 1, tile_y]:
                self.textbox = DialogueBox(sprite.dialogue)
                sprite.direction = 'left'
                self.talking_sprite = sprite

    #ai캐릭터가 player에게 줄 아이템이 있는지 확인하는 메소드
    def check_for_item(self):
        """Checks if sprite has an item to give to the player"""
        item = self.talking_sprite.item

        if item:
            if item in self.game_data['player inventory']:
                if 'quantity' in self.game_data['player inventory'][item]:
                    if item == 'GOLD':
                        self.game_data['player inventory'][item]['quantity'] += 100
                    else:
                        self.game_data['player inventory'][item]['quantity'] += 1
            else:
                self.add_new_item_to_inventory(item)

            self.update_game_items_info(self.talking_sprite)
            self.talking_sprite.item = None

            if self.talking_sprite.name == 'treasurechest':
                self.talking_sprite.dialogue = ['Empty.']

            if item == 'ELIXIR':
                self.game_data['has brother elixir'] = True
                self.game_data['old man gift'] = 'Fire Blast'
                dialogue = ['Hurry! There is precious little time.']
                self.level.reset_dialogue = self.talking_sprite, dialogue

    #인벤토리에 새로운 아이템을 추가하는 메소드(healing potion, ether potion, elxir, fire blast)
    def add_new_item_to_inventory(self, item):
        inventory = self.game_data['player inventory']
        potions = ['Healing Potion', 'Ether Potion']
        if item in potions:
            inventory[item] = dict([('quantity',1),
                                    ('value',15)])
        elif item == 'ELIXIR':
            inventory[item] = dict([('quantity',1)])
        elif item == 'Fire Blast':
            inventory[item] = dict([('magic points', 40),
                                    ('power', 15)])
        else:
            pass

    #게임 아이템 정보를 업데이트하는 메소드
    def update_game_items_info(self, sprite):
        if sprite.name == 'treasurechest':
            self.game_data['treasure{}'.format(sprite.id)] = False
        elif sprite.name == 'oldmanbrother':
            self.game_data['brother elixir'] = False

    #스프라이트(캐릭터)의 방향을 초기화하여 디폴트 방향을 바라보도록 하는 메소드
    def reset_sprite_direction(self):
        """Reset sprite to default direction"""
        for sprite in self.sprites:
            if sprite.state == 'resting':
                sprite.direction = sprite.default_direction

    #surface에 textbox를 그리는 메소드
    def draw(self, surface):
        """Draws textbox to surface"""
        if self.textbox:
            surface.blit(self.textbox.image, self.textbox.rect)

    #name 값을 참조하여 itembox 혹은 dialoguebox를 선택하여 생성하는 메소드
    def make_textbox(self, name, dialogue, item=None):
        """Make textbox on demand"""
        if name == 'itembox':
            textbox = ItemBox(dialogue, item)
        elif name == 'dialoguebox':
            textbox = DialogueBox(dialogue)
        else:
            textbox = None

        return textbox

    #보물상자를 열면 보물상자의 상태를 변경해주는 메소드(보물상자 객체의 index +1)
    def open_chest(self, sprite):
        if sprite.name == 'treasurechest':
            sprite.index = 1

