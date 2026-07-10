from phBot import *
from threading import Timer
import phBotChat
import QtBind
import struct
import random
import json
import os
import sqlite3

pName = 'Myth'
pVersion = '1.8.2'
pUrl = 'https://raw.githubusercontent.com/JellyBitz/phBot-xPlugins/master/xControl_6.py'

# ______________________________ Initializing ______________________________ #

# Globals
inGame = None
followActivated = False
followPlayer = ''
followDistance = 0
stoppicking = True
# drops = {}

# Graphic user interface
gui = QtBind.init(__name__,pName)
QtBind.createLabel(gui,'Control your party using in-game chat. Leader writes commands and your character will follow it.',11,11)

QtBind.createLabel(gui,'< COMMAND (uppercased) #Variable (required) #Variable? (optional) >',11,30)
QtBind.createLabel(gui,'- START : Start bot\n- STOP : Stop bot\n- TRACE #Player? : Start trace to leader or another player\n- NOTRACE : Stop trace\n- RETURN : Use some "Return Scroll" from your inventory\n- TP #A #B : Use teleport from location A to B\n- RECALL #Town : Set recall on city portal\n- ZERK : Use berserker mode if is available\n- GETOUT : Left party\n- MOVEON #Radius? : Set a random movement\n- MOUNT #PetType? : Mount horse by default\n- DISMOUNT #PetType? : Dismount horse by default\n- SETPOS #PosX? #PosY? #Region? #PosZ? : Set training position\n- SETRADIUS #Radius? : Set training radius\n- SETSCRIPT #Path? : Change script path for training area\n- SETAREA #Name : Changes training area by config name\n- PROFILE #Name? : Loads a profile by his name\n- DC : Disconnect from game',15,45)
QtBind.createLabel(gui,'- INJECT #Opcode #Encrypted? #Data? : Inject packet\n- CHAT #Type #Message : Send any message type\n- FOLLOW #Player? #Distance? : Trace a party player using distance\n- NOFOLLOW : Stop following\n- JUMP : Generate knockback visual effect\n- SIT : Sit or Stand up, depends\n- CAPE #Type? : Use PVP Cape\n- EQUIP #ItemName : Equips an item from inventory\n- UNEQUIP #ItemName : Unequips item from character\n- REVERSE #Type #Name?\n- GETPOS : Gets current position',345,80)

tbxLeaders = QtBind.createLineEdit(gui,"",525,11,110,20)
lstLeaders = QtBind.createList(gui,525,32,110,38)
btnAddLeader = QtBind.createButton(gui,'btnAddLeader_clicked',"    Add   ",635,10)
btnRemLeader = QtBind.createButton(gui,'btnRemLeader_clicked',"     Remove     ",635,32)

# ______________________________ Methods ______________________________ #

# Return xControl folder path
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
			QtBind.setText(gui, tbxLeaders,"")
			log('Plugin: Leader added ['+player+']')

# Remove leader selected from list
def btnRemLeader_clicked():
	if inGame:
		selectedItem = QtBind.text(gui,lstLeaders)
		if selectedItem:
			if os.path.exists(getConfig()):
				data = {"Leaders":[]}
				with open(getConfig(), 'r') as f:
					data = json.load(f)
				try:
					# remove leader nickname from file if exists
					data["Leaders"].remove(selectedItem)
					with open(getConfig(),"w") as f:
						f.write(json.dumps(data, indent=4, sort_keys=True))
				except:
					pass # just ignore file if doesn't exist
			QtBind.remove(gui,lstLeaders,selectedItem)
			log('Plugin: Leader removed ['+selectedItem+']')

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
				Timer(2.0, log, ("Plugin: Teleporting to ["+destination+"]")).start()
				return
		log('Plugin: NPC not found. Wrong NPC name or servername')
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
	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			sn = item['servername']
			# Search some kind vehicle by servername
			if '_C_' in sn:
				packet = struct.pack('B',slot)
				packet += struct.pack('H',4588 + (1 if sn.endswith('_SCROLL') else 0)) # Silk scroll
				inject_joymax(0x704C,packet,True)
				return True
	log('Plugin: Horse not found at your inventory')
	return False

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
	character_data = get_character_data()
	# vSRO
	if locale == 22:
		with open(bot_path+"/vSRO.json","r") as f:
			data = json.load(f)
		# Match data with the current server name
		server = character_data['server']
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

# Terminate PHBOT INSTANCE
def Terminate():
	log("Plugin: Closing bot...")
	os.kill(os.getpid(),9)

# Pick Drop Goods
def inject_pick(id, tradeGood):
    packet = b'\x01\x02\x01' + struct.pack('I', id)
    inject_joymax(0x7074, packet, False)
    log('Plugin '+pName+': Picked up "'+tradeGood['name']+'" ')

def getDrops():
	global drops
	drops = get_drops()

def pick_loop():
	global stoppicking
	if stoppicking:
		log('stopped')
	if not stoppicking:
		if not 0 == len(drops):
			timer = Timer(0.5, pick_loop)
			timer.start()
			droppedItem = drops.popitem()
			id = droppedItem[0]
			tradeGood = droppedItem[1]
			xcoor = tradeGood['x']
			ycoor = tradeGood['y']
			#move to item coordinate
			move_to(xcoor, ycoor, 0.0)
			inject_pick(id, tradeGood)
		else:
			getDrops()
			if not 0 == len(drops):
				log('Not all items picked, Picking again')
				pick_loop()
			else:
				log('No drops')
		
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
	# Remove guild name from union chat messages
	if t == 11:
		msg = msg.split(': ',1)[1]
	# Check player at leader list or a Discord message
	if player and lstLeaders_exist(player) or t == 100:
		# Parsing message command
		if msg == "S":
			start_bot()
			log("Plugin: Bot started")
		elif msg == "D":
			stop_bot()
			log("Plugin: Bot stopped")
		elif msg == "GAS":
			if set_training_area("GAS"):
				log("Selling Goods Alex")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg == "GAB":
			if set_training_area("GAB"):
				log("Selling Goods Alex")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg == "ASC":
			log("Going Alex Samar Capadocia")
			set_training_area("ASC")
			start_bot()
		elif msg == "GSS":
			if set_training_area("GSS"):
				log("Selling Goods Samar")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg == "GSB":
			if set_training_area("GSB"):
				log("Buying Goods Samar")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg == "GCB":
			if set_training_area("GCB"):
				log("Buying Goods Cons")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg == "GCS":
			if set_training_area("GCS"):
				log("Selling Goods Cons")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg == "GHB":
			if set_training_area("GHB"):
				log("Buying Goods Hotan")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg == "GHS":
			if set_training_area("GHS"):
				log("Selling Goods Hotan")
				start_bot()
			else:
				log("Training Area Not Found")
		elif msg.startswith("T"):
			# deletes empty spaces on right
			msg = msg.rstrip()
			if msg == "T":
				if start_trace(player):
					log("Plugin: Starting trace to ["+player+"]")
			else:
				msg = msg[5:].split()[0]
				if start_trace(msg):
					log("Plugin: Starting trace to ["+msg+"]")
		elif msg == "N":
			stop_trace()
			log("Plugin: Trace stopped")
		elif msg.startswith("A"):
			# deletes empty spaces on right
			msg = msg.rstrip()
			if msg == "A":
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
		elif msg == 'A':
			# Check current position
			pos = get_position()
			phBotChat.Private(player,'My position is (X:%.1f,Y:%.1f,Z:%1f,Region:%d)'%(pos['x'],pos['y'],pos['z'],pos['region']))
		elif msg.startswith("SETRADIUS"):
			# deletes empty spaces on right
			msg = msg.rstrip()
			if msg == "SETRADIUS":
				# set default radius
				radius = 35
				set_training_radius(radius)
				log("Plugin: Training radius reseted to "+str(radius)+" m.")
			else:
				try:
					# split and parse movement radius
					radius = int(float(msg[9:].split()[0]))
					# to absolute
					radius = (radius if radius > 0 else radius*-1)
					set_training_radius(radius)
					log("Plugin: Training radius set to "+str(radius)+" m.")
				except:
					log("Plugin: Wrong training radius value!")
		elif msg.startswith('SETSCRIPT'):
			# deletes empty spaces on right
			msg = msg.rstrip()
			if msg == 'SETSCRIPT':
				# reset script
				set_training_script('')
				log('Plugin: Training script path has been reseted')
			else:
				# change script to the path specified
				set_training_script(msg[9:])
				log('Plugin: Training script path has been changed')
		elif msg.startswith('SETAREA '):
			# deletes empty spaces on right
			msg = msg[8:]
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
		elif msg == "J":
			inject_teleport("Donwhang","Jangan") or inject_teleport("Alexandria (North)","Jangan") or inject_teleport("Alexandria (South)","Jangan") or inject_teleport("Town of Darkness","Jangan")
		elif msg == "DW":
			inject_teleport("Jangan","Donwhang") or inject_teleport("Hotan","Donwhang")
		elif msg == "H":
			inject_teleport("Donwhang","Hotan") or inject_teleport("Samarkand","Hotan") or inject_teleport("Alexandria (North)","Hotan") or inject_teleport("Alexandria (South)","Hotan") or inject_teleport("Baghdad","Hotan")
		elif msg == "SK":
			inject_teleport("Hotan","Samarkand") or inject_teleport("Constantinople","Samarkand")
		elif msg == "C":
			inject_teleport("Samarkand","Constantinople")
		elif msg == "AS":
			inject_teleport("Jangan","Alexandria (South)") or inject_teleport("Hotan","Alexandria (South)") or inject_teleport("Alexandria (North)","Alexandria (South)") or inject_teleport("Baghdad","Alexandria (South)")
		elif msg == "AN":
			inject_teleport("Jangan","Alexandria (North)") or inject_teleport("Hotan","Alexandria (North)") or inject_teleport("Alexandria (South)","Alexandria (North)") or inject_teleport("Baghdad","Alexandria (North)")
		elif msg == "B":
			inject_teleport("Hotan","Baghdad")
		elif msg == "LQ":
			inject_teleport("Kings Valley","Pharaoh tomb (beginner)")
		elif msg == "RN":
			inject_teleport("Hell Room","Town of Darkness")
		elif msg == "K":
			inject_teleport("Kotsh Unique Gate","Kotsh Unique Room")
		elif msg == "Q1":
			inject_teleport("Harbor Manager Marwa","Pirate Morgun") or inject_teleport("Pirate Morgun","Harbor Manager Gale") or inject_teleport("Harbor Manager Gale","Pirate Morgun") or inject_teleport("Priate Blackbeard","Harbor Manager Gale") or inject_teleport("Aircraft Ticket Seller Shard","Aircraft Ticket Seller Sangnia") or inject_teleport("Aircraft Ticket Seller Sangnia","Aircraft Ticket Seller Shard") or inject_teleport("Tunnel Manager Salhap","Tunnel Manager Maryokuk") or inject_teleport("Tunnel Manager Maryokuk","Tunnel Manager Salhap") or inject_teleport("Tunnel Manager Topni","Tunnel Manager Asui") or inject_teleport("Tunnel Manager Asui","Tunnel Manager Topni") or inject_teleport("Aircraft Ticket Seller Saena","Aircraft Ticket Seller Ajati") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Ajati") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Ajati") or inject_teleport("Boat Ticket Seller Rahan","Boat Ticket Seller Salmai") or inject_teleport("Boat Ticket Seller Salmai","Boat Ticket Seller Rahan") or inject_teleport("Boat Ticket Seller Asimo","Boat Ticket Seller Asa") or inject_teleport("Boat Ticket Seller Asa","Boat Ticket Seller Asimo") or inject_teleport("Ferry Ticket Seller Tayun","Ferry Ticket Seller Doji") or inject_teleport("Ferry Ticket Seller Doji","Ferry Ticket Seller Tayun") or inject_teleport("Ferry Ticket Seller Hageuk","Ferry Ticket Seller Chau") or inject_teleport("Ferry Ticket Seller Chau","Ferry Ticket Seller Hageuk") or inject_teleport("forbidden plain","Kings Valley") or inject_teleport("Kings Valley","forbidden plain") or inject_teleport("abundance ground","Storm and cloud Desert") or inject_teleport("Storm and cloud Desert","abundance ground") or inject_teleport("Underwater Route #2","Underwater Route #3") or inject_teleport("Underwater Route #3","Hotan") or inject_teleport("Kings Valley","Samarkand")
		elif msg == "Q2":
			inject_teleport("Harbor Manager Marwa","Priate Blackbeard") or inject_teleport("Harbor Manager Gale","Priate Blackbeard") or inject_teleport("Pirate Morgun","Harbor Manager Marwa") or inject_teleport("Priate Blackbeard","Harbor Manager Marwa") or inject_teleport("Aircraft Ticket Seller Saena","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Sayun") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Poy") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Sayun") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Poy")
		elif msg == "Q3":
			inject_teleport("Harbor Manager Marwa","Harbor Manager Gale") or inject_teleport("Harbor Manager Gale","Harbor Manager Marwa") or inject_teleport("Aircraft Ticket Seller Ajati","Aircraft Ticket Seller Saena") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Saena")
		elif msg == "RTS":
			# Quickly check if is dead
			character = get_character_data()
			if character['hp'] == 0:
				# RIP
				log('Plugin: Resurrecting at town...')
				inject_joymax(0x3053,b'\x01',False)
			else:
				log('Plugin: Trying to use return scroll...')
				# Avoid high CPU usage with too many chars at the same time
				Timer(random.uniform(0.5,2),use_return_scroll).start()
		elif msg.startswith("TP"):
			# deletes command header and whatever used as separator
			msg = msg[3:]
			if not msg:
				return
			# select split char
			split = ',' if ',' in msg else ' '
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
			distance = 10
			if msg != "F":
				# Check params
				msg = msg[6:].split()
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
		elif msg == "DCD":
			log("Plugin: Disconnecting...")
			disconnect()
		elif msg.startswith("MT"):
			# default value
			pet = "transport"
			if msg != "MT":
				msg = msg[5:].split()
				if msg:
					pet = msg[0]
			# Try mount pet
			if MountPet(pet):
				log("Plugin: Mounting pet ["+pet+"]")
		elif msg.startswith("DX"):
			# default value
			pet = "transport"
			if msg != "DX":
				msg = msg[8:].split()
				if msg:
					pet = msg[0]
			# Try dismount pet
			if DismountPet(pet):
				log("Plugin: Dismounting pet ["+pet+"]")
		elif msg == "GP":
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
		elif msg == "PG":
			global stoppicking
			stoppicking = False
			global drops
			drops = get_drops()
			pick_loop()
		elif msg == 'SPG':
			stoppicking = True
		elif msg == "MWE":
			log('mounting')
			mountToUse = 'War elephant scroll - Trader'
			item = GetItemByExpression(lambda n,s: mountToUse in n or mountToUse == s,13)
			if item:
				UseItem(item)
		elif msg == "MDH":
			log('mounting')
			mountToUse = 'Dark horse trade pet - Trader'
			item = GetItemByExpression(lambda n,s: mountToUse in n or mountToUse == s,13)
			if item:
				UseItem(item)
		elif msg == "MDINO":
			log('mounting')
			mountToUse = 'Dino - Trader'
			item = GetItemByExpression(lambda n,s: mountToUse in n or mountToUse == s,13)
			if item:
				UseItem(item)
		elif msg == "ZXC":
			gdi = get_dropped_items()
			with open('out.txt', 'w') as f:
				print(gdi, 'out.txt', file=f)
		if msg.startswith('LEADS '):
			msg = msg[6:]
			log(msg)
			if inGame:
				player = msg
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
					QtBind.setText(gui, tbxLeaders,"")
					log('Plugin: Leader added ['+player+']')
		elif msg.startswith('RLEADS '):
			msg = msg[7:]
			if inGame:
				selectedItem = msg
				if selectedItem:
					if os.path.exists(getConfig()):
						data = {"Leaders":[]}
						with open(getConfig(), 'r') as f:
							data = json.load(f)
						try:
							# remove leader nickname from file if exists
							data["Leaders"].remove(selectedItem)
							with open(getConfig(),"w") as f:
								f.write(json.dumps(data, indent=4, sort_keys=True))
						except:
							pass # just ignore file if doesn't exist
					QtBind.remove(gui,lstLeaders,selectedItem)
					log('Plugin: Leader removed ['+selectedItem+']')	
	# if msg == "DCTERMINATE":
	# 	Terminate()	
	if msg == "YAWAAA":
		if player == inGame["job_name"] or player == inGame["name"]:
			Terminate()

# Called every 500ms
def event_loop():
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
				log("Following "+followPlayer+"...")
				move_to(movementDistance * x_unit + p['x'],movementDistance * y_unit + p['y'],0)
		else:
			# Avoid negative numbers
			log("Following "+followPlayer+"...")
			move_to(player['x'],player['y'],0)

# Plugin loaded
log("Plugin: "+pName+" v"+pVersion+" successfully loaded")

if os.path.exists(getPath()):
	# Adding RELOAD plugin support
	loadConfigs()
else:
	# Creating configs folder
	os.makedirs(getPath())
	log('Plugin: '+pName+' folder has been created')
