import os, sys, time, pygame, math, random, json
sys.path.append(os.path.abspath("."))
from PIL import Image
import numpy as np
from view.JSONParser import loadJson
from view.displayHandler import displayEntity
from model.openworld.Tile import Tile
from view.visualentity.TextEntity import TextEntity
from view.visualentity.ShapeEntity import ShapeEntity
from view.visualentity.ImageEntity import ImageEntity
from view.visualentity.ScrollBar import ScrollBar
from view.visualentity.Tag import Tag
from view.visualentity.HoverShapeButton import HoverShapeButton
from model.Singleton import Singleton
from model.openworld.worldentities.NPC import NPC

visualEntities = []
buttons = []

quit = False
gameData:Singleton
currentSceneData:list

def refreshMenu():
    global visualEntities
    for entity in visualEntities:
        if entity.isShowing:
            displayEntity(entity, gameData.pygameWindow)
    pygame.display.flip()

def exitButton():
    pygame.quit()

def npcSelectionMenuButton():
    global visualEntities
    for entity in visualEntities:
        if (Tag.EDITOR_NPC_SELECTION in entity.tags):
            entity.isShowing = not entity.isShowing

def npcCreationButton():
    global quit
    global gameData
    quit = True
    gameData.screenOpen = "NPC Creation"

def loadMapEditor(importedData:Singleton):
    global quit
    global visualEntities
    global buttons
    global gameData
    gameData = importedData
    ### Manually write map to open here ###
    opened_map = gameData.currentMap

    ### Visuals and Buttons Stored Globally Here ###
    visualEntities = []
    buttons = []

    ### Global Variables ###
    mouse = [0, 0]
    FPS = 60
    screen = gameData.pygameWindow
    screenX, screenY = screen.get_size()
    prev_time = time.time()
    tileSize = 48
    frameCounter = 0
    buttonPressed = False
    database = gameData.database_factory

    ### Map Data pulled from image ###
    savedMap = Image.open(f"src/main/python/maps/{opened_map}/map.png")
    savedMap = np.array(savedMap)
    displayedMap = savedMap
    height, width, dim = savedMap.shape
    tiles = []

    ### Pull List of Entities on the map ###
    file =  open(f"src/main/python/maps/{opened_map}/entityData.json", 'r')
    entitydata = json.load(file)
    file.close()

    npcdata = database.fetchAllNPCs()
    entityImages = {}
    entityImagesDisplayed = {}

    # Default Spawn Location #
    spawnX = 0
    spawnY = 0

    # Fill entitydata variable with list of entities on the map #
    for entity in entitydata:
        if (entity['type'] == "spawnPoint"):
            spawnX = entity['position'][0]
            spawnY = entity['position'][1]
            img = pygame.image.load(f"src/main/python/sprites/entities/spawn.png")
        elif (entity['type'] == "npc"):
            npcID = entity['id']
            for npc in npcdata:
                if (npc.NPCID == npcID):
                    img = npc.imgPath
            img = pygame.image.load(f"src/main/python/sprites/{img}/overworld.png")
        elif (entity['type'] == "enemy"):
            img = pygame.image.load(f"src/main/python/sprites/entities/{entity['image']}")

        entityImages.update({entity['name']:img})
        img2 = pygame.transform.scale(img, (tileSize, tileSize))
        entityImagesDisplayed.update({entity['name']:img2})
        


    ### Pull List of all tiles ###
    file = open("src/main/python/maps/tileIndex.json", 'r')
    tiledata = json.load(file)
    tileImages = {}
    tileImagesDisplayed = {}

    ## Save images for all tiles ###
    for tile in tiledata:
        img = pygame.image.load(f"src/main/python/sprites/tiles/{tile['image']}")
        tileImages.update({tile['name']:img})
        img2 = pygame.transform.scale(img, (tileSize, tileSize))
        tileImagesDisplayed.update({tile['name']:img2})



    ## Common Functions ##
    

    def convertToScreen(xValue, yValue):
        nonlocal cameraX
        nonlocal cameraY
        xValue = (xValue-cameraX)*tileSize + screenX/2
        yValue = (yValue-cameraY)*tileSize + screenY/2
        return (xValue, yValue)

    def convertToMap(xValue, yValue):
        nonlocal cameraX
        nonlocal cameraY
        xValue = (xValue - screenX/2)/tileSize + cameraX
        yValue = (yValue - screenY/2)/tileSize + cameraY
        return (xValue, yValue)

    def save():
        nonlocal displayedMap
        global gameData
        im = Image.fromarray(displayedMap)
        im.save(f"src/main/python/maps/{gameData.currentMap}/map.png")
        file = open(f"src/main/python/maps/{opened_map}/entityData.json", 'w')
        json.dump(entitydata, file, indent=4)

    def equipTile(tileName):
        nonlocal equippedTileImage
        nonlocal equippedTileName
        nonlocal equippedTileColor
        nonlocal equippedTileSolid
        equippedTileImage.isShowing = True
        equippedTileName = tileName
        if (tileName == "tileNotFound"):
            equippedTileColor = (0, 0, 0)
            equippedTileImage.updateImg("emptyimg.png")
            return
        for tile in tiledata:
            if (tile['name'] == tileName):
                equippedTileColor = tile['color']
                equippedTileSolid = tile['defaultSolid']
                equippedTileImage.updateImg(f"tiles/{tile['image']}")
                break

    def equipNPC(selectedNPCData:NPC):
        nonlocal equippedEntityData
        nonlocal equippedEntityImage
        nonlocal entitydata

        equippedEntityImage.updateImg(selectedNPCData.imgPath)
        equippedEntityImage.isShowing = True
        foundEntity = False
        for entityDataEntry in entitydata:
            if (entityDataEntry['type'] == 'npc'):
                if (entityDataEntry['id'] == selectedNPCData.NPCID):
                    equippedEntityData = entityDataEntry
                    foundEntity = True
        if (not foundEntity):
            jsonAddition = {
            "name": selectedNPCData.NPCName,
            "type": "npc",
            "id": selectedNPCData.NPCID,
            "position": [0,0]
            }
            entitydata.append(jsonAddition)

            img = pygame.image.load(f"src/main/python/sprites/{selectedNPCData.imgPath}/overworld.png")
            entityImages.update({jsonAddition['name']:img})
            img2 = pygame.transform.scale(img, (tileSize, tileSize))
            entityImagesDisplayed.update({jsonAddition['name']:img2})
            equippedEntityData = jsonAddition


    def elevationToggle():
        nonlocal elevationOffsetMode
        nonlocal currentElevationLabel
        nonlocal elevationOffset
        nonlocal equippedTileElevation
        elevationOffsetMode = not elevationOffsetMode
        if (elevationOffsetMode):
            if (elevationOffset >= 0): currentElevationLabel.updateText(f"Current Elevation: +{elevationOffset}")
            else: currentElevationLabel.updateText(f"Current Elevation: -{-1*elevationOffset}")
        else:
            currentElevationLabel.updateText(f"Current Elevation: {equippedTileElevation}")

    currentScrolledTile = 0
    def updateDisplayedTiles(newFirstScrolledTile):
        global visualEntities
        global buttons
        nonlocal tiledata
        nonlocal tileScrollBar
        nonlocal currentScrolledTile
        nonlocal tileSelectionImages

        if (currentScrolledTile == newFirstScrolledTile and not (newFirstScrolledTile == 0)): return
        currentScrolledTile = newFirstScrolledTile

        counter = 0
        for entity in visualEntities[:]:
            if (Tag.EDITOR_TILE_SELECTION in entity.tags and Tag.EDITOR_MENU_ENTRY in entity.tags):
                if (type(entity) == HoverShapeButton): buttons.remove(entity)
                visualEntities.remove(entity)
        

        counter = 0
        for index in range(currentScrolledTile, currentScrolledTile+5):
            if (index > len(tiledata)): break
            if (tiledata[index]['name'] == "tileNotFound"): break
            tile = tiledata[index]
            button = HoverShapeButton(f"Tile_Selection_Button_Entry{counter}", True, 0.025, 0.09 + 0.05*counter, 0.12, 0.05, [Tag.EDITOR_TILE_SELECTION, Tag.EDITOR_MENU_ENTRY], "white", "cyan", "rectangle", "equipTile", [tile['name']])
            visualEntities.append(button)
            buttons.append(button)
            visualEntities.append(TextEntity(f"Tile_Selection_Text_Entry{counter}", True, 0.0625, 0.115 + 0.05*counter, 0.075, 0.05, [Tag.EDITOR_TILE_SELECTION, Tag.EDITOR_MENU_ENTRY], tile['name'], "mono", 20))
            tileSelectionImages[index].reposition(0.11*screenX, (0.095+0.05*counter)*screenY)
            visualEntities.append(tileSelectionImages[index])
            counter += 1

        for entity in visualEntities:
            if (Tag.EDITOR_TILE_SELECTION in entity.tags and Tag.EDITOR_MENU_ENTRY in entity.tags):
                if (not type(entity) == ImageEntity):
                    entity.scale(screenX, screenY)
        buttons.insert(0, buttons.pop(buttons.index(tileScrollBar)))
        visualEntities.append(visualEntities.pop(visualEntities.index(tileScrollBar)))


    # Currently unfinished #
    def fill(location, tile):
        nonlocal width
        nonlocal height
        filledMap = np.append(savedMap, np.zeros([len(savedMap),1]),1)
        print(filledMap)
        #for x in range(0, width):
        #    for y in range(0, height):


    ## Button Functions ##
    def tileSelectionMenuButton():
        nonlocal currentScrolledTile
        displayed = False
        for entity in visualEntities:
            if (Tag.EDITOR_TILE_SELECTION in entity.tags):
                entity.isShowing = not entity.isShowing
                if (entity.isShowing): displayed = True
        if (displayed): 
            print("test")
            updateDisplayedTiles(currentScrolledTile)

    # Scroll Button Function, works with any scroll bar TODO: invidiualize to fix this jank #
    currentlyScrolling = None
    scrollDiff = 0
    def scroll(buttonName):
        nonlocal currentlyScrolling
        nonlocal scrollDiff
        nonlocal mouse

        currentlyScrolling = buttonName
        for entity in visualEntities:
            if (entity.name == currentlyScrolling):
                entity.button.shapeEntity.color = entity.button.secondaryColor
                if (entity.isVertical):
                    scrollDiff = mouse[1] - entity.button.yPosition
                else: 
                    scrollDiff = mouse[0] - entity.button.xPosition
                break











    ### Fill tiles variable with tile information by combining map data and tile data ###
    for y in range(0, height):
        for x in range(0, width):
            tileFound = False
            tileColor = savedMap[y, x][:3]
            tileHeight = savedMap[y, x][3]
            for tile in tiledata:
                if ((tileColor == tile['color']).all()): 
                    tiles.append(Tile(tile['name'], tileHeight, tile['defaultSolid']))
                    tileFound = True
                    break
            if (not tileFound): tiles.append(Tile("tileNotFound", tileHeight,  True))


    ### Pull Menu Structure ###
    loadJson("catgirlDungeoneer.json", screenX, screenY, visualEntities, buttons)

    # Add Fog #
    backgroundHeight = 3*screenY
    backgroundFog = pygame.image.load("src/main/python/sprites/tiles/Gofhres.png").convert()
    backgroundFog = pygame.transform.scale(backgroundFog, (screenX, backgroundHeight))


    ## Set Camera Location ##
    cameraX = spawnX
    cameraY = spawnY


    ## Current Entity attached to the mouse for dragging them around ##
    equippedEntityData = None
    equippedEntityImage = ImageEntity("Equipped_Entity_Image", False, 0, 0, 0.04*screenY/screenX, 0.04, [], f"entities/spawn.png")
    equippedEntityImage.scale(screenX, screenY)
    visualEntities.append(equippedEntityImage)

    ## Current Tile attached to the mouse for dragging them around ##
    equippedTileName = None
    equippedTileImage = ImageEntity("Equipped_Tile_Image", False, 0, 0, 0.04*screenY/screenX, 0.04, [], f"tiles/{tiledata[0]['image']}")
    equippedTileImage.scale(screenX, screenY)
    equippedTileColor = tiledata[0]['color']
    equippedTileSolid = tiledata[0]['defaultSolid']
    visualEntities.append(equippedTileImage)

    ## Current Elevation attached to the mouse for dragging around ##
    equippedTileElevation = 0
    elevationOffsetMode = True
    elevationOffset = 0
    for entity in visualEntities:
        if (entity.name == "Current_Elevation_Label"):
            currentElevationLabel = entity
            break
    for entity in buttons:
        if (entity.name == "ElevationToggleButton"):
            elevationToggleButton = entity
            break


    ## Tile Selection Menu Revealed By Button ##
    menuHeight = 0.3
    visualEntities.append(ShapeEntity("Tile_Selection_Background", False, 0.025, 0.09, 0.12, menuHeight, [Tag.EDITOR_TILE_SELECTION], "White", False, "rectangle"))

    # Save all tile images to be cycled with the scroll bar #
    tileSelectionImages = []
    counter = 0
    for tile in tiledata:
        if (tile['name'] == "tileNotFound"): break
        tileSelectionImages.append(ImageEntity(f"Tile_Selection_Image_Entry{counter}", True, 0.11, 0.095, 0.04*screenY/screenX, 0.04, [Tag.EDITOR_TILE_SELECTION, Tag.EDITOR_MENU_ENTRY], f"tiles/{tile['image']}"))
        tileSelectionImages[counter].scale(screenX, screenY)
        counter += 1

    # Create static menu objects TODO: (move to json later) #
    button = HoverShapeButton(f"Empty_Tile_Selection_Button", False, 0.025, 0.09 + 0.25, 0.12, 0.05, [Tag.EDITOR_TILE_SELECTION], "white", "cyan", "rectangle", "equipTile", ["tileNotFound"])
    visualEntities.append(button)
    buttons.append(button)
    visualEntities.append(TextEntity(f"Empty_Tile_Selection_Text", False, 0.085, 0.115 + 0.25, 0.12, 0.05, [Tag.EDITOR_TILE_SELECTION], "Remove Tile", "mono", 20))

    # Initialize Scroll Bar in Tile Selection menu #
    scrollBarRatio = 0.5
    tileScrollBar = ScrollBar("Tile_Selection_ScrollBar", False, 0.135, 0.09, 0.01, menuHeight-0.05, [Tag.EDITOR_TILE_SELECTION], scrollBarRatio)
    buttons.insert(0, tileScrollBar)
    visualEntities.append(tileScrollBar)

    # Scale created objects for the tile selection menu (this would normally be done in jsonParser but isn't here) #
    for entity in visualEntities:
        if (Tag.EDITOR_TILE_SELECTION in entity.tags):
            entity.scale(screenX, screenY)



    ## Entity Selection Menu (see Tile Selection Menu) ##
    menuHeight = (1+len(npcdata))*0.05
    visualEntities.append(ShapeEntity("NPC_Selection_Background", False, 0.155, 0.09, 0.12, menuHeight, [Tag.EDITOR_NPC_SELECTION], "White", False, "rectangle"))
    counter = 0
    for npc in npcdata:
        button = HoverShapeButton(f"NPC_Selection_Button_Entry{counter}", False, 0.155, 0.09 + 0.05*counter, 0.12, 0.05, [Tag.EDITOR_NPC_SELECTION], "white", "cyan", "rectangle", "equipNPC", [npc])
        visualEntities.append(button)
        buttons.append(button)
        visualEntities.append(TextEntity(f"NPC_Selection_Text_Entry{counter}", False, 0.1925, 0.115 + 0.05*counter, 0.075, 0.05, [Tag.EDITOR_NPC_SELECTION], npc.NPCName, "mono", 20))
        visualEntities.append(ImageEntity(f"NPC_Selection_Image_Entry{counter}", False, 0.24, 0.095 + 0.05*counter, 0.04*screenY/screenX, 0.04, [Tag.EDITOR_NPC_SELECTION], f"{npc.imgPath}/overworld.png"))
        counter += 1
    button = HoverShapeButton(f"Add_NPC_Selection_Button", False, 0.155, 0.09 + 0.05*counter, 0.12, 0.05, [Tag.EDITOR_NPC_SELECTION], "white", "cyan", "rectangle", "equipNPC", ["npcNotFound"])
    visualEntities.append(button)
    buttons.append(button)
    visualEntities.append(TextEntity(f"Add_NPC_Selection_Text", False, 0.215, 0.115 + 0.05*counter, 0.12, 0.05, [Tag.EDITOR_NPC_SELECTION], "Add NPC", "mono", 20))
    for entity in visualEntities:
        if (Tag.EDITOR_NPC_SELECTION in entity.tags):
            entity.scale(screenX, screenY)


    ### Running Editor ###
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()


            # Handle pressing buttons #    
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                buttonPressed = False
                for button in buttons:
                    if button.isShowing:
                        if (type(button) == ScrollBar): button = button.button
                        if button.mouseInRegion(mouse):
                            buttonPressed = True
                            if (button.func == "exit"): buttonFunc = exitButton
                            elif (button.func == "NPCCreation"): buttonFunc = npcCreationButton
                            elif (button.func == "tileSelection"): buttonFunc = tileSelectionMenuButton
                            elif (button.func == "npcSelection"): buttonFunc = npcSelectionMenuButton
                            elif (button.func == "equipTile"): buttonFunc = equipTile
                            elif (button.func == "equipNPC"): buttonFunc = equipNPC
                            elif (button.func == "elevationToggle"): buttonFunc = elevationToggle
                            elif (button.func == "scroll"): buttonFunc = scroll
                            if (len(button.args) == 0): buttonFunc()
                            else: buttonFunc(*button.args)
                            break
                
                # If you click not on a button (picking up an entity) #
                if (not buttonPressed):
                    mouseX, mouseY = convertToMap(mouse[0], mouse[1])
                    mouseX = math.floor(mouseX)
                    mouseY = math.floor(mouseY)
                    for entity in entitydata:
                        if (entity['position'] == [mouseX, mouseY]):
                            equippedEntityData = entity
                            equippedEntityImage.isShowing = True
                            buttonPressed = True

                            if (entity['type'] == "npc"):
                                for npc in npcdata:
                                    if (npc.NPCID == entity['id']):
                                        equippedEntityImage.updateImg(f"{npc.imgPath}/overworld.png")
                                        break
                            elif (equippedEntityData['type'] == "spawnPoint"):
                                equippedEntityImage.updateImg("entities/spawn.png")
                            else: equippedEntityImage.updateImg(f"entities/{entity['image']}")

            # Right click (delete) #
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
                deletedObject = False
                mouseX, mouseY = convertToMap(mouse[0], mouse[1])
                mouseX = math.floor(mouseX)
                mouseY = math.floor(mouseY)
                for entity in entitydata:
                    if (entity['position'] == [mouseX, mouseY]):
                        if (not entity['name'] == "Player Spawn"):
                            entitydata.remove(entity)
                        deletedObject = True
                        break

                # If you didn't delete an entity (remove equipped tile/elevation) #
                if (not deletedObject):
                    equippedTileName = None
                    equippedTileImage.isShowing = False
                    elevationOffsetMode = False
                    elevationOffset = 0
                    elevationToggle()

            # Let go of the mouse #
            if event.type == pygame.MOUSEBUTTONUP:
                # If scrolling release the scroll bar #
                if (not currentlyScrolling is None):
                    for entity in visualEntities:
                        if (entity.name == currentlyScrolling):
                            entity.button.shapeEntity.color = entity.button.primaryColor
                            break
                    currentlyScrolling = None

                # No longer pressing a button #
                buttonPressed = False

                # Allow for changing tile elevations with an offset again #
                for tile in tiles:
                    tile.justChanged = False

                # Drop held entity where mouse is #
                if (not equippedEntityData is None):
                    mouseX, mouseY = convertToMap(mouse[0], mouse[1])
                    mouseX = math.floor(mouseX)
                    mouseY = math.floor(mouseY)
                    equippedEntityImage.isShowing = False
                    for entity in entitydata:
                        if (entity['name'] == equippedEntityData['name']): 
                            entity['position'] = [mouseX, mouseY]
                    equippedEntityData = None

            # Scroll Wheel #        
            if event.type == pygame.MOUSEWHEEL:
                # If over the elevation button change its value #
                if (elevationToggleButton.mouseInRegion(mouse)):
                    if (elevationOffsetMode): 
                        elevationOffset += event.y
                        if (elevationOffset >= 0): currentElevationLabel.updateText(f"Current Elevation: +{elevationOffset}")
                        else: currentElevationLabel.updateText(f"Current Elevation: -{-1*elevationOffset}")
                    else: 
                        equippedTileElevation += event.y
                        currentElevationLabel.updateText(f"Current Elevation: {equippedTileElevation}")
                # If not over the elevation button scroll in/out #
                else:
                    tileSize += 2*event.y
                    if (tileSize <= 0): tileSize = 1
                    for entity in entityImagesDisplayed:
                        entityImagesDisplayed[entity] = pygame.transform.scale(entityImages[entity], (tileSize, tileSize))
                    for tile in tileImagesDisplayed:
                        tileImagesDisplayed[tile] = pygame.transform.scale(tileImages[tile], (tileSize, tileSize))

            # If the mouse moves #
            if event.type == pygame.MOUSEMOTION:
                # Highlight buttons that are highlighted if the mouse is over them #
                for button in buttons:
                    if (type(button) == HoverShapeButton):
                        button.mouseInRegion(mouse)

                # Move tile/entity attached to the cursor #
                equippedTileImage.xPosition = mouse[0]
                equippedTileImage.yPosition = mouse[1]
                equippedEntityImage.xPosition = mouse[0]-tileSize/2
                equippedEntityImage.yPosition = mouse[1]-tileSize/2

                # Move scroll bar if you are dragging one #
                if (not currentlyScrolling is None):
                    for entity in visualEntities:
                        if (entity.name == currentlyScrolling):
                            if (entity.isVertical):
                                newPos = mouse[1] - scrollDiff
                                if (newPos < entity.yPosition): entity.button.reposition(entity.button.xPosition, entity.yPosition)
                                elif (newPos > (entity.yPosition + entity.height*(1-entity.ratio))):
                                    entity.button.reposition(entity.xPosition, entity.yPosition + entity.height*(1-entity.ratio))
                                else:
                                    entity.button.reposition(entity.button.xPosition, mouse[1] - scrollDiff)
                            else:
                                newPos = mouse[0] - scrollDiff
                                if (newPos < entity.xPosition): entity.button.reposition(entity.button.xPosition, entity.yPosition)
                                elif (newPos > (entity.xPosition + entity.width*(1-entity.ratio))):
                                    entity.button.reposition(entity.button.xPosition + entity.width*(1-entity.ratio), entity.yPosition)
                                else:
                                    entity.button.reposition(mouse[0] - scrollDiff, entity.yPosition)

                    if (currentlyScrolling == "Tile_Selection_ScrollBar"): 
                        currDraggedRatio = (tileScrollBar.button.yPosition - tileScrollBar.yPosition)/(tileScrollBar.height - tileScrollBar.height*ratio)
                        if (currDraggedRatio < 0): currDraggedRatio = 0
                        if (currDraggedRatio > 1): currDraggedRatio = 1
                        currTile = round(currDraggedRatio*(len(tiledata)-1))
                        updateDisplayedTiles(currTile)




        ### Inputs ###
        keys = pygame.key.get_pressed()
        keymods = pygame.key.get_mods()
        movementSpeed = (screenY/tileSize)*0.01

        # If you press the mouse and aren't pressing a button place a tile/elevation TODO: move to the event section that handles pressing the mouse #
        if (pygame.mouse.get_pressed()[0] and not buttonPressed):
            mouseX, mouseY = convertToMap(mouse[0], mouse[1])
            mouseX = math.floor(mouseX)
            mouseY = math.floor(mouseY)
            if (mouseX < 0): mouseX = 0
            if (mouseY < 0): mouseY = 0
            if (mouseX >= width): mouseX = width-1
            if (mouseY >= height): mouseY = height-1
            if (not equippedTileName is None): displayedMap[mouseY, mouseX][:3] = equippedTileColor
            if (not tiles[width*mouseY + mouseX].justChanged):
                if (not equippedTileName is None): tiles[width*mouseY + mouseX].name = equippedTileName
                if (elevationOffsetMode): 
                    tiles[width*mouseY + mouseX].height = displayedMap[mouseY, mouseX][3] + elevationOffset
                    displayedMap[mouseY, mouseX][3] = displayedMap[mouseY, mouseX][3] + elevationOffset
                else: 
                    tiles[width*mouseY + mouseX].height = equippedTileElevation
                    displayedMap[mouseY, mouseX][3] = equippedTileElevation
                if (not equippedTileName is None): tiles[width*mouseY + mouseX].solid = equippedTileSolid
                tiles[width*mouseY + mouseX].justChanged = True

        # Move around the camera with the arrow keys #
        if (keys[pygame.K_LEFT] and keys[pygame.K_UP]):
            cameraX += -0.707*movementSpeed
            cameraY += -0.707*movementSpeed
        elif (keys[pygame.K_LEFT] and keys[pygame.K_DOWN]):
            cameraX += -0.707*movementSpeed
            cameraY += 0.707*movementSpeed
        elif (keys[pygame.K_LEFT]):
            cameraX += -movementSpeed
        elif (keys[pygame.K_RIGHT] and keys[pygame.K_UP]):
            cameraX += 0.707*movementSpeed
            cameraY += -0.707*movementSpeed
        elif (keys[pygame.K_RIGHT] and keys[pygame.K_DOWN]):
            cameraX += 0.707*movementSpeed
            cameraY += 0.707*movementSpeed
        elif (keys[pygame.K_RIGHT]):
            cameraX += movementSpeed
        elif (keys[pygame.K_UP]):
            cameraY += -movementSpeed
        elif (keys[pygame.K_DOWN]):
            cameraY += movementSpeed


        # Save the map when you press ctrl+s #
        if (keymods and pygame.KMOD_CTRL and keys[pygame.K_s]):
            save()
            print("saved")



        ## Display ##
        screen.fill((0, 0, 0))
        fogParallax = 0.2
        ratio = ((frameCounter%6000)/6000)
        bgY = (ratio*backgroundHeight) - fogParallax*cameraY*tileSize
        bgY2 = bgY - backgroundHeight
        bgY3 = bgY + backgroundHeight


        bgY -= screenY
        bgY2 -= screenY
        bgY3 -= screenY
        screen.blit(backgroundFog, (0, bgY))
        screen.blit(backgroundFog, (0, bgY2))
        screen.blit(backgroundFog, (0, bgY3))

        ## Show Tiles ##
        for x in range(0, width):
            for y in range(0, height):
                screen.blit(tileImagesDisplayed[tiles[width*y + x].name], (convertToScreen(x, y)))

        ## Show Entities ##
        for entity in entitydata:
            screen.blit(entityImagesDisplayed[entity['name']], (convertToScreen(*entity['position'])))
                
            
        LINE_THICKNESS = 1
        elevationMarkerTextFont = pygame.font.SysFont("mono", int(tileSize/3))
        ## Show Hitboxes and Elevation ##
        for x in range(0, width):
            for y in range(0, height):
                if (not tiles[width*y + x].name == "tileNotFound"):
                        if (tiles[width*y + x].solid): 
                            pygame.draw.line(screen, "Purple", convertToScreen(x, y), convertToScreen(x, y+1), LINE_THICKNESS)
                            pygame.draw.line(screen, "Purple", convertToScreen(x+1, y), convertToScreen(x+1, y+1), LINE_THICKNESS)
                            pygame.draw.line(screen, "Purple", convertToScreen(x, y), convertToScreen(x+1, y), LINE_THICKNESS)
                            pygame.draw.line(screen, "Purple", convertToScreen(x, y+1), convertToScreen(x+1, y+1), LINE_THICKNESS)
                        else:
                            textLabel = elevationMarkerTextFont.render(str(tiles[width*y + x].height), False, "Red")
                            textRect = textLabel.get_rect()
                            textRect.center = convertToScreen(x+0.75, y+0.75)
                            screen.blit(textLabel, textRect)
                            if (x < width-1 and (not tiles[width*y + x+1].name == "tileNotFound") and (not tiles[width*y + x+1].solid)):
                                heightDiff = abs(int(tiles[width*y + x].height) - int(tiles[width*y + x+1].height))
                                if (heightDiff == 1): pygame.draw.line(screen, "Yellow", convertToScreen(x+1, y), convertToScreen(x+1, y+1), LINE_THICKNESS)
                                elif (heightDiff > 1): pygame.draw.line(screen, "Red", convertToScreen(x+1, y), convertToScreen(x+1, y+1), LINE_THICKNESS)
                            if (y < height-1 and (not tiles[width*(y+1) + x].name == "tileNotFound") and (not tiles[width*(y+1) + x].solid)):
                                heightDiff = abs(int(tiles[width*y + x].height) - int(tiles[width*(y+1) + x].height))
                                if (heightDiff == 1): pygame.draw.line(screen, "Yellow", convertToScreen(x, y+1), convertToScreen(x+1, y+1), LINE_THICKNESS)
                                elif (heightDiff > 1): pygame.draw.line(screen, "Red", convertToScreen(x, y+1), convertToScreen(x+1, y+1), LINE_THICKNESS)

        refreshMenu()

        ## Frame Limiter ##
        frameCounter += 1
        current_time = time.time()
        dt = current_time - prev_time
        prev_time = current_time
        sleep_time = (1. / FPS) - dt
        if sleep_time > 0:
            time.sleep(sleep_time)

        ## Quit ##
        if (quit):
            quit = False
            break
    return gameData