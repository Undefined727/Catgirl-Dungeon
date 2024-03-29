from model.openworld.OpenWorldEntity import OpenWorldEntity
from model.openworld.Circle import Circle
from model.character.Character import Character

class Enemy:
    spawnX:int
    spawnY:int
    img:str
    respawnTimer:int
    changeDirectionTimer:int
    enemyMoveDirection:str
    worldObject:OpenWorldEntity
    enemyStats:list[Character]


    def __init__(self, enemyTypes, levels, img, position, database):
        if (len(position) > 1): position = tuple(position)
        self.enemyStats = []
        for i in range(0, len(enemyTypes)):
            self.enemyStats.append(database.fetchCharacter(enemyTypes[i]))
            self.enemyStats[i].changeLevel(levels[i])

        self.spawnX, self.spawnY = position
        self.img = img
        self.respawnTimer = 0
        self.changeDirectionTimer = 0
        self.enemyMoveDirection = "Up"
        self.worldObject = OpenWorldEntity(img, Circle((self.spawnX, self.spawnY), 0.5), "enemy", "attack")

    def setCenter(self, point):
        self.worldObject.setCenter(point)

    def move(self, diff):
        self.worldObject.move(diff)

    def getSprite(self):
        return self.worldObject.getSprite()
    
    def getImagePosition(self):
        return self.worldObject.getImagePosition()