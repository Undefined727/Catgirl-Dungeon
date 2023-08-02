from model.visualentity.VisualEntity import VisualEntity
import pygame

class ImageEntity(VisualEntity):
    img = None
    path = "catgirl.png"

    def __init__(self, name = "Default_Image", isShowing = True, xPosition = 0, yPosition = 0, width = 0, height = 0, tags = [], path = "catgirl.png"):
        super().__init__(name, isShowing, xPosition, yPosition, width, height, tags)
        self.updateImg(path)

    def updateImg(self, path):
        self.img = pygame.image.load("sprites/" + path)

    def resize(self, width, height):
        self.width = width
        self.height = height
        print(str(self.width) + " " + str(self.height))
        self.img = pygame.transform.scale(self.img, (self.width, self.height))

    def reposition(self, xPosition, yPosition):
        self.xPosition = xPosition
        self.yPosition = yPosition


    @staticmethod
    def createFrom(json_object):
        newObject = ImageEntity()
        newObject.__dict__.update(json_object)
        newObject.updateImg(newObject.path)
        return newObject