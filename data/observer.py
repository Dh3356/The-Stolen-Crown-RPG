"""
Module for all game observers.
"""

# observer.py 기능 : 게임 내 Observer 기능을 구현한다.

# 모듈: pygame, constants, setup, component(attackitems)
import pygame as pg
from . import constants as c
from . import setup
from .components import attackitems
from . import setup

# Battle 클래스 : 게임 내 전투 메커니즘 구현
class Battle(object):
    """
    Observes events of battle and passes info to components.
    """
    # init 메소드(self, level) : 객체 인스턴스 생성(레벨, 적 observer, 이벤트 종류 딕셔너리)
    def __init__(self, level):
        self.level = level
        self.player = level.player
        self.set_observer_for_enemies()
        self.event_dict = self.make_event_dict()

    # set_observer_for_enemies(self) 메소드 : 적에 대한 observer 추가(observer란 캐릭터의 상태를 표현할 수 있음)
    def set_observer_for_enemies(self):
        for enemy in self.level.enemy_list:
            enemy.observers.append(self)

    # make_event_dict 메소드(self) : observer가 가리키는 캐릭터의 이벤트들을 발생(적 사망 or 데미지, 주인공 데미지)
    def make_event_dict(self):
        """
        Make a dictionary of events the Observer can
        receive.
        """
        event_dict = {c.ENEMY_DEAD: self.enemy_dead,
                      c.ENEMY_DAMAGED: self.enemy_damaged,
                      c.PLAYER_DAMAGED: self.player_damaged}

        return event_dict

    # on_notify(self, event) 메소드 : 발생한 event를 event_dict에서 가져옴
    def on_notify(self, event):
        """
        Notify Observer of event.
        """
        if event in self.event_dict:
            self.event_dict[event]()

    # player_damaged(self) 메소드 : 플레이어가 데미지를 받으면 battle.py의 데미지 상태(enter_player_damaged_state)로 진입
    def player_damaged(self):
        self.level.enter_player_damaged_state()

     # enemy_damaged(self) 메소드 : 적이 데미지를 받으면 battle.py의 데미지 상태(enter_enemy_damaged_state)로 진입
    def enemy_damaged(self):
        """
        Make an attack animation over attacked enemy.
        """
        self.level.enter_enemy_damaged_state()

    # enemy_dead(self) 메소드 : 플레이어가 공격하려는 적이 죽으면 None으로 설정하여 처리
    def enemy_dead(self):
        """
        Eliminate all traces of enemy.
        """
        self.level.player.attacked_enemy = None

# SoundEffects(object) 클래스 : 효과음 설정 클래스
class SoundEffects(object):
    """
    Observer for sound effects.
    """
    # on_notify(self, event) 메소드 : 이벤트에 따라 각기 다른 효과음 출력
    def on_notify(self, event):
        """
        Observer is notified of SFX event.
        """
        if event in setup.SFX:
            setup.SFX[event].play()

# MusicChange(object) 클래스 : 이벤트에 따른 배경음 변경 클래스
class MusicChange(object):
    """
    Observer for special music events.
    """
    # init(self) 메소드 : 이벤트 딕셔너리 인스턴스 생성
    def __init__(self):
        self.event_dict = self.make_event_dict()

    # make_event_dict(self) 메소드 : 게임 승리를 키 값으로, 이에 맞는 배경음을 밸류 값으로 하여 딕셔너리 반환
    def make_event_dict(self):
        """
        Make a dictionary with events keyed to new music.
        """
        new_dict = {c.BATTLE_WON: 'enchanted_festival'}
        return new_dict
    
    # on_notify(self, event) 메소드 : 이벤트 딕셔너리에 해당하는 이벤트 발생 시 이에 맞는 배경음 로드하여 재생
    def on_notify(self, event):
        """
        Observer is notified of change in music.
        """
        if event in self.event_dict:
            new_music = self.event_dict[event]
            if new_music in setup.MUSIC:
                music_file = setup.MUSIC[new_music]
                pg.mixer.music.load(music_file)
                pg.mixer.music.play(-1)



















