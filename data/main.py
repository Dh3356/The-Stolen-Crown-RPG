from data.states import shop, levels, battle, main_menu, death
from data.states import credits
from . import setup, tools
from . import constants as c


TOWN = 'town'                   # 도시 
MAIN_MENU = 'main menu'         # 메인메뉴
CASTLE = 'castle'               # 왕 거주 성
HOUSE = 'house'
INN = 'Inn'
ARMOR_SHOP = 'armor shop'       # 갑옷(방어) 상점
WEAPON_SHOP = 'weapon shop'     #  무기 상점
MAGIC_SHOP = 'magic shop'       # 마법 상점
POTION_SHOP = 'potion shop'     # 포션(약물) 상점
PLAYER_MENU = 'player menu'     # 사용자 메뉴
OVERWORLD = 'overworld'         
BROTHER_HOUSE = 'brotherhouse'  # 노인의 형제가 거주하는 집
BATTLE = 'battle'   
DUNGEON = 'dungeon'             # 던전1
DUNGEON2 = 'dungeon2'           # 던전2
DUNGEON3 = 'dungeon3'           # 던전3
DUNGEON4 = 'dungeon4'           # 던전4
DUNGEON5 = 'dungeon5'           # 던전5
INSTRUCTIONS = 'instructions'
DEATH_SCENE = 'death scene'
LOADGAME = 'load game'
CREDITS = 'credits'

# 전체 실행 main 메소드
def main():
    """Add states to control here"""
    run_it = tools.Control(setup.ORIGINAL_CAPTION)
    state_dict = {MAIN_MENU: main_menu.Menu(),
                  TOWN: levels.LevelState(TOWN),
                  CASTLE: levels.LevelState(CASTLE),
                  HOUSE: levels.LevelState(HOUSE),
                  OVERWORLD: levels.LevelState(OVERWORLD, True),
                  BROTHER_HOUSE: levels.LevelState(BROTHER_HOUSE),
                  INN: shop.Inn(),
                  ARMOR_SHOP: shop.ArmorShop(),
                  WEAPON_SHOP: shop.WeaponShop(),
                  MAGIC_SHOP: shop.MagicShop(),
                  POTION_SHOP: shop.PotionShop(),
                  BATTLE: battle.Battle(),
                  DUNGEON: levels.LevelState(DUNGEON, True),
                  DUNGEON2: levels.LevelState(DUNGEON2, True),
                  DUNGEON3: levels.LevelState(DUNGEON3, True),
                  DUNGEON4: levels.LevelState(DUNGEON4, True),
                  DUNGEON5: levels.LevelState(DUNGEON5, True),
                  INSTRUCTIONS: main_menu.Instructions(),
                  LOADGAME: main_menu.LoadGame(),
                  DEATH_SCENE: death.DeathScene(),
                  CREDITS: credits.Credits()
                  }

    run_it.setup_states(state_dict, c.MAIN_MENU)
    run_it.main()
