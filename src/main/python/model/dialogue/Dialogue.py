from model.item.Item import Item
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from model.database.DatabaseModels import engine, DBDialogue

class Dialogue:
    id : int
    tag : str
    leading_text : str
    content : str
    character_id : int
    emotion : str
    reward_friendship : int
    reward_xp : int
    reward_items : dict [ Item : int ]
    follow_up = None

    def __init__(self,
                 id : int = 0,
                 tag : str = "",
                 leading_text : str = "",
                 content : str = "",
                 character_id : int = 0,
                 emotion : str = "",
                 reward_friendship : int = 0,
                 reward_xp : int = 0):
        
        self.id = id
        self.setTag(tag)
        self.setLeadingText(leading_text)
        self.setContent(content)
        self.setCharacterID(character_id)
        self.setEmotion(emotion)
        self.setFriendshipRewards(reward_friendship)
        self.setXPRewards(reward_xp)

    ## Getters ##
    def getID(self) -> int:
        return self.id

    def getTag(self) -> str:
        return self.tag

    def getContent(self) -> str:
        return self.content
    
    def getLeadingText(self) -> str:
        return self.leading_text

    def getCharacterID(self) -> str:
        return self.character

    def getEmotion(self) -> str:
        return self.emotion

    def getFriendshipRewards(self) -> int:
        return self.reward_friendship

    def getXPRewards(self) -> int:
        return self.reward_xp

    def getItemRewards(self) -> dict [ Item : int ]:
        return self.reward_items

    def getFollowUpQuest(self):
        return self.follow_up

    ## Setters ##
    def setTag(self, new_tag : str):
        self.tag = new_tag

    def setLeadingText(self, leading_text : str):
        self.leading_text = leading_text    

    def setContent(self, new_content : str):
        self.content = new_content

    def setCharacterID(self, new_character : str):
        self.character = new_character

    def setEmotion(self, new_emotion : str):
        self.emotion = new_emotion

    def setFriendshipRewards(self, new_friendship_value : int):
        self.friendship = new_friendship_value

    def setItemRewards(self, new_items : dict [ Item : int ]):
        self.reward_items = new_items

    def setXPRewards(self, new_xp : int):
        self.reward_xp = new_xp

    def setFollowUpQuest(self, new_quest):
        self.follow_up = new_quest

    ## Misc ##
    def __eq__(self, another_object) -> bool:
        if type(self) != type(another_object):
            return False
        if self.getID() == another_object.getID() and self.getContent() == another_object.getContent():
            return True

    def __hash__(self) -> int:
        return hash((self.id, self.tag, self.character_id, self.emotion))

    def __repr__(self) -> str:
        result = f"ID: {self.getID()}"
        result += f"   Tag: {self.getTag()}\n"
        result += f"Character: {self.getCharacterID()}"
        result += f"   Character expression: {self.getEmotion()}\n"
        result += f"Content: {self.getContent()}\n"
        result += f"Rewards:\n"
        result += f"Friendship: {self.getFriendshipRewards()}    "
        result += f"XP: {self.getXPRewards()}\n"
        result += f"Items: {self.getItemRewards()}\n"
        return result

    # @staticmethod
    # def generateID() -> int:
    #     with Session(engine) as session:
    #         query = session.query(func.max(DBDialogue.id)).all()
    #         max_id = query[0][0]
    #         return max_id + 1

    ## TODO implement ##