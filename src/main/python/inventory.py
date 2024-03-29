import pygame, time
from view.visualentity.ImageEntity import ImageEntity
from view.visualentity.TextEntity import TextEntity
from view.visualentity.ItemDisplay import ItemDisplay
from view.visualentity.InventoryCharacterEntity import InventoryCharacterEntity
from model.player.Player import Player
from model.Singleton import Singleton
from view.displayHandler import displayEntity
from view.JSONParser import loadJson

visualEntities = []
buttons = []
leaveScreen = False

gameData:Singleton
playerData:Player
screen:pygame.surface

def refreshScreen(screen):
    global visualEntities
    for entity in visualEntities:
         if entity.isShowing:
            displayEntity(entity, screen)

    pygame.display.flip()

def combatButton():
    global leaveScreen
    global gameData
    leaveScreen = True
    gameData.screenOpen = "Combat"

def returnToMapButton():
    global leaveScreen
    global gameData
    leaveScreen = True
    gameData.screenOpen = "Open World"

currentCharacter = 0
def changeCharacterButton():
    global playerData
    global visualEntities
    global currentCharacter
    for entity in visualEntities:
        if type(entity) == InventoryCharacterEntity:
            characterDisplay = entity
    currentCharacter = (currentCharacter+1)%len(playerData.party)
    characterDisplay.changeCharacter(playerData.party[currentCharacter])

def skillSelection():
    global playerData
    global currentCharacter
    global leaveScreen
    global gameData
    leaveScreen = True
    gameData.currentCharacter = playerData.party[currentCharacter]
    gameData.screenOpen = "Skill Selection"

def loadInventory(transferredData):
    global visualEntities
    global buttons
    global gameData
    global playerData
    global screen
    global leaveScreen
    global currentCharacter
    
    leaveScreen = False
    gameData = transferredData
    playerData = gameData.player
    screen = gameData.pygameWindow
    screenX, screenY = screen.get_size()
    FPS = 60
    
    
    loadJson("inventoryScreen.json", screenX, screenY, visualEntities, buttons)

    for entity in visualEntities:
        if type(entity) == ItemDisplay:
            itemDisplay = entity
        if type(entity) == InventoryCharacterEntity:
            characterDisplay = entity

    if (gameData.currentCharacter is not None):
        count = 0
        for char in playerData.party:
            if (char == gameData.currentCharacter):
                currentCharacter = count
                characterDisplay.changeCharacter(playerData.party[currentCharacter])
                break
            else: count += 1
    else:
        characterDisplay.changeCharacter(playerData.party[0])

    
    currInventory = playerData.inventory.getItems()
    currInventorySlot = 0
    itemDisplay.changeItem(currInventory[currInventorySlot].item)
    counter = 0
    for slot in currInventory:
        slotBackground = ImageEntity(f"InventorySlotBackground{counter}", True, 0.02 + counter*0.07, 0.15, 0.06, 0.06*screenX/screenY, [], f"inventorySlotBackground.png", True)
        slotImage = ImageEntity(f"InventorySlot{counter}", True, 0.027 + counter*0.07, 0.15+0.007*screenX/screenY, 0.046, 0.046*screenX/screenY, [], f"items/{slot.item.getPath()}", True)
        slotNumber = TextEntity(f"InventorySlotCount{counter}", True, 0.065 + counter*0.07, 0.24, 0.03, 0.06, [], str(slot.count), "mono", 26)
        slotBackground.scale(screenX, screenY)
        slotImage.scale(screenX, screenY)
        slotNumber.scale(screenX, screenY)
        visualEntities.append(slotBackground)
        visualEntities.append(slotImage)
        visualEntities.append(slotNumber)
        counter += 1


    
    INITIAL_CHANGE_SELECTED_ITEM_DELAY = 40
    AUTO_CHANGE_ITEM_DELAY = 10
    swapItemTimer = INITIAL_CHANGE_SELECTED_ITEM_DELAY
    equipItemDelay = 30

    prev_time = 0
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if (event.type == pygame.MOUSEBUTTONDOWN):
                for entity in buttons:
                    if entity.mouseInRegion(mouse):
                        if (entity.func == "returnToMap"): buttonFunc = returnToMapButton
                        elif (entity.func == "changeCharacter"): buttonFunc = changeCharacterButton
                        elif (entity.func == "skillSelection"): buttonFunc = skillSelection
                        if (len(entity.args) == 0): buttonFunc()
                        elif (len(entity.args) == 1): buttonFunc(entity.args[0])
                        else: buttonFunc(entity.args)
                        break
            ## When the player initially presses a button it will be taken into account here ##
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_LEFT):
                    currInventorySlot -=1
                    if (currInventorySlot < 0): currInventorySlot = len(currInventory) - 1
                    itemDisplay.changeItem(currInventory[currInventorySlot].item)
                    swapItemTimer = INITIAL_CHANGE_SELECTED_ITEM_DELAY
                if (event.key == pygame.K_RIGHT):
                    currInventorySlot +=1
                    if (currInventorySlot >= len(currInventory)): currInventorySlot = 0
                    itemDisplay.changeItem(currInventory[currInventorySlot].item)
                    swapItemTimer = INITIAL_CHANGE_SELECTED_ITEM_DELAY
            if (event.type == pygame.KEYUP):
                if (event.key == pygame.K_LEFT):
                    swapItemTimer = INITIAL_CHANGE_SELECTED_ITEM_DELAY
                if (event.key == pygame.K_RIGHT):
                    swapItemTimer = INITIAL_CHANGE_SELECTED_ITEM_DELAY

        
        ### Held Inputs ###
        keys = pygame.key.get_pressed()
        if (swapItemTimer > 0): swapItemTimer -= 1
        if (equipItemDelay > 0): equipItemDelay -= 1
        

        if (keys[pygame.K_LEFT]):
            if (swapItemTimer <= 0):
                currInventorySlot -=1
                if (currInventorySlot < 0): currInventorySlot = len(currInventory) - 1
                itemDisplay.changeItem(currInventory[currInventorySlot].item)
                swapItemTimer = AUTO_CHANGE_ITEM_DELAY
        elif (keys[pygame.K_RIGHT]):
            if (swapItemTimer <= 0):
                currInventorySlot +=1
                if (currInventorySlot >= len(currInventory)): currInventorySlot = 0
                itemDisplay.changeItem(currInventory[currInventorySlot].item)
                swapItemTimer = AUTO_CHANGE_ITEM_DELAY
    
    
        if (keys[pygame.K_SPACE]):
            playerData.party[currentCharacter].loadout.equip(currInventory[currInventorySlot].item)
            playerData.party[currentCharacter].update()
            characterDisplay.updateCharacter()

        ## Frame Limiter ##
        current_time = time.time()
        dt = current_time - prev_time
        prev_time = current_time
        sleep_time = (1. / FPS) - dt
        if sleep_time > 0:
            time.sleep(sleep_time)

        refreshScreen(screen)
        if (leaveScreen):
            leaveScreen = False 
            break
    return gameData
