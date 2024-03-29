from model.effect.EffectTag import EffectTag
from model.effect.EffectType import EffectType
#from util.IDHandler import IDHandler
from util.IllegalArgumentException import IllegalArgumentException

class Effect:
    id: str
    name: str
    effect_type : EffectType
    value: int
    duration : int
    tags : list[ EffectTag ]

    def __init__(self, name = "Placeholder Name", eff_type : EffectType = EffectType.NONE, value : int = 0, duration : int = -1, tags : list[ EffectTag ] = [], id : str = None):
        if id is None: 
            raise IllegalArgumentException("no id")
            #self.setID(IDHandler.generateID(Effect))
        else: self.setID(id)
        self.setName(name)
        self.setType(eff_type)
        self.setValue(value)
        self.setDuration(duration)
        self.setTags(tags)

    def getDuration(self) -> int:
        return self.duration_current

    def getName(self) -> str:
        return self.name

    def getTags(self) -> list[ EffectTag ]:
        return self.tags

    def getType(self) -> EffectType:
        return self.effect_type

    def getValue(self) -> int:
        return self.value

    def getID(self) -> str:
        return self.id

    def setDuration(self, new_duration : int):
        if (new_duration < 0 and new_duration != -1):
            raise IllegalArgumentException("Invalid duration for an effect")
        self.duration_current = new_duration

    def setName(self, new_name : str):
        self.name = new_name

    def setTags(self, tags:[]):
        self.tags = tags

    def setType(self, new_type : EffectType):
        self.effect_type = new_type

    def setValue(self, new_value : int):
        self.value = new_value

    def setID(self, new_id : str):
        self.id = new_id

    def addTag(self, tag : EffectTag):
        self.tags.append(tag)

    def removeTag(self, tag : EffectTag):
        self.tags.remove(tag)

    def isExpired(self) -> bool:
        return self.duration_current == 0

    def isPermanent(self) -> bool:
        return self.duration_current == -1

    def update(self):
        if (self.duration_current() > 0):
            self.duration_current -= 1

    def equals(self, another_effect):
        if type(self) != type(another_effect): return False
        if self.getType() != another_effect.getType(): return False
        if self.name != another_effect.name: return False
        return True