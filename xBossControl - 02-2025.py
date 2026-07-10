from phBot import *
from threading import Timer
import phBotChat
import QtBind
import struct
import random
import json
import os
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
import threading
import phBotChat
import QtBind
import struct
import random
import json
import os
import sqlite3

pName = 'xControl'
pVersion = '02/2025'
pUrl = 'https://raw.githubusercontent.com/JellyBitz/phBot-xPlugins/master/xControl.py'

# ______________________________ Initializing ______________________________ #

# Globals
inGame = None
followActivated = False
followPlayer = ''
followDistance = 0
stoppicking = True
# drops = {}

# Graphic user interface
gui = QtBind.init(__name__,"xBossControl  1")
QtBind.createLabel(gui,'Control your party using in-game chat. Leader writes commands and your character will follow it.\n ❴ xBossControl ❵ have many features more than the normal xControl.',11,10)

QtBind.createLabel(gui,'< COMMAND (uppercased) #Variable (required) #Variable? (optional) >',11,37)
QtBind.createLabel(gui,'- ( S ) : Start bot or ( SP ) : Stop bot\n- ( T or J) : to make them trace you ( TT #name ) to trace player\n- ( N ) : Stop trace\n- ( R ) : Use some "Return Scroll" from your inventory\n- ( RT ) : Use some "Return Scroll" from your inventory\n- ( TP #A #B ) : Use teleport from location A to B\n- ( RC #Town ) : Set recall on city portal\n- ( Z ) : Use berserker mode if is available\n- ( GO ) : Left party\n- ( MOVEON #Radius? ) : Set a random movement\n- ( M or MT #PetType? ) : Mount horse by default\n- ( D or DS #PetType? ) : Dismount horse by default\n- ( A #PosX? #PosY? #Region? #PosZ? ) : Set training position\n- ( SETR #Radius? ) : Set training radius\n- ( ST #Path? ) : Change script path for training area\n- ( SA #Name ) : Changes training area by config name\n- ( PF #Name? ) : Loads a profile by his name\n- ( DC ) : Disconnect from game\n- ( TN ) : Terminate current transport\n- ( USE #ItemName ) : Use item from inventory',15,50)
QtBind.createLabel(gui,'- ( INJECT #Opcode #Encrypted? #Data? ) : Inject packet\n- ( CHAT #Type #Message ) : Send any message type\n- ( F ) : to make them follow you\n- ( F #Player? #Distance? ) : Trace a party player using distance\n- ( NF ) : Stop following\n- ( JUMP ) : Generate knockback visual effect\n- ( SIT ) : Sit or Stand up, depends\n- ( CAPE #Type? ) : Use PVP Cape\n- ( EQ #ItemName ) : Equips an item from inventory\n- ( UQ #ItemName ) : Unequips item from character\n- ( RV #Type #Name?) : to use REVERSE\n- ( PG ) : Pick Goods /// ( SPG ) : Stop Pick Goods ',345,140)

# Graphic user interface (*)
gui_ = QtBind.init(__name__,"xBossControl  2")

QtBind.createLabel(gui_,'<- This Page Have Extra commands In xBossControl ->',210,11)

QtBind.createLabel(gui_,'- ( J ) : Teleport to Jangan \n- ( H ) : Teleport to Hotan\n- ( SK ) : Teleport to Samarkand\n- ( B ) : Teleport to Baghdad \n\n- ( Q1 ) : Teleport to First Option at List\n- ( Q2 ): Teleport to Second Option\n- ( Q3 ): Teleport to Third Option\n \n- ( KP1 ) : If you want to go Holy Water Temple (Beginner) \n- ( KP2 ) : If you want to go Holy Water Temple (Intermediate)\n- ( KP3 ) : If you want to go Holy Water Temple (Advance)\n- ( J5 ) : If you want to go Jupiter Temple ( Room 5 ) \n- ( J6 ) : If you want to go Jupiter Temple ( Room 6 )\n \n- ( PET1 ) : Use Dino\n- ( PET2 ) : Use Dark Horse\n- ( PET3 ) : Use White Elephant\n- ( PET4 ) : Use War Elephant',15,45)
QtBind.createLabel(gui_,'- ( DW ) : Teleport to Donwhang\n- ( LQ ) : Teleport to Pharaoh tomb (beginner)\n- ( C ) : Teleport to Constantinople\n- ( RN ) : Teleport to Town of Darkness\n\n- ( ADDL #PlayerName ) to Add Leader in list\n- ( REML #PlayerName ) to Remove Leader in list',345,45)


tbxLeaders = QtBind.createLineEdit(gui,"",525,11,110,20)
lstLeaders = QtBind.createList(gui,525,32,110,100)
btnAddLeader = QtBind.createButton(gui,'btnAddLeader_clicked',"    Add   ",635,10)
btnRemLeader = QtBind.createButton(gui,'btnRemLeader_clicked',"     Remove     ",635,32)

#disable mode

cbxEnabled = QtBind.createCheckBox(gui,'cbxDoNothing','Disable T Command, J still possible',310,110)


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

Name_1 = [236]
Name_2 = [237]

def ReturnScroll(name):
	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			sn = item['name']
			if sn.startswith('Instant Return Scroll') or sn == 'Special Return Scroll' or sn == 'Bandit Den Return Scroll':
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
	# Remove guild name from union chat messages
	if t == 11:
		msg = msg.split(': ',1)[1]
	# Check player at leader list or a Discord message
	if player and lstLeaders_exist(player) or t == 100:
		# Parsing message command
		if msg == "S":
			start_bot()
			log("Plugin: Bot started")
		elif msg == "SP":
			stop_bot()
			log("Plugin: Bot stopped")




		elif msg == "T" or msg == "J":
			# deletes empty spaces on right
			msg = msg.rstrip()
			if msg == "T" and not QtBind.isChecked(gui,cbxEnabled) or msg == "J":
				if start_trace(player):
					log("Plugin: Starting trace to ["+player+"]")
			else:
				msg = msg[1:].strip()  # Enlève les espaces inutiles
				msg_split = msg.split()  # Découpe la chaîne en liste de mots

				if msg_split:  # Vérifie que la liste n'est pas vide avant d'accéder à [0]
					msg = msg.split()[0]  # Évite une erreur si la chaîne est vide
					if start_trace(msg):
						log("Plugin: Starting trace to ["+msg+"]")
				else:
					log("Plugin: Bot wont trace, T is Disabled")




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
		elif msg == 'A':
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

		elif msg.startswith('ST'):
			# deletes empty spaces on right
			msg = msg.rstrip()
			if msg == 'ST':
				# reset script
				set_training_script('')
				log('Plugin: Training script path has been reseted')
			else:
				# change script to the path specified
				set_training_script(msg[9:])
				log('Plugin: Training script path has been changed')
		elif msg.startswith('SA '):
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
		elif msg == "Z":
			log("Plugin: Using Berserker mode")
			inject_joymax(0x70A7,b'\x01',False)

# _____________________________ Towns TP _____________________________ #

		elif msg.startswith("J"):
			inject_teleport("Donwhang","Jangan") or inject_teleport("Alexandria (North)","Jangan") or inject_teleport("Alexandria (South)","Jangan") or inject_teleport("Town of Darkness","Jangan")
		elif msg.startswith("DW"):
			inject_teleport("Jangan","Donwhang") or inject_teleport("Hotan","Donwhang")
		elif msg.startswith("H"):
			inject_teleport("Donwhang","Hotan") or inject_teleport("Samarkand","Hotan") or inject_teleport("Alexandria (North)","Hotan") or inject_teleport("Alexandria (South)","Hotan") or inject_teleport("Baghdad","Hotan")
		elif msg.startswith("SK"):
			inject_teleport("Hotan","Samarkand") or inject_teleport("Constantinople","Samarkand")
		elif msg.startswith("C"):
			inject_teleport("Samarkand","Constantinople")
		elif msg.startswith("B"):
			inject_teleport("Hotan","Baghdad")
		elif msg.startswith("LQ"):
			inject_teleport("Kings Valley","Pharaoh tomb (beginner)")
		elif msg.startswith("RN"):
			inject_teleport("Hell Room","Town of Darkness")
		elif msg.startswith("K"):
			inject_teleport("Kotsh Unique Gate","Kotsh Unique Room")

# ______________________________ Trade TP ______________________________ #

		elif msg.startswith("Q1"):
			inject_teleport("Harbor Manager Marwa","Pirate Morgun") or inject_teleport("Pirate Morgun","Harbor Manager Gale") or inject_teleport("Harbor Manager Gale","Pirate Morgun") or inject_teleport("Priate Blackbeard","Harbor Manager Gale") or inject_teleport("Aircraft Ticket Seller Shard","Aircraft Ticket Seller Sangnia") or inject_teleport("Aircraft Ticket Seller Sangnia","Aircraft Ticket Seller Shard") or inject_teleport("Tunnel Manager Salhap","Tunnel Manager Maryokuk") or inject_teleport("Tunnel Manager Maryokuk","Tunnel Manager Salhap") or inject_teleport("Tunnel Manager Topni","Tunnel Manager Asui") or inject_teleport("Tunnel Manager Asui","Tunnel Manager Topni") or inject_teleport("Aircraft Ticket Seller Saena","Aircraft Ticket Seller Ajati") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Ajati") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Ajati") or inject_teleport("Boat Ticket Seller Rahan","Boat Ticket Seller Salmai") or inject_teleport("Boat Ticket Seller Salmai","Boat Ticket Seller Rahan") or inject_teleport("Boat Ticket Seller Asimo","Boat Ticket Seller Asa") or inject_teleport("Boat Ticket Seller Asa","Boat Ticket Seller Asimo") or inject_teleport("Ferry Ticket Seller Tayun","Ferry Ticket Seller Doji") or inject_teleport("Ferry Ticket Seller Doji","Ferry Ticket Seller Tayun") or inject_teleport("Ferry Ticket Seller Hageuk","Ferry Ticket Seller Chau") or inject_teleport("Ferry Ticket Seller Chau","Ferry Ticket Seller Hageuk") or inject_teleport("forbidden plain","Kings Valley") or inject_teleport("Kings Valley","forbidden plain") or inject_teleport("abundance ground","Storm and cloud Desert") or inject_teleport("Storm and cloud Desert","abundance ground") or inject_teleport("Underwater Route #2","Underwater Route #3") or inject_teleport("Underwater Route #3","Hotan") or inject_teleport("Temple","sanctum of Atonement") or inject_teleport("Storm and cloud Desert","Temple")
		elif msg.startswith("Q2"):
			inject_teleport("Harbor Manager Marwa","Priate Blackbeard") or inject_teleport("Harbor Manager Gale","Priate Blackbeard") or inject_teleport("Pirate Morgun","Harbor Manager Marwa") or inject_teleport("Priate Blackbeard","Harbor Manager Marwa") or inject_teleport("Aircraft Ticket Seller Saena","Airship Ticket Seller Dawari") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Sayun") or inject_teleport("Aircraft Ticket Seller Sayun","Airship Ticket Seller Poy") or inject_teleport("Airship Ticket Seller Poy","Aircraft Ticket Seller Sayun") or inject_teleport("Aircraft Ticket Seller Ajati","Airship Ticket Seller Poy")
		elif msg.startswith("Q3"):
			inject_teleport("Harbor Manager Marwa","Harbor Manager Gale") or inject_teleport("Harbor Manager Gale","Harbor Manager Marwa") or inject_teleport("Aircraft Ticket Seller Ajati","Aircraft Ticket Seller Saena") or inject_teleport("Airship Ticket Seller Dawari","Aircraft Ticket Seller Saena")

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

# ____________________________ New ___________________________ #

		elif msg == "R":
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
		elif msg.startswith("PF"):
			if msg == "PF":
				if set_profile('Default'):
					log("Plugin: Setting Default profile")
			else:
				msg = msg[7:]
				if set_profile(msg):
					log("Plugin: Setting "+msg+" profile")
		elif msg == "DC":
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
		elif msg == "TN":
			pets = get_pets()
			if pets:
				for k, v in pets.items():
					if v['type'] == 'transport':
						log(f'Plugin: Terminating pet [{v["name"]}]')
						inject_joymax(0x70C6, struct.pack('I', k), False)
		elif msg == "GO":
			# Check if has party
			if get_party():
				# Left it
				log("Plugin: Leaving the party..")
				inject_joymax(0x7061,b'',False)
		elif msg.startswith("RC "):
			msg = msg[7:]
			if msg:
				npcUID = GetNPCUniqueID(msg)
				if npcUID > 0:
					log("Plugin: Designating recall to \""+msg.title()+"\"...")
					inject_joymax(0x7059, struct.pack('I',npcUID), False)
		elif msg.startswith("EQ "):
			msg = msg[6:]
			if msg:
				# search item with similar name or exact server name
				item = GetItemByExpression(lambda n,s: msg in n or msg == s,13)
				if item:
					EquipItem(item)
		elif msg.startswith("UQ "):
			msg = msg[8:]
			if msg:
				# search item with similar name or exact server name
				item = GetItemByExpression(lambda n,s: msg in n or msg == s,0,12)
				if item:
					UnequipItem(item)
		elif msg.startswith("RV "):
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
		elif msg.startswith('ADDL '):
			msg = msg[5:]
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
		elif msg.startswith('REML '):
			msg = msg[5:]
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
		elif msg == "PG":
			global stoppicking
			stoppicking = False
			global drops
			drops = get_drops()
			pick_loop()
		elif msg == 'SPG':
			stoppicking = True
		elif msg.startswith("USE "):
			# remove command
			msg = msg[4:]
			if msg:
				# search item with similar name or exact server name
				item = GetItemByExpression(lambda n,s: msg in n or msg == s,13)
				if item:
					UseItem(item)

		# Transport Commands
		if msg == ("PET1"):
			items = get_inventory()['items']
			for slot, item in enumerate(items):
				if item:
					name = item['servername']
					if name == ('ITEM_COS_T_ULTRA'):
						p = struct.pack('B', slot)  # Inventory Slot
						p += b'\xED\x11'
						log(f'Plugin: Using transport "{item["name"]}"...')
						inject_joymax(0x704C, p, True)
						return
			log(r'Plugin: You dont have any transport pet')
		elif msg == ("PET2"):
			items = get_inventory()['items']
			for slot, item in enumerate(items):
				if item:
					name = item['servername']
					if name == ('ITEM_COS_T_DARKHORSE_SCROLL'):
						p = struct.pack('B', slot)  # Inventory Slot
						p += b'\xED\x11'
						log(f'Plugin: Using transport "{item["name"]}"...')
						inject_joymax(0x704C, p, True)
						return
			log(r'Plugin: You dont have any transport pet')
		elif msg == ("PET3"):
			items = get_inventory()['items']
			for slot, item in enumerate(items):
				if item:
					name = item['servername']
					if name == ('ITEM_COS_T_WHITEELEPHANT_SCROLL'):
						p = struct.pack('B', slot)  # Inventory Slot
						p += b'\xED\x11'
						log(f'Plugin: Using transport "{item["name"]}"...')
						inject_joymax(0x704C, p, True)
						return
			log(r'Plugin: You dont have any transport pet')
		elif msg == ("PET4"):
			items = get_inventory()['items']
			for slot, item in enumerate(items):
				if item:
					name = item['servername']
					if name == ('ITEM_COS_T_WARELEPHANT_SCROLL'):
						p = struct.pack('B', slot)  # Inventory Slot
						p += b'\xED\x11'
						log(f'Plugin: Using transport "{item["name"]}"...')
						inject_joymax(0x704C, p, True)
						return
			log(r'Plugin: You dont have any transport pet')



# ____________________________ Script Arguments ___________________________ #

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

#RemoveSkill,skillname...Remove the skill if active
def RemoveSkill(args):
	locale = get_locale()
	if locale == 18 or locale == 56:
		RemSkill = args[1]
		skills = get_active_skills()
		for ID, skill in skills.items():
			if skill['name'] == RemSkill:
				packet = b'\x01\x05'
				packet += struct.pack('<I', ID)
				packet += b'\x00'
				inject_joymax(0x7074,packet,False)
				log('Plugin: Removing skill [%s]' %RemSkill)
				return 0
		log('Plugin: Skill is not active')
		return 0
	log('Plugin: Only supported on iSRO or TRSRO, contact me to add support for your server')
	return 0

#Drop,itemname... drops the first stack of the specified item
def Drop(args):
	locale = get_locale()
	if locale == 18 or locale == 56:
		DropItem = args[1]
		items = get_inventory()['items']
		for slot, item in enumerate(items):
			if item:
				name = item['name']
				if name == DropItem:
					p = b'\x07' # static stuff maybe
					p += struct.pack('B', slot)
					log('Plugin: Dropping item [%s][%s]' %(item['quantity'],name))
					inject_joymax(0x7034,p,True)
					return 0
		log(r'Plugin: You Dont Have any Items to Drop')
		return 0
	log('Plugin: Only supported on iSRO or TRSRO, contact me to add support for your server')
	return 0

#OpenphBot,commandlinearguments..opens a bot with the specified arguements
def OpenphBot(args):
	cmdargs = args[1]
	if os.path.exists(path + "phBot.exe"):
		subprocess.Popen(path + "phBot.exe " + cmdargs)
		log('Plugin: Opening a new bot')
		return 0
	log('Plugin: Invalid path to bot')
	return 0

	
def event_loop():
	global delay_counter, CheckStartTime, SkipCommand, CheckCloseTime
	if CheckStartTime:
		delay_counter += 500
		if delay_counter >= 60000:
			delay_counter = 0
			CurrentTime = str(datetime.datetime.now())[11:16]
			if CurrentTime == StartBotAt:
				CheckStartTime = False
				SkipCommand = True
				log('Plugin: Starting Bot')
				start_bot()

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
log("Plugin: "+pName+" ❴ OldDaddys <3 ❵ v"+pVersion+" successfully loaded ✔")

if os.path.exists(getPath()):
	# Adding RELOAD plugin support
	loadConfigs()
else:
	# Creating configs folder
	os.makedirs(getPath())
	log('Plugin: '+pName+' folder has been created')
