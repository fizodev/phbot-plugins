from phBot import *
import QtBind
from threading import Timer
from time import sleep
import sqlite3
import json
import struct
import os

pVersion = '1.5.5'
pName = 'xAutoDungeon'
pUrl = 'https://raw.githubusercontent.com/JellyBitz/phBot-xPlugins/master/xAutoDungeon.py'

# ______________________________ Initializing ______________________________ #

DIMENSIONAL_COOLDOWN_DELAY = 7200 # seconds (2 hours)
WAIT_DROPS_DELAY_MAX = 90 # seconds
COUNT_MOBS_DELAY = 1.0 # seconds
MAX_ATTACKING_TIME = 600 # seconds (10 minutes)

# Globals
character_data = None
itemUsedByPlugin = None
dimensionalItemActivated = None
attack_session_id = 0

# Graphic user interface
gui = QtBind.init(__name__,pName)

lblMobs = QtBind.createLabel(gui,'#   Add monster names to ignore    #\n#          from Monster Counter         #',31,6)
tbxMobs = QtBind.createLineEdit(gui,"",31,35,100,20)
lstMobs = QtBind.createList(gui,31,56,176,203)
lstMobsData = []
btnAddMob = QtBind.createButton(gui,'btnAddMob_clicked',"    Add    ",132,34)
btnRemMob = QtBind.createButton(gui,'btnRemMob_clicked',"     Remove     ",80,258)

lblMonsterCounter = QtBind.createLabel(gui,"#                 Monster Counter                 #",520,6)
lstMonsterCounter = QtBind.createList(gui,520,23,197,237)
QtBind.append(gui,lstMonsterCounter,'Name (Type)') # Header

lblPreferences = QtBind.createLabel(gui,"#             Monster Counter preferences            #",240,6)
lstIgnore = []
lstOnlyCount = []

_y = 26
lblGeneral = QtBind.createLabel(gui,'General (0)',240,_y)
cbxIgnoreGeneral = QtBind.createCheckBox(gui,'cbxIgnoreGeneral_clicked','Ignore',345,_y)
cbxOnlyCountGeneral = QtBind.createCheckBox(gui,'cbxOnlyCountGeneral_clicked','Only Count',405,_y)
_y+=20
lblChampion = QtBind.createLabel(gui,'Champion (1)',240,_y)
cbxIgnoreChampion = QtBind.createCheckBox(gui,'cbxIgnoreChampion_clicked','Ignore',345,_y)
cbxOnlyCountChampion = QtBind.createCheckBox(gui,'cbxOnlyCountChampion_clicked','Only Count',405,_y)
_y+=20
lblGiant = QtBind.createLabel(gui,'Giant (4)',240,_y)
cbxIgnoreGiant = QtBind.createCheckBox(gui,'cbxIgnoreGiant_clicked','Ignore',345,_y)
cbxOnlyCountGiant = QtBind.createCheckBox(gui,'cbxOnlyCountGiant_clicked','Only Count',405,_y)
_y+=20
lblTitan = QtBind.createLabel(gui,'Titan (5)',240,_y)
cbxIgnoreTitan = QtBind.createCheckBox(gui,'cbxIgnoreTitan_clicked','Ignore',345,_y)
cbxOnlyCountTitan = QtBind.createCheckBox(gui,'cbxOnlyCountTitan_clicked','Only Count',405,_y)
_y+=20
lblStrong = QtBind.createLabel(gui,'Strong (6)',240,_y)
cbxIgnoreStrong = QtBind.createCheckBox(gui,'cbxIgnoreStrong_clicked','Ignore',345,_y)
cbxOnlyCountStrong = QtBind.createCheckBox(gui,'cbxOnlyCountStrong_clicked','Only Count',405,_y)
_y+=20
lblElite = QtBind.createLabel(gui,'Elite (7)',240,_y)
cbxIgnoreElite = QtBind.createCheckBox(gui,'cbxIgnoreElite_clicked','Ignore',345,_y)
cbxOnlyCountElite = QtBind.createCheckBox(gui,'cbxOnlyCountElite_clicked','Only Count',405,_y)
_y+=20
lblUnique = QtBind.createLabel(gui,'Unique (8)',240,_y)
cbxIgnoreUnique = QtBind.createCheckBox(gui,'cbxIgnoreUnique_clicked','Ignore',345,_y)
cbxOnlyCountUnique = QtBind.createCheckBox(gui,'cbxOnlyCountUnique_clicked','Only Count',405,_y)
_y+=20
lblParty = QtBind.createLabel(gui,'Party (16)',240,_y)
cbxIgnoreParty = QtBind.createCheckBox(gui,'cbxIgnoreParty_clicked','Ignore',345,_y)
cbxOnlyCountParty = QtBind.createCheckBox(gui,'cbxOnlyCountParty_clicked','Only Count',405,_y)
_y+=20
lblChampionParty = QtBind.createLabel(gui,'ChampionParty (17)',240,_y)
cbxIgnoreChampionParty = QtBind.createCheckBox(gui,'cbxIgnoreChampionParty_clicked','Ignore',345,_y)
cbxOnlyCountChampionParty = QtBind.createCheckBox(gui,'cbxOnlyCountChampionParty_clicked','Only Count',405,_y)
_y+=20
lblGiantParty = QtBind.createLabel(gui,'GiantParty (20)',240,_y)
cbxIgnoreGiantParty = QtBind.createCheckBox(gui,'cbxIgnoreGiantParty_clicked','Ignore',345,_y)
cbxOnlyCountGiantParty = QtBind.createCheckBox(gui,'cbxOnlyCountGiantParty_clicked','Only Count',405,_y)

_y+=30
cbxAcceptForgottenWorld = QtBind.createCheckBox(gui,'cbxAcceptForgottenWorld_checked','Accept Forgotten World invitations',240,_y)

# ______________________________ Methods ______________________________ #

def cbxIgnoreGeneral_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",0) # 0 = General
def cbxOnlyCountGeneral_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",0)

def cbxIgnoreChampion_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",1) # 1 = Champion
def cbxOnlyCountChampion_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",1)

def cbxIgnoreGiant_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",4) # 4 = Giant
def cbxOnlyCountGiant_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",4)

def cbxIgnoreTitan_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",5) # 5 = Titan
def cbxOnlyCountTitan_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",5)

def cbxIgnoreStrong_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",6) # 6 = Strong
def cbxOnlyCountStrong_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",6)

def cbxIgnoreElite_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",7) # 7 = Elite
def cbxOnlyCountElite_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",7)

def cbxIgnoreUnique_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",8) # 8 = Unique
def cbxOnlyCountUnique_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",8)

def cbxIgnoreParty_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",16) # 16 = Party
def cbxOnlyCountParty_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",16)

def cbxIgnoreChampionParty_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",17) # 17 = ChampionParty
def cbxOnlyCountChampionParty_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",17)

def cbxIgnoreGiantParty_clicked(checked):
	Checkbox_Checked(checked,"lstIgnore",20) # 20 = GiantParty
def cbxOnlyCountGiantParty_clicked(checked):
	Checkbox_Checked(checked,"lstOnlyCount",20)

def cbxAcceptForgottenWorld_checked(checked):
	saveConfigs()

# Generalizing checkbox methods
def Checkbox_Checked(checked,gListName,mobType):
	gListReference = globals()[gListName]
	if checked:
		gListReference.append(mobType)
	else:
		gListReference.remove(mobType)
	saveConfigs()

# Return folder path
def getPath():
	return get_config_dir()+pName+"\\"

# Return character configs path (JSON)
def getConfig():
	return getPath()+character_data['server'] + "_" + character_data['name'] + ".json"

# Load default configs
def loadDefaultConfig():
	# Clear data
	global lstMobsData,lstIgnore,lstOnlyCount

	lstMobsData = []
	QtBind.clear(gui,lstMobs)

	lstIgnore = []
	QtBind.setChecked(gui,cbxIgnoreGeneral,False)
	QtBind.setChecked(gui,cbxIgnoreChampion,False)
	QtBind.setChecked(gui,cbxIgnoreGiant,False)
	QtBind.setChecked(gui,cbxIgnoreTitan,False)
	QtBind.setChecked(gui,cbxIgnoreStrong,False)
	QtBind.setChecked(gui,cbxIgnoreElite,False)
	QtBind.setChecked(gui,cbxIgnoreUnique,False)
	QtBind.setChecked(gui,cbxIgnoreParty,False)
	QtBind.setChecked(gui,cbxIgnoreChampionParty,False)
	QtBind.setChecked(gui,cbxIgnoreGiantParty,False)

	lstOnlyCount = []
	QtBind.setChecked(gui,cbxOnlyCountGeneral,False)
	QtBind.setChecked(gui,cbxOnlyCountChampion,False)
	QtBind.setChecked(gui,cbxOnlyCountGiant,False)
	QtBind.setChecked(gui,cbxOnlyCountTitan,False)
	QtBind.setChecked(gui,cbxOnlyCountStrong,False)
	QtBind.setChecked(gui,cbxOnlyCountElite,False)
	QtBind.setChecked(gui,cbxOnlyCountUnique,False)
	QtBind.setChecked(gui,cbxOnlyCountParty,False)
	QtBind.setChecked(gui,cbxOnlyCountChampionParty,False)
	QtBind.setChecked(gui,cbxOnlyCountGiantParty,False)

	QtBind.setChecked(gui,cbxAcceptForgottenWorld,False)

# Load config if exists
def loadConfigs():
	loadDefaultConfig()
	if isJoined() and os.path.exists(getConfig()):
		data = {}
		with open(getConfig(),"r") as f:
			data = json.load(f)
		# Check to load config
		if "Ignore Names" in data:
			global lstMobsData
			lstMobsData = data["Ignore Names"]
			# Load names visually
			for name in lstMobsData:
				QtBind.append(gui,lstMobs,name)
		
		if "Ignore Types" in data:
			global lstIgnore
			for t in data["Ignore Types"]:
				if t == 8:
					QtBind.setChecked(gui,cbxIgnoreUnique,True)
				elif t == 7:
					QtBind.setChecked(gui,cbxIgnoreElite,True)
				elif t == 6:
					QtBind.setChecked(gui,cbxIgnoreStrong,True)
				elif t == 5:
					QtBind.setChecked(gui,cbxIgnoreTitan,True)
				elif t == 4:
					QtBind.setChecked(gui,cbxIgnoreGiant,True)
				elif t == 1:
					QtBind.setChecked(gui,cbxIgnoreChampion,True)
				elif t == 0:
					QtBind.setChecked(gui,cbxIgnoreGeneral,True)
				elif t == 16:
					QtBind.setChecked(gui,cbxIgnoreParty,True)
				elif t == 17:
					QtBind.setChecked(gui,cbxIgnoreChampionParty,True)
				elif t == 20:
					QtBind.setChecked(gui,cbxIgnoreGiantParty,True)
				else:
					# skip it if is not filtered
					continue
				lstIgnore.append(t)

		if "OnlyCount Types" in data:
			global lstOnlyCount
			for t in data["OnlyCount Types"]:
				if t == 8:
					QtBind.setChecked(gui,cbxOnlyCountUnique,True)
				elif t == 7:
					QtBind.setChecked(gui,cbxOnlyCountElite,True)
				elif t == 6:
					QtBind.setChecked(gui,cbxOnlyCountStrong,True)
				elif t == 5:
					QtBind.setChecked(gui,cbxOnlyCountTitan,True)
				elif t == 4:
					QtBind.setChecked(gui,cbxOnlyCountGiant,True)
				elif t == 1:
					QtBind.setChecked(gui,cbxOnlyCountChampion,True)
				elif t == 0:
					QtBind.setChecked(gui,cbxOnlyCountGeneral,True)
				elif t == 16:
					QtBind.setChecked(gui,cbxOnlyCountParty,True)
				elif t == 17:
					QtBind.setChecked(gui,cbxOnlyCountChampionParty,True)
				elif t == 20:
					QtBind.setChecked(gui,cbxOnlyCountGiantParty,True)
				else:
					# skip it if is not filtered
					continue
				lstOnlyCount.append(t)

		if 'Accept ForgottenWorld' in data and data['Accept ForgottenWorld']:
			QtBind.setChecked(gui,cbxAcceptForgottenWorld,True)

# Save all config
def saveConfigs():
	# Save if data has been loaded
	if isJoined():
		# Save all data
		data = {}

		data['OnlyCount Types'] = lstOnlyCount
		data['Ignore Types'] = lstIgnore
		data['Ignore Names'] = lstMobsData
		data['Accept ForgottenWorld'] = QtBind.isChecked(gui,cbxAcceptForgottenWorld)

		# Overrides
		with open(getConfig(),"w") as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))

# Check if character is ingame
def isJoined():
	global character_data
	character_data = get_character_data()
	if not (character_data and "name" in character_data and character_data["name"]):
		character_data = None
	return character_data

# Add mob to the list
def btnAddMob_clicked():
	global lstMobsData
	# Check name
	text = QtBind.text(gui,tbxMobs)
	if text and not ListContains(text,lstMobsData):
		lstMobsData.append(text)
		# Add visually
		QtBind.append(gui,lstMobs,text)
		QtBind.setText(gui,tbxMobs,"")
		saveConfigs()
		log('Plugin: Monster added ['+text+']')

# Add mob to the list
def btnRemMob_clicked():
	global lstMobsData
	# Check selected
	selected = QtBind.text(gui,lstMobs)
	if selected:
		lstMobsData.remove(selected)
		# Remove visually
		QtBind.remove(gui,lstMobs,selected)
		saveConfigs()
		log('Plugin: Monster removed ['+selected+']')

# Return True if text exist at the list
def ListContains(text,lst):
	text = text.lower()
	for i in range(len(lst)):
		if lst[i].lower() == text:
			return True
	return False

# Return True if item exists
def QtBind_ItemsContains(text,lst):
	return ListContains(text,QtBind.getItems(gui,lst))

# Attacking mobs using all configs from bot
def AttackMobs(wait,isAttacking,position,radius,duration,elapsed_time,session_id):
	global attack_session_id
	if session_id != attack_session_id:
		return

	if isAttacking:
		elapsed_time += wait

	count = getMobCount(position,radius)

	# Determine termination
	terminate = False
	if duration is not None:
		if elapsed_time >= duration:
			log("Plugin: AttackArea duration of %.1f seconds has elapsed. Stopping attack." % duration)
			terminate = True
	else:
		if elapsed_time >= MAX_ATTACKING_TIME:
			log("Plugin: Attacking time exceeded ("+str(MAX_ATTACKING_TIME)+"s). Returning to town.")
			terminate = True
			use_return_scroll()
		elif count == 0:
			log("Plugin: All mobs killed!")
			terminate = True

	if not terminate:
		# Start to kill mobs using bot
		if not isAttacking:
			start_bot()
			log("Plugin: Starting to attack at this area. Radius: "+(str(radius) if radius != None else "Max.")+((" for %.1f seconds." % duration) if duration is not None else "."))
		# Check again after the delay
		Timer(wait,AttackMobs,[wait,True,position,radius,duration,elapsed_time,session_id]).start()
	else:
		# Invalidate session to prevent any late-firing timers
		attack_session_id += 1

		# Waits for pickable drops from pick filter database
		conn = GetFilterConnection()
		if conn:
			try:
				cursor = conn.cursor()
				WaitPickableDrops(cursor)
			except Exception as e:
				log("Plugin: Error checking pickable drops: "+str(e))
			finally:
				conn.close()

		# All mobs killed or time is up, stop botting
		stop_bot()
		# Setting training area far away. The bot should continue where he was at the script
		set_training_position(0,0,0,0)
		# Wait for bot to calm down and move back to the starting point
		log("Plugin: Getting back to the script...")
		Timer(2.5,move_to,[position['x'],position['y'],position['z']]).start()
		# give it some time to reach the movement
		Timer(5.0,start_bot).start()

# Count all mobs around your character (60 or more it's the max. range I think)
def getMobCount(position,radius):
	# Clear
	QtBind.clear(gui,lstMonsterCounter)
	QtBind.append(gui,lstMonsterCounter,'Name (Type)') # Header
	count = 0
	# Get my position to calc radius
	p = position if radius != None else None
	# Check all mob around
	monsters = get_monsters()
	if monsters:
		for key, mob in monsters.items():
			# Ignore if this mob type is found
			if mob['type'] in lstIgnore:
				continue
			# Only count setup
			if len(lstOnlyCount) > 0:
				# If is not in only count, skip it
				if not mob['type'] in lstOnlyCount:
					continue
			# Ignore mob names
			elif ListContains(mob['name'],lstMobsData):
				continue
			# Checking radius
			if radius != None:
				if round(GetDistance(p['x'], p['y'],mob['x'],mob['y']),2) > radius:
					continue
			# Adding GUI for a complete UX
			QtBind.append(gui,lstMonsterCounter,mob['name']+' ('+str(mob['type'])+')')
			count+=1
	return count

# Calc the distance from point A to B
def GetDistance(ax,ay,bx,by):
	return ((bx-ax)**2 + (by-ay)**2)**(0.5)

# Create a database connection to config filter
def GetFilterConnection():
	global character_data
	if not character_data:
		character_data = get_character_data()
	if not character_data or 'server' not in character_data or 'name' not in character_data:
		return None
	# Path to the filter database
	path = get_config_dir()+character_data['server']+'_'+character_data['name']+'.db3'
	if os.path.exists(path):
		# Connect to db3
		return sqlite3.connect(path)
	return None

def IsPickable(filterCursor,ItemID):
	if not filterCursor:
		return False
	# Check existence of pickable item by character
	return filterCursor.execute('SELECT EXISTS(SELECT 1 FROM pickfilter WHERE id=? AND pick=1 LIMIT 1)',(ItemID,)).fetchone()[0]

# Sleep the thread while waits for pickable drops
def WaitPickableDrops(filterCursor,waiting=0):
	if not filterCursor:
		return
	# Time is over for waiting drops
	if waiting >= WAIT_DROPS_DELAY_MAX:
		log("Plugin: Timeout for picking up drops!")
		return
	# check if there is a pickable drop
	drops = get_drops()
	if drops:
		# Check drops if someone is pickable
		drop = None
		for key in drops:
			value = drops[key]
			if IsPickable(filterCursor,value['model']):
				drop = value
				break
		if drop:
			log('Plugin: Waiting for picking up "'+drop['name']+'"...')
			# wait 1s
			sleep(1.0)
			# Check again
			WaitPickableDrops(filterCursor,waiting+1)

# Returns the item information if is found
def GetDimensionalHole(Name):
	searchByName = Name != ''
	# Search the dimensional hole through items
	items = get_inventory()['items']
	for slot, item in enumerate(items):
		if item:
			# Check if match the current item
			match = False
			if searchByName:
				match = (Name == item['name'])
			else:
				itemData = get_item(item['model'])
				match = (itemData['tid1'] == 3 and itemData['tid2'] == 12 and itemData['tid3'] == 7)

			if match:
				item['slot'] = slot
				return item
	return None

# Returns the dimensional talking object if is found near
def GetDimensionalPillarUID(Name):
	# Load all talking objects around
	npcs = get_npcs()
	if npcs:
		for uid, npc in npcs.items():
			# Try to check object model (Casually the dimensional match with the item model) 
			item = get_item(npc['model'])
			# Check if data is valid and matching (exact or partial)
			if item:
				if item['name'] == Name or (Name and (Name.lower() in item['name'].lower() or item['name'].lower() in Name.lower())):
					return uid
	return 0

# Select and enter to the dimensional hole specified
def EnterToDimensional(Name):
	# Check unique id from dimensional pillar around
	uid = GetDimensionalPillarUID(Name)
	if uid:
		# Select dimensional
		log('Plugin: Selecting dimensional hole...')
		packet = struct.pack('I',uid)
		inject_joymax(0x7045,packet,False)
		sleep(1.0)
		# Enter and select the option
		log('Plugin: Entering to dimensional hole...')
		inject_joymax(0x704B,packet,False)
		packet += struct.pack('H',3)
		inject_joymax(0x705A,packet,False)
		# Start bot, doesn't matter if is teleporting
		Timer(5.0,start_bot).start()
		return
	# Error message
	log('Plugin: "'+Name+'" cannot be found around you!')

# Avoid interpreter lock
def GoDimensionalThread(Name):
	# Check if dimensional still opened
	if dimensionalItemActivated:
		Name = dimensionalItemActivated['name']
		log('Plugin: '+( '"'+Name+'"' if Name else 'Dimensional Hole')+' still opened!')
		EnterToDimensional(Name)
		return
	# Check if the item exists on inventory
	item = GetDimensionalHole(Name)
	if item:
		# Inject item usage
		log('Plugin: Using "'+item['name']+'"...')
		p = struct.pack('B',item['slot'])
		locale = get_locale()
		if locale == 56 or locale == 18: # TRSRO & (PROBABLY) iSRO
			p += b'\x30\x0C\x0C\x07'
		else: #locale == 22: # vSRO
			p += b'\x6C\x3E'
		# Set item used
		global itemUsedByPlugin
		itemUsedByPlugin = item
		inject_joymax(0x704C,p,True)
	else:
		# Error message
		log('Plugin: '+( '"'+Name+'"' if Name else 'Dimensional Hole')+' cannot be found at your inventory')

# ______________________________ Events ______________________________ #

# Attack all mobs around using the bot config. Ex: "AttackArea" or "AttackArea,75" or "AttackArea,75,30"
# Will be using radius maximum (75 approx) as default
def AttackArea(args):
	# radius maximum as default
	radius = None
	if len(args) >= 2 and args[1]:
		try:
			radius = round(float(args[1]),2)
		except ValueError:
			log("Plugin error: AttackArea invalid radius value. Ignoring radius parameter.")

	# duration as optional parameter
	duration = None
	if len(args) >= 3 and args[2]:
		try:
			duration = round(float(args[2]),2)
			# Capping duration at 600 seconds as per design decision
			if duration > 600.0:
				log("Plugin: AttackArea duration of %.1f seconds exceeds cap. Capping at 600.0 seconds." % duration)
				duration = 600.0
			elif duration <= 0:
				log("Plugin error: AttackArea duration must be positive. Skipping command.")
				return 0
		except ValueError:
			log("Plugin error: AttackArea invalid duration value. Skipping command.")
			return 0

	# Check position
	p = get_position()
	if not p:
		return 0

	# Check if we should start attacking.
	# If duration is specified, we ALWAYS start attacking (waiting/killing for duration).
	# If duration is NOT specified, we only start if there are mobs (> 0).
	mobs_count = getMobCount(p,radius)
	if duration is not None or mobs_count > 0:
		# stop scripting
		stop_bot()
		# set automatically the training area
		set_training_position(p['region'], p['x'], p['y'],p['z'])
		# set automatically the radius to avoid setting conflict
		if radius != None:
			set_training_radius(radius)
		else:
			set_training_radius(100.0)

		# Start a new session to avoid overlapping timers
		global attack_session_id
		attack_session_id += 1
		current_session = attack_session_id

		# start to kill mobs on other thread because interpreter lock
		Timer(0.001,AttackMobs,[COUNT_MOBS_DELAY,False,p,radius,duration,0.0,current_session]).start()
	# otherwise continue normally
	else:
		log("Plugin: No mobs at this area. Radius: "+(str(radius) if radius != None else "Max."))
	return 0

# Use, select and enter to the dimensional forgotten world. 
# Ex: "GoDimensional" or "GoDimensional,Dimension Hole (Flame Mountain-3 stars)"
def GoDimensional(args):
	# Stop bot while doing the whole process
	stop_bot()
	# Check if the name has been set
	name = ''
	if len(args) > 1:
		name = args[1]
	# Avoid lock
	Timer(0.001,GoDimensionalThread,[name]).start()
	return 0

# Called after teleporting
def teleported():
	global attack_session_id
	attack_session_id += 1

# Called when the character enters the game world
def joined_game():
	global attack_session_id
	attack_session_id += 1
	loadConfigs()

# All packets received from game server will be passed to this function
# Returning True will keep the packet and False will not forward it to the game client
def handle_joymax(opcode, data):
	# SERVER_DIMENSIONAL_INVITATION_REQUEST
	if opcode == 0x751A:
		if QtBind.isChecked(gui,cbxAcceptForgottenWorld):
			# Create packet response
			packet = data[:4] # Request ID
			packet += b'\x00\x00\x00\x00' # unknown ID
			packet += b'\x01' # Accept flag
			inject_joymax(0x751C,packet,False)
			log('Plugin: Forgotten World invitation accepted!')
	# SERVER_INVENTORY_ITEM_USE
	elif opcode == 0xB04C:
		# Just check recent item used to keep it simple
		global itemUsedByPlugin
		if itemUsedByPlugin:
			# Success
			if data[0] == 1:
				log('Plugin: "'+itemUsedByPlugin['name']+'" has been opened')
				# Set timer for cooldown usage
				global dimensionalItemActivated
				dimensionalItemActivated = itemUsedByPlugin
				def DimensionalCooldown():
					global dimensionalItemActivated
					dimensionalItemActivated = None
				Timer(DIMENSIONAL_COOLDOWN_DELAY,DimensionalCooldown).start()
				# Avoid locking the proxy thread
				Timer(5.0,EnterToDimensional,[itemUsedByPlugin['name']]).start()
			else:
				log('Plugin: "'+itemUsedByPlugin['name']+'" cannot be opened')
			# Stop checking item used
			itemUsedByPlugin = None
	return True

# Plugin loaded
log('Plugin: '+pName+' v'+pVersion+' succesfully loaded')

if os.path.exists(getPath()):
	# Adding RELOAD plugin support
	try:
		loadConfigs()
	except:
		# Just in case omg -_-
		log('Plugin: Error loading '+pName+' config file')
else:
	# Creating configs folder
	os.makedirs(getPath())
	log('Plugin: '+pName+' folder has been created')