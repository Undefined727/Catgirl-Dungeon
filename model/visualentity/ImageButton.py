from PIL import Image
from model.visualentity.VisualEntity import VisualEntity
from model.visualentity.ImageEntity import ImageEntity
import numpy, pygame

class ImageButton(VisualEntity):
    func = None
    args = None
    npArray = None
    img = None
    isActive = True
    isShowing = True
    path = "nekoarc.png"

    def __init__(self, name = "Default_Image_Button", isShowing = True, xPosition = 0, yPosition = 0, width = 0, height = 0, tags = [], path = "nekoarc.png", func = None, args = [], isActive = True):
        super().__init__(name, isShowing, xPosition, yPosition, width, height, tags)
        self.func = func
        self.args = args
        self.img = ImageEntity("Button_Image", isShowing, xPosition, yPosition, width, height, tags, path)
        self.isActive = isActive
           

    def mouseInRegion(self, mouse):
        x = int(mouse[0]-self.xPosition)
        y = int(mouse[1]-self.yPosition)
        if (x >= 0 and x < int(self.width) and y >= 0 and y < int(self.height)): 
            transparency = self.npArray[y, x, 3]
            if (transparency != 0): return True
        return False
    
    def resize(self, width, height):
        self.width = width
        self.height = height

    def reposition(self, xPosition, yPosition):
        self.xPosition = xPosition
        self.yPosition = yPosition

    def scale(self, screenX, screenY):
        self.resize(self.width*screenX, self.height*screenY)
        self.reposition(self.xPosition*screenX, self.yPosition*screenY)
        self.img.scale(screenX, screenY)
        PILimg = Image.open("sprites/" + self.path).convert('RGBA')
        PILimg = PILimg.resize((int(self.width), int(self.height)))
        self.npArray = numpy.asarray(PILimg)

    def buttonVisual(self):
        return self.img

    @staticmethod
    def createFrom(json_object):
        newObject = ImageButton()
        newObject.__dict__.update(json_object)
        newObject.img = ImageEntity("Button_Image", newObject.isShowing, newObject.xPosition, newObject.yPosition, newObject.width, newObject.height, newObject.tags, newObject.path)
        return newObject