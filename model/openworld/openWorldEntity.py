from model.openworld.Circle import Circle
from model.openworld.Rectangle import Rectangle
import model.openworld.ShapeMath as ShapeMath
from model.character.Character import Character
import pygame

class openWorldEntity:
    accX = 0
    accY = 0
    speedX = 0
    speedY = 0
    
    name = "default_name"
    currentHeight = 0
    shape = Circle(0, 0)
    imgPath = "nekoarc.png"
    img = pygame.image.load("sprites/nekoarc.png")
    rotImg = img
    currentRotation = 0
    # entityType replaced by some sort of enum/database later maybe
    # For now we have Grass, and Enemy for entityType
    # "data" has whatever data matches the type, so the enemy/enemies for Enemy and whatever the grass drops
    # "trigger" is the type of entity that activates the entity with whatever data is contained within it
    # This will likely be replaced with a dictionary later so different triggers can cause different effects
    entityType = "grass"
    data = Character("Wizard", "wizard.png", 5)
    trigger = "attack"

    def __init__(self, imgPath, shape, entityType, data, trigger):
        self.shape = shape
        self.imgPath = imgPath
        self.entityType = entityType
        self.data = data 
        self.trigger = trigger
        self.name = imgPath


        img = pygame.image.load("sprites/" + imgPath)
        imgSize = shape.getImageSize()
        self.img = pygame.transform.scale(img, imgSize)
        self.rotImg = self.img
        self.currentRotation = 0
    
    def rotate(self, angle, pivot):
        self.currentRotation -= angle
        self.currentRotation %= 360
        ShapeMath.rotate(self.shape, angle, pivot)
        self.rotImg = pygame.transform.rotate(self.img, self.currentRotation)
    
    def getSprite(self):
        return self.rotImg
    
    def getImagePosition(self):
        return self.shape.getImagePosition()
    
    def getCenter(self):
        return self.shape.getCenter()

