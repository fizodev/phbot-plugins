from phBot import *
from threading import Timer
from datetime import datetime, timedelta
from time import sleep
import urllib.request
import datetime
import phBotChat
import subprocess
import signal
import QtBind
import struct
import random
import json
import os
import sqlite3

pName = 'Control_AIO'
pVersion = '1.2.0'

# ______________________________ Initializing ______________________________ #

# Globals
slot = []
inGame = None
followActivated = False
stopPicking=True
followPlayer = ''
followDistance = 0
StartBotAt = 0
CloseBotAt = 0
CheckStartTime = False
CheckCloseTime = False
SkipCommand1 = False
SkipCommand2 = False
SkipCommand3 = False
delay_counter = 0
path = get_config_dir()[:-7]
drops = {}

# Graphic user interface
gui = QtBind.init(__name__,"ControlAIO")
QtBind.createLabel(gui,'Control your party using in-game chat. Leader writes commands and your character will follow it.',11,11)

QtBind.createLabel(gui,'<- This ControlAIO have many features more than the normal xControl  ->    ',11,30)
QtBind.createLabel(gui,'- ( S ) : Start bot\n- ( SP ) : Stop bot\n- ( T ) : to make them trace you ( TT ) #name to trace player\n- ( N ) : Stop trace\n- ( R ) : Use some "Return Scroll" from your inventory\n- TP #A #B : Use teleport from location A to B\n- RECALL #Town : Set recall on city portal\n- ZERK : Use berserker mode if is available\n- ( G ) : Left party\n- MOVEON #Radius? : Set a random movement\n- ( M ) #PetType? : Mount horse by default\n- ( D ) #PetType? : Dismount horse by default\n- ( SET )  #PosX? #PosY? #Region? #PosZ? : Set training position\n- ( SETR ) #Radius? : Set training radius\n- ( SETS ) #Path? : Change script path for training area\n- ( SETA ) #Name : Changes training area by config name\n- ( PROFILE ) #Name? : Loads a profile by his name\n- DC : Disconnect from game',15,45)
QtBind.createLabel(gui,'- INJECT #Opcode #Encrypted? #Data? : Inject packet\n- CHAT #Type #Message : Send any message type\n- ( F ) #Player? #Distance? : Trace a party player using distance\n- ( NF ) : Stop following\n- JUMP : Generate knockback visual effect\n- SIT : Sit or Stand up, depends\n- CAPE #Type? : Use PVP Cape\n- EQUIP #ItemName : Equips an item from inventory\n- UNEQUIP #ItemName : Unequips item from character\n- REVERSE #Type #Name?\n- GETPOS : Gets current position\n- USE #ItemName : Use item from inventory\n- USE Transport : Use transport from inventory\n- TERMINATE : Terminate current transport',345,80)
QtBind.createLabel(gui,'v'+pVersion+'  Made by ❴ Orsa ❵ ✔',580,280)

# Graphic user interface (*)
gui_ = QtBind.init(__name__,"P1 ( Args )")

QtBind.createLabel(gui_,'<- This Page Have Extra Codes In The ControlAIO 1 Using it in Script ->',210,11)
QtBind.createLabel(gui_,'- LeaveParty : Ex. LeaveParty .. Putting in Script LeaveParty He Will Leave Party\n- Notification : Ex. Notification,title,message ..show a windows notification, bot must be minimized\n- NotifyList : Ex. NotifyList,message .. Create a notification in the list\n- PlaySound : Ex. PlaySound,ding.wav ... wav file must be in your phbot folder\n- SetScript : Ex. SetScript,Mobs103.txt .. script must be in your phbot folder\n- StartBot : Ex. StartBot,in,5 .. Starts bot in 5 mins ,, StartBot,at,05:30 .. Starts bot at specified time.. 24hour clock\n- CloseBot : Ex. CloseBot ..kills the bot immediately ,, CloseBot,in,5 ... kills the bot in 5 mins ,, \n   CloseBot,at,05:30 ..kills the bot at a specific time.. 24hour clock\n- GoClientless : Ex. GoClientless .. Kills the Client instantly\n- StopStart : Ex. StopStart .. Stops and starts the bot 5 second later\n- StartTrace : Ex. StartTrace,player ..Starts tracing a player\n- WaitParty : Ex. WaitParty,8 It will stop bot and wait untill party become 8/8 to continue botting',15,45)
QtBind.createLabel(gui_,'v'+pVersion+'  Made by ❴ Orsa ❵ ✔',580,280)

# Graphic user interface (+)
gui__ = QtBind.init(__name__,"P1 ( Town )")

QtBind.createLabel(gui__,'<- This Page Have Extra Codes In The ControlAIO 1 ->',230,11)
QtBind.createLabel(gui__,'╔══════════════════▶ HWT TP ◀═══════════════════╗',20,45)
QtBind.createLabel(gui__,'- ( KP1 ) : If you want to go Holy Water Temple (Beginner) لو عايز تروح\n- ( KP2 ) : If you want to go Holy Water Temple (Intermediate)لو عايز تروح\n- ( KP3 ) : If you want to go Holy Water Temple (Advance) لو عايز تروح',28,60 )
QtBind.createLabel(gui__,'║',20,57)
QtBind.createLabel(gui__,'║',380,57)
QtBind.createLabel(gui__,'║',20,69)
QtBind.createLabel(gui__,'║',380,69)
QtBind.createLabel(gui__,'║',20,81)
QtBind.createLabel(gui__,'║',380,81)
QtBind.createLabel(gui__,'║',20,89)
QtBind.createLabel(gui__,'║',380,89)
QtBind.createLabel(gui__,'╚════════════════════════════════════════════╝',20,100)
QtBind.createLabel(gui__,'╔════════════════▶ Juipter ',390,45)
QtBind.createLabel(gui__,'TP ◀═══════════════╗',569,45)
QtBind.createLabel(gui__,'- ( J5 ) : If you want to go Juipter Temple ( Room 5 ) لو عايز تروح\n- ( J6 ) : If you want to go Juipter Temple ( Room 6 ) لو عايز تروح ',398,65 )
QtBind.createLabel(gui__,'║',390,57)
QtBind.createLabel(gui__,'║',710,57)
QtBind.createLabel(gui__,'║',390,69)
QtBind.createLabel(gui__,'║',710,69)
QtBind.createLabel(gui__,'║',390,81)
QtBind.createLabel(gui__,'║',710,81)
QtBind.createLabel(gui__,'║',390,89)
QtBind.createLabel(gui__,'║',710,89)
QtBind.createLabel(gui__,'╚═══════════════════════════════════════╝',390,100)
QtBind.createLabel(gui__,'╔════════════════════════▶ Town ',150,120)
QtBind.createLabel(gui__,'TP ◀════════════════════════╗',385,120)
QtBind.createLabel(gui__,'- ( J ) : If you in any town and want to go Jangan لو انت في اي تاون وعايز تروح\n- ( DW ) : If you in any town and want to go Donwhang لو انت في اي تاون وعايز تروح\n- ( H )  : If you in any town and want to go Hotan لو انت في اي تاون وعايز تروح\n- ( SK ) : If you in any town and want to go Samarkand لو انت في اي تاون وعايز تروح\n- ( C ) : If you in any town and want to go Constantinople لو انت في اي تاون وعايز تروح\n- ( AS ) : If you in any town and want to go Alexandria (South) لو انت في اي تاون وعايز تروح\n- ( AN ) : If you in any town and want to go Alexandria (North) لو انت في اي تاون وعايز تروح\n- ( B ) : If you in any town and want to go Baghdad لو انت في اي تاون وعايز تروح',160,140)
QtBind.createLabel(gui__,'║',150,132)
QtBind.createLabel(gui__,'║',598,132)
QtBind.createLabel(gui__,'║',150,144)
QtBind.createLabel(gui__,'║',598,144)
QtBind.createLabel(gui__,'║',150,156)
QtBind.createLabel(gui__,'║',598,156)
QtBind.createLabel(gui__,'║',150,168)
QtBind.createLabel(gui__,'║',598,168)
QtBind.createLabel(gui__,'║',150,180)
QtBind.createLabel(gui__,'║',598,180)
QtBind.createLabel(gui__,'║',150,192)
QtBind.createLabel(gui__,'║',598,192)
QtBind.createLabel(gui__,'║',150,204)
QtBind.createLabel(gui__,'║',598,204)
QtBind.createLabel(gui__,'║',150,216)
QtBind.createLabel(gui__,'║',598,216)
QtBind.createLabel(gui__,'║',150,228)
QtBind.createLabel(gui__,'║',598,228)
QtBind.createLabel(gui__,'║',150,240)
QtBind.createLabel(gui__,'║',598,240)
QtBind.createLabel(gui__,'╚═══════════════════════════════════════════════════════╝',150,252)

QtBind.createLabel(gui__,'v'+pVersion+'  Made by ❴ Orsa ❵ ✔',580,280)

# Graphic user interface (-)
gui___ = QtBind.init(__name__,"P1 ( Trade )")

QtBind.createLabel(gui___,'╔══════════════════════════════▶ Trade Teleports -',25,10)
QtBind.createLabel(gui___,'{ Translation English } ◀═════════════════════════════╗',368,10)
QtBind.createLabel(gui___,'║',25,20)
QtBind.createLabel(gui___,'║',713,20)
QtBind.createLabel(gui___,'║',25,32)
QtBind.createLabel(gui___,'║',713,32)
QtBind.createLabel(gui___,'║',25,44)
QtBind.createLabel(gui___,'║',713,44)
QtBind.createLabel(gui___,'║',25,56)
QtBind.createLabel(gui___,'║',713,56)
QtBind.createLabel(gui___,'║',25,68)
QtBind.createLabel(gui___,'║',713,68)
QtBind.createLabel(gui___,'║',25,80)
QtBind.createLabel(gui___,'║',713,80)
QtBind.createLabel(gui___,'║',25,91)
QtBind.createLabel(gui___,'║',713,91)
QtBind.createLabel(gui___,'║',25,103)
QtBind.createLabel(gui___,'║',713,103)
QtBind.createLabel(gui___,'╚═════════════════════════════════════════════════════════════════════════════════════╝',25,115)

QtBind.createLabel(gui___,'╔══════════════════════════════▶ Trade Teleports  -',25,130)
QtBind.createLabel(gui___,'{ Translation Arabic } ◀═════════════════════════════╗',371,130)
QtBind.createLabel(gui___,'║',25,140)
QtBind.createLabel(gui___,'║',713,140)
QtBind.createLabel(gui___,'║',25,152)
QtBind.createLabel(gui___,'║',713,152)
QtBind.createLabel(gui___,'║',25,164)
QtBind.createLabel(gui___,'║',713,164)
QtBind.createLabel(gui___,'║',25,176)
QtBind.createLabel(gui___,'║',713,176)
QtBind.createLabel(gui___,'║',25,188)
QtBind.createLabel(gui___,'║',713,188)
QtBind.createLabel(gui___,'║',25,200)
QtBind.createLabel(gui___,'║',713,200)
QtBind.createLabel(gui___,'║',25,212)
QtBind.createLabel(gui___,'║',713,212)
QtBind.createLabel(gui___,'║',25,224)
QtBind.createLabel(gui___,'║',713,224)
QtBind.createLabel(gui___,'║',25,236)
QtBind.createLabel(gui___,'║',713,236)
QtBind.createLabel(gui___,'║',25,248)
QtBind.createLabel(gui___,'║',713,248)
QtBind.createLabel(gui___,'║',25,260)
QtBind.createLabel(gui___,'║',713,260)
QtBind.createLabel(gui___,'║',25,272)
QtBind.createLabel(gui___,'║',713,272)
QtBind.createLabel(gui___,'╚═════════════════════════════════════════════════════════════════════════════════════╝',25,284)

QtBind.createLabel(gui___,'- ( O1 ) If you are in Alex or Cons ▶ Droa then ▶ Samarkand Teleports ▶ Niya Or Karakoram North ▶ Hotan ▶ Donwhang ▶ Jangan',38,26)
QtBind.createLabel(gui___,'- ( O2 ) If you are in Alex or Cons ▶ Sigia then ▶ Roc Mountain North ▶ Karakoram North Or Roc Mountain South ▶ Karakoram South ▶ Hotan \n- ▶ Donwhang ▶ Jangan',38,39)
QtBind.createLabel(gui___,'- ( O3 ) If you are in Constantinople ▶ Alex Or Roc Mountain North ▶ Karakoram South Or Roc Mountain South ▶ Karakoram North',38,65)
QtBind.createLabel(gui___,'- ( O4 ) If you are in Jangan ▶ Donwhang ▶ Hotan ▶ Niya Or Karakoram North ▶ Samarkand ▶ Droa Or Sigia ▶ Constantinople',38,78)
QtBind.createLabel(gui___,'- ( O5 ) If you are in Jangan ▶ Donwhang ▶ Hotan ▶ Karakoram North Or Karakoram South ▶ Roc Mountain North ▶ Sigia ▶ Constantinople',38,91)
QtBind.createLabel(gui___,'- ( O6 ) If you are in Karakoram North Or Karakoram South ▶ Roc Mountain South - Sigia or Droa ▶ Alexandria',38,104)
QtBind.createLabel(gui___,'--لو انت في الكس او كونس و عايز تروح Droa  ومن Droa  ل Samarkand ومن Samarkand ل Niya او Karakoram North ومن Karakoram او Niya ل \nHotan و Donwhang و Jangan هتستخدم ( O1 )',60,143)
QtBind.createLabel(gui___,'-لو انت في الكس او كونس و عايز تروح Sigia ومن Sigia ل Roc Mountain North ومن Roc Mountain North ل Karakoram North أو من Roc Mountain\n South ل Karakoram South ومن Karakoram ل Hotan و Donwhang و Jangan هتستخدم ( O2 )',49,169)
QtBind.createLabel(gui___,'-لو انت في كونس و عايز تروح Alex او لو انت في Samarkand و عايز تروح Roc Mountain North و من Roc Mountain North عايز تروح Karakoram South\n او لو انت في Roc Mountain South و عايز تروح Karakoram North هتستخدم ( O3 )',40,195)
QtBind.createLabel(gui___,'-لو انت في جنجان و عايز تروح ل Donwhang و من Donwhang ل Hotan ومن Hotan ل Niya أو Karakoram North ومن Niya او Karakoram ل Samarkand\n ومن Samarkand ل Droa او Sigia بعد كدة Constantinople هتستخدم ( O4 )',35,220)
QtBind.createLabel(gui___,'-لو انت في جنجان و عايز تروح ل Donwhang و من Donwhang ل Hotan ومن Hotan ل Karakoram North او Karakoram South ل Roc Mountain North\n ومن Roc Mountain North ل Samarkand ومن Roc Mountain او Samarkand ل Sigia ومن Sigia ل Constantinople هتستخدم ( O5 )',42,246)
QtBind.createLabel(gui___,'-لو انت في Karakoram North او Karakoram South وعايز تروح Roc Mountain South او لو انت في Sigia او Droa وعايز تروح اليكس هتستخدم ( O6 )',47,272)


tbxLeaders = QtBind.createLineEdit(gui,"",525,11,110,20)
lstLeaders = QtBind.createList(gui,525,32,110,38)
btnAddLeader = QtBind.createButton(gui,'btnAddLeader_clicked',"    Add   ",635,10)
btnRemLeader = QtBind.createButton(gui,'btnRemLeader_clicked',"     Remove     ",635,32)

# ______________________________ Methods ______________________________ #

# Return ControlAIO 1 folder path
def getPath():
    return get_config_dir()+pName+"\\"

# Return character configs path (JSON)
def getConfig():
    return getPath()+inGame['server'] + "_" + inGame['name'] + ".json"

# Check if character is ingame
def isJoined():
    global inGame
    inGame = get_character_data()
    if not (inGame and "name" in inGame and inGame["name"]):
        inGame = None
    return inGame

# Load default configs
def loadDefaultConfig():
    # Clear data
    QtBind.clear(gui,lstLeaders)

# Loads all config previously saved
def loadConfigs():
    loadDefaultConfig()
    if isJoined():
        # Check config exists to load
        if os.path.exists(getConfig()):
            data = {}
            with open(getConfig(),"r") as f:
                data = json.load(f)
            if "Leaders" in data:
                for nickname in data["Leaders"]:
                    QtBind.append(gui,lstLeaders,nickname)

# Add leader to the list
def btnAddLeader_clicked():
    if inGame:
        player = QtBind.text(gui,tbxLeaders)
        add_leader(player)

def add_leader(player):
    if inGame:
        # Player nickname it's not empty
        if player and not lstLeaders_exist(player):
            # Init dictionary
            data = {}
            # Load config if exist
            if os.path.exists(getConfig()):
                with open(getConfig(), 'r') as f:
                    data = json.load(f)
            # Add new leader
            if not "Leaders" in data:
                data['Leaders'] = []
            data['Leaders'].append(player)
            # Replace configs
            with open(getConfig(),"w") as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))
            QtBind.append(gui,lstLeaders,player)
            QtBind.setText(gui, tbxLeaders, "")
            log('Plugin: Leader added ['+player+']')

# Remove leader selected from list
def btnRemLeader_clicked():
    if inGame:
        selectedItem = QtBind.text(gui,lstLeaders)
        remove_leader(selectedItem)

def remove_leader(player):
    if inGame:
        if player:
            if os.path.exists(getConfig()):
                data = {"Leaders":[]}
                with open(getConfig(), 'r') as f:
                    data = json.load(f)
                try:
                    # remove leader nickname from file if exists
                    data["Leaders"].remove(player)
                    with open(getConfig(),"w") as f:
                        f.write(json.dumps(data, indent=4, sort_keys=True))
                except:
                    pass # just ignore file if doesn't exist
            QtBind.remove(gui,lstLeaders,player)
            log('Plugin: Leader removed ['+player+']')

# Return True if nickname exist at the leader list
def lstLeaders_exist(nickname):
    nickname = nickname.lower()
    players = QtBind.getItems(gui,lstLeaders)
    for i in range(len(players)):
        if players[i].lower() == nickname:
            return True
    return False

# Inject teleport packet, using the source and destination name
def inject_teleport(source,destination):
    t = get_teleport_data(source, destination)
    if t:
        npcs = get_npcs()
        for key, npc in npcs.items():
            if npc['name'] == source or npc['servername'] == source:
                log("Plugin: Selecting teleporter ["+source+"]")
                # Teleport found, select it
                inject_joymax(0x7045, struct.pack('<I', key), False)
                # Start a timer to teleport in 2.0 seconds
                Timer(2.0, inject_joymax, (0x705A,struct.pack('<IBI', key, 2, t[1]),False)).start()
                Timer(2.0, log, ["Plugin: Teleporting to ["+destination+"]"]).start()
                return
    else:
        log('Plugin: Teleport data not found. Wrong teleport name or servername')

# Send message, Ex. "All Hello World!" or "private JellyBitz Hi!"
def handleChatCommand(msg):
    # Try to split message
    args = msg.split(' ',1)
    # Check if the format is correct and is not empty
    if len(args) != 2 or not args[0] or not args[1]:
        return
    # Split correctly the message
    t = args[0].lower()
    if t == 'private' or t == 'note':
        # then check message is not empty
        argsExtra = args[1].split(' ',1)
        if len(argsExtra) != 2 or not argsExtra[0] or not argsExtra[1]:
            return
        args.pop(1)
        args += argsExtra
    # Check message type
    sent = False
    if t == "all":
        sent = phBotChat.All(args[1])
    elif t == "private":
        sent = phBotChat.Private(args[1],args[2])
    elif t == "party":
        sent = phBotChat.Party(args[1])
    elif t == "guild":
        sent = phBotChat.Guild(args[1])
    elif t == "union":
        sent = phBotChat.Union(args[1])
    elif t == "note":
        sent = phBotChat.Note(args[1],args[2])
    elif t == "stall":
        sent = phBotChat.Stall(args[1])
    elif t == "global":
        sent = phBotChat.Global(args[1])
    if sent:
        log('Plugin: Message "'+t+'" sent successfully!')

# Move to a random position from the actual position using a maximum radius
def randomMovement(radiusMax=10):
    # Generating a random new point
    pX = random.uniform(-radiusMax,radiusMax)
    pY = random.uniform(-radiusMax,radiusMax)
    # Mixing with the actual position
    p = get_position()
    pX = pX + p["x"]
    pY = pY + p["y"]
    # Moving to new position
    move_to(pX,pY,p["z"])
    log("Plugin: Random movement to (X:%.1f,Y:%.1f)"%(pX,pY))

# Follow a player using distance. Return success
def start_follow(player,distance):
    if party_player(player):
        global followActivated,followPlayer,followDistance
        followPlayer = player
        followDistance = distance
        followActivated = True
        return True
    return False

# Return True if the player is in the party
def party_player(player):
    players = get_party()
    if players:
        for p in players:
            if players[p]['name'] == player:
                return True
    return False

# Return point [X,Y] if player is in the party and near, otherwise return None
def near_party_player(player):
    players = get_party()
    if players:
        for p in players:
            if players[p]['name'] == player and players[p]['player_id'] > 0:
                return players[p]
    return None

# Calc the distance from point A to B
def GetDistance(ax,ay,bx,by):
    return ((bx-ax)**2 + (by-ay)**2)**0.5

# Stop follow player
def stop_follow():
    global followActivated,followPlayer,followDistance
    result = followActivated
    # stop
    followActivated = False
    followPlayer = ""
    followDistance = 0
    return result

# Try to summon a vehicle
def MountHorse():
    # search item with similar name or exact server name
    item = GetItemByExpression(lambda n,s: s.startswith('ITEM_COS_C_'),13)
    if item:
        UseItem(item)
        return True
    log('Plugin: Horse not found at your inventory')
    return False

# Try to mount pet by type, return success
def MountPet(petType):
    # just in case
    if petType == 'pick':
        return False
    elif petType == 'horse':
        return MountHorse()
    # get all summoned pets
    pets = get_pets()
    if pets:
        for uid,pet in pets.items():
            if pet['type'] == petType:
                p = b'\x01' # mount flag
                p += struct.pack('I',uid)
                inject_joymax(0x70CB,p, False)
                return True
    return False

# Try to dismount pet by type, return success
def DismountPet(petType):
    petType = petType.lower()
    # just in case
    if petType == 'pick':
        return False
    # get all summoned pets
    pets = get_pets()
    if pets:
        for uid,pet in pets.items():
            if pet['type'] == petType:
                p = b'\x00'
                p += struct.pack('I',uid)
                inject_joymax(0x70CB,p, False)
                return True
    return False

# Gets the NPC unique ID if the specified name is found near
def GetNPCUniqueID(name):
    NPCs = get_npcs()
    if NPCs:
        name = name.lower()
        for UniqueID, NPC in NPCs.items():
            NPCName = NPC['name'].lower()
            if name == NPCName:
                return UniqueID
    return 0

# Search an item by name or servername through lambda expression and return his information
def GetItemByExpression(_lambda,start=0,end=0):
    inventory = get_inventory()
    items = inventory['items']
    if end == 0:
        end = inventory['size']
    # check items between intervals
    for slot, item in enumerate(items):
        if start <= slot and slot <= end:
            if item:
                # Search by lambda
                if _lambda(item['name'],item['servername']):
                    # Save slot location
                    item['slot'] = slot
                    return item
    return None

# Finds an empty slot, returns -1 if inventory is full
def GetEmptySlot():
    items = get_inventory()['items']
    # check the first empty
    for slot, item in enumerate(items):
        if slot >= 13:
            if not item:
                return slot
    return -1

# Injects item movement on inventory
def Inject_InventoryMovement(movementType,slotInitial,slotFinal,logItemName,quantity=0):
    p = struct.pack('<B',movementType)
    p += struct.pack('<B',slotInitial)
    p += struct.pack('<B',slotFinal)
    p += struct.pack('<H',quantity)
    log('Plugin: Moving item "'+logItemName+'"...')
    # CLIENT_INVENTORY_ITEM_MOVEMENT
    inject_joymax(0x7034,p,False)

# Try to equip item
def EquipItem(item):
    itemData = get_item(item['model'])
    # Check equipables only
    if itemData['tid1'] != 1:
        log('Plugin: '+item['name']+' cannot be equiped!')
        return
    # Check equipable type
    t = itemData['tid2']
    # garment, protector, armor, robe, light, heavy
    if t == 1 or t == 2 or t == 3 or t == 9 or t == 10 or t == 11:
        t = itemData['tid3']
        # head
        if t == 1:
            Inject_InventoryMovement(0,item['slot'],0,item['name'])
        # shoulders
        elif t == 2:
            Inject_InventoryMovement(0,item['slot'],2,item['name'])
        # chest
        elif t == 3:
            Inject_InventoryMovement(0,item['slot'],1,item['name'])
        # pants
        elif t == 4:
            Inject_InventoryMovement(0,item['slot'],4,item['name'])
        # gloves
        elif t == 5:
            Inject_InventoryMovement(0,item['slot'],3,item['name'])
        # boots
        elif t == 6:
            Inject_InventoryMovement(0,item['slot'],5,item['name'])
    # shields
    elif t == 4:
        Inject_InventoryMovement(0,item['slot'],7,item['name'])
    # accesories ch/eu
    elif t == 5 or t == 12:
        t = itemData['tid3']
        # earring
        if t == 1:
            Inject_InventoryMovement(0,item['slot'],9,item['name'])
        # necklace
        elif t == 2:
            Inject_InventoryMovement(0,item['slot'],10,item['name'])
        # ring
        elif t == 3:
            # Check if second ring slot is empty
            if not GetItemByExpression(lambda s,n: True,11):
                Inject_InventoryMovement(0,item['slot'],12,item['name'])
            else:
                Inject_InventoryMovement(0,item['slot'],11,item['name'])
    # weapon ch/eu
    elif t == 6:
        Inject_InventoryMovement(0,item['slot'],6,item['name'])
    # job
    elif t == 7:
        Inject_InventoryMovement(0,item['slot'],8,item['name'])
    # avatar
    elif t == 13:
        t = itemData['tid3']
        # hat
        if t == 1:
            Inject_InventoryMovement(36,item['slot'],0,item['name'])
        # dress
        elif t == 2:
            Inject_InventoryMovement(36,item['slot'],1,item['name'])
        # accesory
        elif t == 3:
            Inject_InventoryMovement(36,item['slot'],2,item['name'])
        # flag
        elif t == 4:
            Inject_InventoryMovement(36,item['slot'],3,item['name'])
    # devil spirit
    elif t == 14:
        Inject_InventoryMovement(36,item['slot'],4,item['name'])

# Try to unequip item
def UnequipItem(item):
    # find an empty slot
    slot = GetEmptySlot()
    if slot != -1:
        Inject_InventoryMovement(0,item['slot'],slot,item['name'])

# Try to use the item specified
def UseItem(item):
    # Create packet and inject it
    p = struct.pack('<B',item['slot'])
    loc = get_locale()

    tid = GetTIDFromItem(item['model'])
    if loc == 22: # vsro
        p += struct.pack('<H',tid)
    else:
        p += struct.pack('<I',tid)

    log('Plugin: Using item "'+item['name']+'"...')
    # CLIENT_INVENTORY_ITEM_USE
    inject_joymax(0x704C,p,True)

# Get Type ID from item
def GetTIDFromItem(itemId):
    conn = GetDatabaseConnection()
    c = conn.cursor()
    c.execute('SELECT cash_item, tid1, tid2, tid3 FROM items WHERE id=?',(itemId,))
    result = c.fetchone()
    # calculate TID
    result = result[0] + (3 * 4) + (result[1] * 32) + (result[2] * 128) + (result[3] * 2048)
    conn.close()
    return result

# Create a connection to database
def GetDatabaseConnection():
    bot_path = os.getcwd()
    # Load the server info
    data = {}
    locale = get_locale()
    # vSRO
    if locale == 22:
        with open(bot_path+"/vSRO.json","r") as f:
            data = json.load(f)
        # Match data with the current server name
        server = inGame['server']
        for k in data:
            servers = data[k]['servers']
            # Check if servers is in list
            if server in servers:
                # Scan data folder
                for path in os.scandir(bot_path+"/Data"):
                    # Check databases only
                    if path.is_file() and path.name.endswith(".db3"):
                        # Connect to check if the data matches
                        conn = sqlite3.connect(bot_path+"/Data/"+path.name)
                        c = conn.cursor()
                        c.execute('SELECT * FROM data WHERE k="path" AND v=?',(data[k]['path'],))
                        if c.fetchone():
                            # match found
                            return conn
                        else:
                            conn.close()
    # iSRO
    elif locale == 18:
        return sqlite3.connect(bot_path+"/Data/iSRO.db3")
    # TrSRO
    elif locale == 56:
        return sqlite3.connect(bot_path+"/Data/TRSRO.db3")
    return None

def getDrops():
    global drops
    drops = get_drops()

# Pick loop
def pick_loop():
    global stopPicking
    if stopPicking:
        log('stopped')
    if not stopPicking:
        if not 0 == len(drops):
            timer = Timer(0.5, pick_loop)
            timer.start()
            droppedItem = drops.popitem()
            id = droppedItem[0]
            tradeGood = droppedItem[1]
            xCoor = tradeGood['x']
            yCoor = tradeGood['y']
            #move to item coordinate
            move_to(xCoor, yCoor, 0.0)
            inject_pick(id, tradeGood)
        else:
            getDrops()
            if not 0 == len(drops):
                log('Not all items picked, Picking again')
                pick_loop()
            else:
                log('No drops')

# Pick Drop Goods
def inject_pick(id, tradeGood):
    packet = b'\x01\x02\x01' + struct.pack('I', id)
    inject_joymax(0x7074, packet, False)
    log('Plugin '+pName+': Picked up "'+tradeGood['name']+'" ')

Name_1 = [236]
Name_2 = [237]

def ReturnScroll(name):
    items = get_inventory()['items']
    for slot, item in enumerate(items):
        if item:
            sn = item['name']
            if sn.startswith('Instant Return Scroll') or sn == 'Special Return Scroll' or sn == 'Beginner Return Scroll':
                packet = struct.pack('B', slot)
                packet += struct.pack('B', name[0])
                packet += struct.pack('B', 9)
                inject_joymax(0x704C,packet,True)
                return
    log('Plugin: "Return Scroll" not found at your inventory')

# ______________________________ Events ______________________________ #

# Called when the bot successfully connects to the game server
def connected():
    global inGame
    inGame = None

# Called when the character enters the game world
def joined_game():
    loadConfigs()

# All chat messages received are sent to this function
def handle_chat(t,player,msg):
    global stopPicking
    # Remove guild name from union chat messages
    if t == 11:
        msg = msg.split(': ',1)[1]
    # Check player at leader list or a Discord message
    if player and lstLeaders_exist(player) or t == 100:
        # Parsing message command
        if msg == "PET1":
            handle_chat(t, player, "USE White Elephant")
        elif msg == "CT":
            inject_joymax(0x704B, struct.pack('4B', 0x5C, 0x02, 0x00, 0x00), True)
        elif msg == "PET2":
            handle_chat(t, player, "USE Dark horse trade pet")
        elif msg == "PET3":
            handle_chat(t, player, "USE Dino")
        elif msg == "PET4":
            handle_chat(t, player, "USE Indian ox")
        elif msg == "PET5":
            handle_chat(t, player, "USE Goldclad trade Horse")
        elif msg == "PET6":
            handle_chat(t, player, "USE Behemoth")
        elif msg == "PG":
            global stopPicking
            stopPicking = False
            global drops
            drops = get_drops()
            pick_loop()
        elif msg == 'SPG':
            stopPicking = True
        elif msg.startswith("ADDL "):
            player = msg[5:]
            add_leader(player)
        elif msg.startswith("REML "):
            player = msg[5:]
            remove_leader(player)
        elif msg == "S":
            start_bot()
            log("Plugin: Bot started")
        elif msg == "SP":
            stop_bot()
            log("Plugin: Bot stopped")
        elif msg == "T" or msg == "J":
            # deletes empty spaces on right
            msg = msg.rstrip()
            if msg == "T" or msg == "J":
                if start_trace(player):
                    log("Plugin: Starting trace to ["+player+"]")
            else:
                msg = msg[1:].split()[0]
                if start_trace(msg):
                    log("Plugin: Starting trace to ["+msg+"]")
        elif msg.startswith("TT"):
            # deletes empty spaces on right
            msg = msg.rstrip()
            if msg == "TT":
                if start_trace(player):
                    log("Plugin: Starting trace to ["+player+"]")
            else:
                msg = msg[2:].split()[0]
                if start_trace(msg):
                    log("Plugin: Starting trace to ["+msg+"]")
        elif msg == "N":
            stop_trace()
            log("Plugin: Trace stopped")
        elif msg == "SET":
            # deletes empty spaces on right
            msg = msg.rstrip()
            if msg == "SET":
                p = get_position()
                set_training_position(p['region'], p['x'], p['y'],p['z'])
                log("Plugin: Training area set to current position (X:%.1f,Y:%.1f)"%(p['x'],p['y']))
            else:
                try:
                    # check arguments
                    p = msg[6:].split()
                    x = float(p[0])
                    y = float(p[1])
                    # auto calculated if is not specified
                    region = int(p[2]) if len(p) >= 3 else 0
                    z = float(p[3]) if len(p) >= 4 else 0
                    set_training_position(region,x,y,z)
                    log("Plugin: Training area set to (X:%.1f,Y:%.1f)"%(x,y))
                except:
                    log("Plugin: Wrong training area coordinates!")
        elif msg == 'GETPOS':
            # Check current position
            pos = get_position()
            phBotChat.Private(player,'My position is (X:%.1f,Y:%.1f,Z:%1f,Region:%d)'%(pos['x'],pos['y'],pos['z'],pos['region']))
        elif msg.startswith("SETR"):
            # deletes empty spaces on right
            msg = msg.rstrip()
            if msg == "SETR":
                # set default radius
                radius = 35
                set_training_radius(radius)
                log("Plugin: Training radius reseted to "+str(radius)+" m.")
            else:
                try:
                    # split and parse movement radius
                    radius = int(float(msg[4:].split()[0]))
                    # to absolute
                    radius = (radius if radius > 0 else radius*-1)
                    set_training_radius(radius)
                    log("Plugin: Training radius set to "+str(radius)+" m.")
                except:
                    log("Plugin: Wrong training radius value!")
        elif msg.startswith("SETS"):
            # deletes empty spaces on right
            msg = msg.rstrip()
            if msg == "SETS":
                # reset script
                set_training_script('')
                log('Plugin: Training script path has been reseted')
            else:
                # change script to the path specified
                set_training_script(msg[4:])
                log('Plugin: Training script path has been changed')
        elif msg.startswith('SETA '):
            # deletes empty spaces on right
            msg = msg[5:]
            if msg:
                # try to change to specified area name
                if set_training_area(msg):
                    log('Plugin: Training area has been changed to ['+msg+']')
                else:
                    log('Plugin: Training area ['+msg+'] not found in the list')
        elif msg == "SIT":
            log("Plugin: Sit/Stand")
            inject_joymax(0x704F,b'\x04',False)
        elif msg == "JUMP":
            # Just a funny emote lol
            log("Plugin: Jumping!")
            inject_joymax(0x3091,b'\x0c',False)
        elif msg.startswith("CAPE"):
            # deletes empty spaces on right
            msg = msg.rstrip()
            if msg == "CAPE":
                log("Plugin: Using PVP Cape by default (Yellow)")
                inject_joymax(0x7516,b'\x05',False)
            else:
                # get cape type normalized
                cape = msg[4:].split()[0].lower()
                if cape == "off":
                    log("Plugin: Removing PVP Cape")
                    inject_joymax(0x7516,b'\x00',False)
                elif cape == "red":
                    log("Plugin: Using PVP Cape (Red)")
                    inject_joymax(0x7516,b'\x01',False)
                elif cape == "gray":
                    log("Plugin: Using PVP Cape (Gray)")
                    inject_joymax(0x7516,b'\x02',False)
                elif cape == "blue":
                    log("Plugin: Using PVP Cape (Blue)")
                    inject_joymax(0x7516,b'\x03',False)
                elif cape == "white":
                    log("Plugin: Using PVP Cape (White)")
                    inject_joymax(0x7516,b'\x04',False)
                elif cape == "yellow":
                    log("Plugin: Using PVP Cape (Yellow)")
                    inject_joymax(0x7516,b'\x05',False)
                else:
                    log("Plugin: Wrong PVP Cape color!")
        elif msg == "ZERK":
            log("Plugin: Using Berserker mode")
            inject_joymax(0x70A7,b'\x01',False)
        elif msg == "RR":
            # Quickly check if is dead
            character = get_character_data()
            if character['hp'] == 0:
                # RIP
                log('Plugin: Resurrecting at town...')
                inject_joymax(0x3053,b'\x01',False)
            else:
                log('Plugin: Trying to use return scroll...')
                # Avoid high CPU usage with too many chars at the same time
                ReturnScroll(Name_1)
                ReturnScroll(Name_2)
        elif msg.startswith("TP"):
            # deletes command header and whatever used as separator
            msg = msg[3:]
            if not msg:
                return
            # select split char
            split = '.' if '.' in msg else ','
            # extract arguments
            source_dest = msg.split(split)
            # needs to be at least two name points to try teleporting
            if len(source_dest) >= 2:
                inject_teleport(source_dest[0].strip(),source_dest[1].strip())
        elif msg.startswith("INJECT "):
            msgPacket = msg[7:].split()
            msgPacketLen = len(msgPacket)
            if msgPacketLen == 0:
                log("Plugin: Incorrect structure to inject packet")
                return
            # Check packet structure
            opcode = int(msgPacket[0],16)
            data = bytearray()
            encrypted = False
            dataIndex = 1
            if msgPacketLen >= 2:
                enc = msgPacket[1].lower()
                if enc == 'true' or enc == 'false':
                    encrypted = enc == "true"
                    dataIndex +=1
            # Create packet data and inject it
            for i in range(dataIndex, msgPacketLen):
                data.append(int(msgPacket[i],16))
            inject_joymax(opcode,data,encrypted)
            # Log the info
            log("Plugin: Injecting packet...\nOpcode: 0x"+'{:02X}'.format(opcode)+" - Encrypted: "+("Yes" if encrypted else "No")+"\nData: "+(' '.join('{:02X}'.format(int(msgPacket[x],16)) for x in range(dataIndex, msgPacketLen)) if len(data) else 'None'))
        elif msg.startswith("CHAT "):
            handleChatCommand(msg[5:])
        elif msg.startswith("MOVEON"):
            if msg == "MOVEON":
                randomMovement()
            else:
                try:
                    # split and parse movement radius
                    radius = int(float(msg[6:].split()[0]))
                    # to positive
                    radius = (radius if radius > 0 else radius*-1)
                    randomMovement(radius)
                except:
                    log("Plugin: Movement maximum radius incorrect")
        elif msg.startswith("F"):
            # default values
            charName = player
            distance = 0
            if msg != "F":
                # Check params
                msg = msg[1:].split()
                try:
                    if len(msg) >= 1:
                        charName = msg[0]
                    if len(msg) >= 2:
                        distance = float(msg[1])
                except:
                    log("Plugin: Follow distance incorrect")
                    return
            # Start following
            if start_follow(charName,distance):
                log("Plugin: Starting to follow to ["+charName+"] using ["+str(distance)+"] as distance")
        elif msg == "NF":
            if stop_follow():
                log("Plugin: Following stopped")
        elif msg.startswith("PROFILE"):
            if msg == "PROFILE":
                if set_profile('Default'):
                    log("Plugin: Setting Default profile")
            else:
                msg = msg[7:]
                if set_profile(msg):
                    log("Plugin: Setting "+msg+" profile")
        elif msg == "DCC":
            log("Plugin: Disconnecting...")
            disconnect()
        elif msg == "M" or msg == "MT":
            # default value
            pet = "transport"
            if msg != "M" or msg != "MT":
                msg = msg[2:].split()
                if msg:
                    pet = msg[0]
            # Try mount pet
            if MountPet(pet):
                log("Plugin: Mounting pet ["+pet+"]")
        elif msg == "D" or msg == "DS":
            # default value
            pet = "transport"
            if msg != "D" or msg != "DS":
                msg = msg[2:].split()
                if msg:
                    pet = msg[0]
            # Try dismount pet
            if DismountPet(pet):
                log("Plugin: Dismounting pet ["+pet+"]")
        elif msg == "TERMINATEE":
            pets = get_pets()
            if pets:
                for k, v in pets.items():
                    if v['type'] == 'transport':
                        log(f'Plugin: Terminating pet [{v["name"]}]')
                        inject_joymax(0x70C6, struct.pack('I', k), False)
        elif msg == "USE Transport":
            items = get_inventory()['items']
            for slot, item in enumerate(items):
                if item:
                    name = item['servername']
                    if name.startswith('ITEM_COS_T_'):
                        p = struct.pack('B', slot)  # Inventory Slot
                        p += b'\xED\x11'
                        log(f'Plugin: Using transport "{item["name"]}"...')
                        inject_joymax(0x704C, p, True)
                        return
            log(r'Plugin: You dont have any transport pet')
        elif msg == "G":
            # Check if has party
            if get_party():
                # Left it
                log("Plugin: Leaving the party..")
                inject_joymax(0x7061,b'',False)
        elif msg.startswith("RECALL "):
            msg = msg[7:]
            if msg:
                npcUID = GetNPCUniqueID(msg)
                if npcUID > 0:
                    log("Plugin: Designating recall to \""+msg.title()+"\"...")
                    inject_joymax(0x7059, struct.pack('I',npcUID), False)
        elif msg.startswith("EQUIP "):
            msg = msg[6:]
            if msg:
                # search item with similar name or exact server name
                item = GetItemByExpression(lambda n,s: msg in n or msg == s,13)
                if item:
                    EquipItem(item)
        elif msg.startswith("UNEQUIP "):
            msg = msg[8:]
            if msg:
                # search item with similar name or exact server name
                item = GetItemByExpression(lambda n,s: msg in n or msg == s,0,12)
                if item:
                    UnequipItem(item)
        elif msg.startswith("REVERSE "):
            # remove command
            msg = msg[8:]
            if msg:
                # check params
                msg = msg.split(' ',1)
                # param type
                if msg[0] == 'return':
                    # try to use it
                    if reverse_return(0,''):
                        log('Plugin: Using reverse to the last return scroll location')
                elif msg[0] == 'death':
                    # try to use it
                    if reverse_return(1,''):
                        log('Plugin: Using reverse to the last death location')
                elif msg[0] == 'player':
                    # Check existing name
                    if len(msg) >= 2:
                        # try to use it
                        if reverse_return(2,msg[1]):
                            log('Plugin: Using reverse to player "'+msg[1]+'" location')
                elif msg[0] == 'zone':
                    # Check existing zone
                    if len(msg) >= 2:
                        # try to use it
                        if reverse_return(3,msg[1]):
                            log('Plugin: Using reverse to zone "'+msg[1]+'" location')
        elif msg.startswith("USE "):
            # remove command
            msg = msg[4:]
            if msg:
                # search item with similar name or exact server name
                item = GetItemByExpression(lambda n,s: msg in n or msg == s,13)
                if item:
                    UseItem(item)

# _____________________________ Towns TP _____________________________ #

        elif msg == ("JG"):
            inject_teleport("Constantinople","Samarkand") or inject_teleport("Samarkand","Hotan") or inject_teleport("Baghdad","Hotan") or inject_teleport("Hotan","Donwhang") or inject_teleport("Donwhang","Jangan") or inject_teleport("Alexandria (North)","Jangan") or inject_teleport("Alexandria (South)","Jangan")
        elif msg == ("DW"):
            inject_teleport("Constantinople","Samarkand") or inject_teleport("Samarkand","Hotan") or inject_teleport("Baghdad","Hotan") or inject_teleport("Hotan","Donwhang") or inject_teleport("Jangan","Donwhang") or inject_teleport("Alexandria (North)","Hotan") or inject_teleport("Alexandria (South)","Hotan")
        elif msg == ("H"):
            inject_teleport("Constantinople","Samarkand") or inject_teleport("Samarkand","Hotan") or inject_teleport("Donwhang","Hotan") or inject_teleport("Jangan","Donwhang") or inject_teleport("Alexandria (North)","Hotan") or inject_teleport("Alexandria (South)","Hotan") or inject_teleport("Baghdad","Hotan")
        elif msg == ("SK"):
            inject_teleport("Baghdad","Hotan") or inject_teleport("Alexandria (North)","Hotan") or inject_teleport("Alexandria (South)","Hotan") or inject_teleport("Donwhang","Hotan") or inject_teleport("Jangan","Donwhang") or inject_teleport("Hotan","Samarkand") or inject_teleport("Constantinople","Samarkand")
        elif msg == ("C"):
            inject_teleport("Alexandria (North)","Hotan") or inject_teleport("Alexandria (South)","Hotan") or inject_teleport("Hotan","Samarkand") or inject_teleport("Donwhang","Hotan") or inject_teleport("Jangan","Donwhang") or inject_teleport("Samarkand","Constantinople")
        elif msg == ("AS"):
            inject_teleport("Constantinople","Samarkand") or inject_teleport("Samarkand","Hotan") or inject_teleport("Donwhang","Hotan") or inject_teleport("Jangan","Alexandria (South)") or inject_teleport("Hotan","Alexandria (South)") or inject_teleport("Alexandria (North)","Alexandria (South)") or inject_teleport("Baghdad","Alexandria (South)")
        elif msg == ("AN"):
            inject_teleport("Constantinople","Samarkand") or inject_teleport("Samarkand","Hotan") or inject_teleport("Donwhang","Hotan") or inject_teleport("Jangan","Alexandria (North)") or inject_teleport("Hotan","Alexandria (North)") or inject_teleport("Alexandria (South)","Alexandria (North)") or inject_teleport("Baghdad","Alexandria (North)")
        elif msg == ("B"):
            inject_teleport("Constantinople","Samarkand") or inject_teleport("Samarkand","Hotan") or inject_teleport("Donwhang","Hotan") or inject_teleport("Jangan","Donwhang") or inject_teleport("Hotan","Baghdad")

# _____________________________ Trade TP _____________________________ #

        elif msg == ("O1"):
            inject_teleport("Harbor Manager Gale","Pirate Morgun") or inject_teleport("Harbor Manager Marwa","Pirate Morgun") or inject_teleport("Aircraft Ticket Seller Saena","Airship Ticket Seller Dawari") or inject_teleport("Tunnel Manager Salhap","Tunnel Manager Maryokuk") or inject_teleport("Tunnel Manager Topni","Tunnel Manager Asui") or inject_teleport("Boat Ticket Seller Rahan","Boat Ticket Seller Salmai") or inject_teleport("Boat Ticket Seller Asimo","Boat Ticket Seller Asa") or inject_teleport("Ferry Ticket Seller Hageuk","Ferry Ticket Seller Chau") or inject_teleport("Ferry Ticket Seller Tayun","Ferry Ticket Seller Doji")
        elif msg == ("O2"):
            inject_teleport("Harbor Manager Marwa","Priate Blackbeard") or inject_teleport("Harbor Manager Gale","Priate Blackbeard") or inject_teleport("Aircraft Ticket Seller Shard","Aircraft Ticket Seller Sangnia") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Dawari") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Poy") or inject_teleport("Boat Ticket Seller Rahan","Boat Ticket Seller Salmai") or inject_teleport("Boat Ticket Seller Asimo","Boat Ticket Seller Asa") or inject_teleport("Ferry Ticket Seller Hageuk","Ferry Ticket Seller Chau") or inject_teleport("Ferry Ticket Seller Tayun","Ferry Ticket Seller Doji")
        elif msg == ("O3"):
            inject_teleport("Harbor Manager Gale","Harbor Manager Marwa") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Poy") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Dawari") or inject_teleport("Aircraft Ticket Seller Saena","Aircraft Ticket Seller Ajati")
        elif msg == ("O4"):
            inject_teleport("Ferry Ticket Seller Chau","Ferry Ticket Seller Hageuk") or inject_teleport("Ferry Ticket Seller Doji","Ferry Ticket Seller Tayun") or inject_teleport("Boat Ticket Seller Salmai","Boat Ticket Seller Rahan") or inject_teleport("Boat Ticket Seller Asa","Boat Ticket Seller Asimo") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Saena") or inject_teleport("Tunnel Manager Maryokuk","Tunnel Manager Salhap") or inject_teleport("Tunnel Manager Asui","Tunnel Manager Topni") or inject_teleport("Pirate Morgun","Harbor Manager Gale") or inject_teleport("Priate Blackbeard","Harbor Manager Gale") or inject_teleport("Underwater Route #2","Underwater Route #3") or inject_teleport("Underwater Route #3","Hotan")
        elif msg == ("O5"):
            inject_teleport("Ferry Ticket Seller Chau","Ferry Ticket Seller Hageuk") or inject_teleport("Ferry Ticket Seller Doji","Ferry Ticket Seller Tayun") or inject_teleport("Boat Ticket Seller Salmai","Boat Ticket Seller Rahan") or inject_teleport("Boat Ticket Seller Asa","Boat Ticket Seller Asimo") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Ajati") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Ajati") or inject_teleport("Aircraft Ticket Seller Sangnia","Aircraft Ticket Seller Shard") or inject_teleport("Pirate Morgun","Harbor Manager Gale") or inject_teleport("Priate Blackbeard","Harbor Manager Gale") or inject_teleport("Aircraft Ticket Seller Ajati","Aircraft Ticket Seller Saena") or inject_teleport("Underwater Route #2","Underwater Route #3") or inject_teleport("Underwater Route #3","Hotan")
        elif msg == ("O6"):
            inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Sayun") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Sayun") or inject_teleport("Pirate Morgun","Harbor Manager Marwa") or inject_teleport("Priate Blackbeard","Harbor Manager Marwa")
        elif msg == ("Q1"):
            inject_teleport("Harbor Manager Marwa","Pirate Morgun") or inject_teleport("Pirate Morgun","Harbor Manager Gale") or inject_teleport("Harbor Manager Gale","Pirate Morgun") or inject_teleport("Priate Blackbeard","Harbor Manager Gale") or inject_teleport("Aircraft Ticket Seller Shard","Aircraft Ticket Seller Sangnia") or inject_teleport("Aircraft Ticket Seller Sangnia","Aircraft Ticket Seller Shard") or inject_teleport("Tunnel Manager Salhap","Tunnel Manager Maryokuk") or inject_teleport("Tunnel Manager Maryokuk","Tunnel Manager Salhap") or inject_teleport("Tunnel Manager Topni","Tunnel Manager Asui") or inject_teleport("Tunnel Manager Asui","Tunnel Manager Topni") or inject_teleport("Aircraft Ticket Seller Saena","Aircraft Ticket Seller Ajati") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Ajati") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Ajati") or inject_teleport("Boat Ticket Seller Rahan","Boat Ticket Seller Salmai") or inject_teleport("Boat Ticket Seller Salmai","Boat Ticket Seller Rahan") or inject_teleport("Boat Ticket Seller Asimo","Boat Ticket Seller Asa") or inject_teleport("Boat Ticket Seller Asa","Boat Ticket Seller Asimo") or inject_teleport("Ferry Ticket Seller Tayun","Ferry Ticket Seller Doji") or inject_teleport("Ferry Ticket Seller Doji","Ferry Ticket Seller Tayun") or inject_teleport("Ferry Ticket Seller Hageuk","Ferry Ticket Seller Chau") or inject_teleport("Ferry Ticket Seller Chau","Ferry Ticket Seller Hageuk") or inject_teleport("forbidden plain","Kings Valley") or inject_teleport("Kings Valley","forbidden plain") or inject_teleport("abundance ground","Storm and cloud Desert") or inject_teleport("Storm and cloud Desert","abundance ground") or inject_teleport("Underwater Route #2","Underwater Route #3") or inject_teleport("Underwater Route #3","Hotan")
        elif msg == ("Q2"):
            inject_teleport("Harbor Manager Marwa","Priate Blackbeard") or inject_teleport("Harbor Manager Gale","Priate Blackbeard") or inject_teleport("Pirate Morgun","Harbor Manager Marwa") or inject_teleport("Priate Blackbeard","Harbor Manager Marwa") or inject_teleport("Aircraft Ticket Seller Saena","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Sayun") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Poy") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Sayun") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Poy")
        elif msg == ("Q3"):
            inject_teleport("Harbor Manager Marwa","Harbor Manager Gale") or inject_teleport("Harbor Manager Gale","Harbor Manager Marwa") or inject_teleport("Aircraft Ticket Seller Ajati","Aircraft Ticket Seller Saena") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Saena")
        elif msg == ("ST"):
            # 0x705A True 02 00 00 00 02 19 00 00 00
            inject_joymax(0x705A, b'\x02\x00\x00\x00\x02\x19\x00\x00\x00', True)


# ______________________________ HWT TP ______________________________ #

        elif msg == ("KP1"):
            inject_teleport("Kings Valley","Pharaoh tomb (beginner)")
        elif msg == ("KP2"):
            inject_teleport("Kings Valley","Pharaoh tomb (intermediate)")
        elif msg == ("KP3"):
            inject_teleport("Kings Valley","Pharaoh tomb (advance)")

# ____________________________ Juipter TP ___________________________ #

        elif msg == ("J5"):
            inject_teleport("Temple of Jupiter Entrance","Zealots Hideout (Intermediate)")
        elif msg == ("J6"):
            inject_teleport("Temple of Jupiter Entrance","Zealots Hideout (Advanced)")
# ____________________________ Script Arguments ___________________________ #

# Send message, even through script. Ex. "chat,All,Hello World!" or "chat,private,JellyBitz,Hi!"
def chat(args):
    args = FixEscapeComma(args)
    # Avoid wrong structure and empty stuffs
    if len(args) < 3 or not args[1] or not args[2]:
        return
    # Check message type
    sent = False
    t = args[1].lower()
    if t == "all":
        sent = phBotChat.All(args[2])
    elif t == "private":
        sent = phBotChat.Private(args[2],args[3])
    elif t == "party":
        sent = phBotChat.Party(args[2])
    elif t == "guild":
        sent = phBotChat.Guild(args[2])
    elif t == "union":
        sent = phBotChat.Union(args[2])
    elif t == "note":
        sent = phBotChat.Note(args[2],args[3])
    elif t == "stall":
        sent = phBotChat.Stall(args[2])
    elif t == "global":
        sent = phBotChat.Global(args[2])
    if sent:
        log('Plugin: Message "'+t+'" sent successfully!')


# Fix array comma handled by bot
def FixEscapeComma(_array):
    _len = len(_array)
    i = 0
    while i < _len:
        # Check if any argument ends with '\'
        if _array[i].endswith('\\') and i < (_len-1):
            _array[i] = _array[i][:-1]+','+_array[i+1]
            del _array[i+1]
            _len-=1
        else:
            i+=1
    return _array

def ResetSkip1():
    global SkipCommand2
    SkipCommand2 = False

def ResetSkip2():
    global SkipCommand3
    SkipCommand3 = False


def LeaveParty(args):
    if get_party():
        inject_joymax(0x7061,b'',False)
        log('Plugin: Leaving Party')
    return 0

def Notification(args):
    if len(args) == 3:
        title = args[1]
        message = args[2]
        show_notification(title, message)
        return 0
    log('Plugin: Incorrect Notification command')
    return 0

def NotifyList(args):
    if len(args) == 2:
        message = args[1]
        create_notification(message)
        return 0
    log('Plugin: Incorrect NotifyList command')
    return 0

def PlaySound(args):
    FileName = args[1]
    if os.path.exists(path + FileName):
        play_wav(path + FileName)
        log('Plugin: Playing [%s]' %FileName)
        return 0
    log('Plugin: Sound file [%s] doesnt exist' %FileName)
    return 0

def SetScript(args):
    name = args[1]
    if os.path.exists(path + name):
        set_training_script(path + name)
        log('Plugin: Changing Script to [%s]' %name)
        return 0
    log('Plugin: Script [%s] doesnt exist' %name)
    return 0

def CloseBot(args):
    global CloseBotAt, CheckCloseTime
    CheckCloseTime = True
    if len(args) == 1:
        Terminate()
        return 0
    type = args[1]
    time = args[2]
    if type == 'in':
        CloseBotAt = str(datetime.datetime.now() + timedelta(minutes=int(time)))[11:16]
        log('Plugin: Closing Bot At [%s]' %CloseBotAt)
    elif type == 'at':
        CloseBotAt = time
        log('Plugin: Closing Bot At [%s]' %CloseBotAt)
    return 0

def Terminate():
    log("Plugin: Closing bot...")
    os.kill(os.getpid(),9)

def GoClientless(args):
    pid = get_client()['pid']
    if pid:
        os.kill(pid, signal.SIGTERM)
        return 0
    log('Plugin: Client is not open!')
    return 0

def StartBot(args):
    global StartBotAt, CheckStartTime, SkipCommand1
    #avoid bot doing command again after restarting
    if SkipCommand1:
        SkipCommand1 = False
        return 0
    stop_bot()
    type = args[1]
    time = args[2]
    CheckStartTime = True
    if type == 'in':
        StartBotAt = str(datetime.datetime.now() + timedelta(minutes=int(time)))[11:16]
        log('Plugin: Starting Bot At [%s]' %StartBotAt)
    elif type == 'at':
        StartBotAt = time
        log('Plugin: Starting Bot At [%s]' %StartBotAt)
    return 0

def StopStart(args):
    global SkipCommand2
    #avoid bot doing command again after restarting
    if SkipCommand2:
        SkipCommand2 = False
        return 0
    stop_bot()
    log("Plugin: Starting Bot In [ 5 seconds ]")
    Timer(5.0, start_bot, ()).start()
    #some cases the bot may not pass over the command again when starting again
    Timer(30.0, ResetSkip1, ()).start()
    SkipCommand2 = True
    return 0

def StartTrace(args):
    global SkipCommand3
    #avoid bot doing command again after restarting
    if SkipCommand3:
        SkipCommand3 = False
        return 0
    elif len(args) == 2:
        stop_bot()
        player = args[1]
        if start_trace(player):
            log('Plugin: Starting to trace [%s]' %player)
            return 0
        else:
            log('Plugin: Player [%s] is not near.. Continuing' %player)
            SkipCommand3 = True
            Timer(1.0, start_bot, ()).start()
            #some cases the bot may not pass over the command again when starting again
            Timer(30.0, ResetSkip2, ()).start()
            return 0
    log('Plugin: Incorrect StartTrace format')
    return 0

def WaitParty(args):
    # Read member count
    memberCount = 8
    if len(args) >= 2:
        memberCount = round(float(args[1]))
    # Check position
    p = get_position()
    if GetPartyMembersCount() < memberCount:
        # Stop scripting
        stop_bot()
        # set automatically the training area
        set_training_position(p['region'], p['x'], p['y'], p['z'])
        Timer(0.001, Party,[memberCount, p]).start()
    # otherwise continue normally
    else:
        party = get_party()
        for key in party:
            log("Plugin: All Members Are Ready! Members In Party: ["+str(party[key]['name'])+"]")
    return 0

def GetPartyMembersCount():
    # It will be counting myself
    party = get_party()
    if party:
        return len(party)
    return 1

def Party(MemberCount,position):
    log('Plugin: Waiting for #' + str(MemberCount) + ' members to continue')
    while GetPartyMembersCount() < MemberCount:
        sleep(0.5)
    stop_bot()
    # Setting training area far away. The bot should continue where he was at the script
    set_training_position(0, 0, 0, 0)
    # Wait for bot to calm down and move back to the starting point
    log("Plugin: Getting back to the script...")
    Timer(0.5, move_to, [position['x'], position['y'], position['z']]).start()
    # give it some time to reach the movement
    Timer(1.5, start_bot).start()


# Called every 500ms
def event_loop():
    global delay_counter, CheckStartTime, SkipCommand1, CheckCloseTime
    if inGame and followActivated:
        player = near_party_player(followPlayer)
        # check if is near
        if not player:
            return
        # check distance to the player
        if followDistance > 0:
            p = get_position()
            playerDistance = round(GetDistance(p['x'],p['y'],player['x'],player['y']),2)
            # check if has to move
            if followDistance < playerDistance:
                # generate vector unit
                x_unit = (player['x'] - p['x']) / playerDistance
                y_unit = (player['y'] - p['y']) / playerDistance
                # distance to move
                movementDistance = playerDistance-followDistance
                move_to(movementDistance * x_unit + p['x'],movementDistance * y_unit + p['y'],0)
        else:
            # Avoid negative numbers
            move_to(player['x'],player['y'],0)
    elif CheckStartTime:
        delay_counter += 500
        if delay_counter >= 60000:
            delay_counter = 0
            CurrentTime = str(datetime.datetime.now())[11:16]
            if CurrentTime == StartBotAt:
                CheckStartTime = False
                SkipCommand1 = True
                log('Plugin: Starting Bot')
                start_bot()

    elif CheckCloseTime:
        delay_counter += 500
        if delay_counter >= 60000:
            delay_counter = 0
            CurrentTime = str(datetime.datetime.now())[11:16]
            if CurrentTime == CloseBotAt:
                CheckCloseTime = False
                Terminate()




# Plugin loaded
log("Plugin: "+pName+" ❴ E n c r y p t ❵ v"+pVersion+" successfully loaded ✔")

if os.path.exists(getPath()):
    # Adding RELOAD plugin support
    loadConfigs()
else:
    # Creating configs folder
    os.makedirs(getPath())
    log('Plugin: '+pName+' folder has been created')