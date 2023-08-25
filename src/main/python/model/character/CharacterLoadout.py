from src.main.python.util.Messages import Error
from src.main.python.model.item.Item import Item
from src.main.python.model.item.ItemSlot import ItemSlot
from src.main.python.model.effect.EffectType import EffectType
from src.main.python.util.IllegalArgumentException import IllegalArgumentException

class CharacterLoadout:
    slots : dict[ ItemSlot, Item ]

    def __init__(self, slots : dict[ ItemSlot, Item ] = {
        ItemSlot.HEAD : None,
        ItemSlot.CHEST : None,
        ItemSlot.LEGS : None,
        ItemSlot.WAIST : None,
        ItemSlot.WEAPON : None,
        ItemSlot.ACCESSORY1 : None,
        ItemSlot.ACCESSORY2 : None
    }):
        self.slots = slots

    def isSlotEmpty(self, slot : ItemSlot) -> bool:
        if slot not in self.slots: raise IllegalArgumentException(Error.INEXISTENT_SLOT)
        return self.slots is None

    def equip(self, item : Item) -> list[ ItemSlot ]:
        for slot in item.getSlots():
            if slot not in self.slots: raise IllegalArgumentException(Error.INEXISTENT_SLOT)
            if self.slots[slot] is not None: raise IllegalArgumentException(Error.SLOT_TAKEN)
        for slot in item.getSlots(): self.slots[slot] = item
        return item.getSlots()

    def unequip(self, slot : ItemSlot) -> Item:
        if slot not in self.slots: raise IllegalArgumentException(Error.INEXISTENT_SLOT)
        if self.slots[slot] is None: raise IllegalArgumentException(Error.NO_ITEM)
        item = self.slots[slot]
        for slot in item.getSlots(): self.slots[slot] = None
        return item

    def getBonuses(self) -> dict[ EffectType, int ]:
        result = dict()
        for key in self.slots:
            item = self.slots.get(key)
            item_bonuses = item.getBonuses()
            for bonus in item_bonuses:
                if bonus in result: result[bonus] += item_bonuses[bonus]
                result[bonus] = item_bonuses[bonus]
        return result