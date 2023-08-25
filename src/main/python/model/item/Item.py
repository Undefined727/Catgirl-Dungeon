from sqlalchemy.engine.row import Row
from src.main.python.model.item.ItemSlot import ItemSlot
from src.main.python.model.item.ItemTag import ItemTag
from src.main.python.model.effect.EffectType import EffectType
import uuid

class Item:
    id : str
    name : str
    slots : list[ ItemSlot ]
    item_tags : list[ ItemTag ]
    item_bonuses : dict[ EffectType, int ]
    description : str
    #Statuses below when implemented

    def __init__(self, name:str = "Placeholder Name", slots:list[ItemSlot] = [ItemSlot.WEAPON], description:str = "", item_tags:list[ItemTag] = list()):
        self.id = str(uuid.uuid5(uuid.NAMESPACE_DNS,"basedstudios.dev"))
        self.name = name
        self.slots = slots
        self.description = description
        self.item_tags = item_tags

    def getSlot(self):
        return self.slot

    def toDatabaseItem(self):
        return {
            'id' : self.id,
            'name': self.name,
            'item_slot' : self.slot.name,
            'description': self.description
        }