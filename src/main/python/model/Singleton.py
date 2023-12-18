from src.main.python.model.character.Character import Character
from src.main.python.view.visualentity.CombatCharacterEntity import CombatCharacterEntity
from src.main.python.model.player.Player import Player
from src.main.python.model.database.DBElementFactory import DBElementFactory
import pygame

class Singleton:
    currentDisplayedParty:list[CombatCharacterEntity]
    currentDisplayedEnemies:list[CombatCharacterEntity]
    currentEnemies:list[Character]
    # For screens that display data for a character specifically, i.e. Skill Selection
    currentCharacter:Character
    player : Player
    currentMap : str
    screenOpen : str
    pygameWindow : pygame.surface
    renderedMapEntities : list
    database_factory : DBElementFactory
    currentWeatherEffect : str
    currentTerrainEffect: str

    def __init__(self, screen, dataFile):
        self.pygameWindow = screen
        self.database_factory = DBElementFactory()
        self.player = Player(self.database_factory)
        self.screenOpen = "Welcome"
        self.currentMap = None
        self.currentEnemies = None
        self.currentCharacter = None
        self.renderedMapEntities = None
        self.currentWeatherEffect = "Fog"
        self.currentTerrainEffect = "None"
        

#global_states = Singleton()