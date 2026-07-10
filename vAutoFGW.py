from phBot import *
import QtBind
from threading import Timer
from time import sleep
import struct

pVersion = '1.0.0'
pName = 'vAutoFGW'

DIMENSIONAL_COOLDOWN_DELAY = 18000 # seconds (5 hours)
REQUIRED_PROFILE = 'FGW'

# Globals
itemUsedByPlugin = None
dimensionalItemActivated = None

# Graphic user interface
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'vAutoFGW automatically uses and enters Dimensional Holes for the Forgotten World (FGW).\n\n'
                             'It also triggers the bot to auto-start 5.0 seconds after teleporting into the FGW spawn coordinates,\n\n'
                             'provided the current active bot profile matches the configured profile (default: "FGW").\n\n\n'
                             'By: H Y P E R V I S O R', 10, 10)

# Calc the distance from point A to B
def GetDistance(ax, ay, bx, by):
	return ((bx - ax) ** 2 + (by - ay) ** 2) ** (0.5)

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
		packet = struct.pack('I', uid)
		inject_joymax(0x7045, packet, False)
		sleep(1.0)
		# Enter and select the option
		log('Plugin: Entering to dimensional hole...')
		inject_joymax(0x704B, packet, False)
		packet += struct.pack('H', 3)
		inject_joymax(0x705A, packet, False)
		# Start bot, doesn't matter if is teleporting
		Timer(5.0, start_bot).start()
		return
	# Error message
	log('Plugin: "' + Name + '" cannot be found around you!')

# Avoid interpreter lock
def GoFGWThread(Name):
	# Check if dimensional still opened
	if dimensionalItemActivated:
		Name = dimensionalItemActivated['name']
		log('Plugin: ' + ('"' + Name + '"' if Name else 'Dimensional Hole') + ' still opened!')
		EnterToDimensional(Name)
		return
	# Check if the item exists on inventory
	item = GetDimensionalHole(Name)
	if item:
		# Inject item usage
		log('Plugin: Using "' + item['name'] + '"...')
		p = struct.pack('B', item['slot'])
		locale = get_locale()

		if locale in [56, 18, 61]: # TRSRO, iSRO, and VTC
			p += b'\x30\x0C\x0C\x07'
		else: #locale == 22: # vSRO
			p += b'\x6C\x3E'
		# Set item used
		global itemUsedByPlugin
		itemUsedByPlugin = item
		inject_joymax(0x704C, p, True)
	else:
		# Error message
		log('Plugin: ' + ('"' + Name + '"' if Name else 'Dimensional Hole') + ' cannot be found at your inventory')

# Use, select and enter to the dimensional forgotten world. 
# Ex: "GoFGW" or "GoFGW,Dimension Hole (Flame Mountain-3 stars)"
def GoFGW(args):
	if get_profile() != REQUIRED_PROFILE:
		return 0
	# Stop bot while doing the whole process
	stop_bot()
	# Check if the name has been set
	name = ''
	if len(args) > 1:
		name = args[1]
	# Avoid lock
	Timer(0.001, GoFGWThread, [name]).start()
	return 0

# All packets received from game server will be passed to this function
# Returning True will keep the packet and False will not forward it to the game client
def handle_joymax(opcode, data):
	if get_profile() != REQUIRED_PROFILE:
		return True
	# SERVER_INVENTORY_ITEM_USE
	if opcode == 0xB04C:
		# Just check recent item used to keep it simple
		global itemUsedByPlugin
		if itemUsedByPlugin:
			# Success
			if data[0] == 1:
				log('Plugin: "' + itemUsedByPlugin['name'] + '" has been opened')
				# Set timer for cooldown usage
				global dimensionalItemActivated
				dimensionalItemActivated = itemUsedByPlugin
				def DimensionalCooldown():
					global dimensionalItemActivated
					dimensionalItemActivated = None
				Timer(DIMENSIONAL_COOLDOWN_DELAY, DimensionalCooldown).start()
				# Avoid locking the proxy thread
				Timer(5.0, EnterToDimensional, [itemUsedByPlugin['name']]).start()
			else:
				log('Plugin: "' + itemUsedByPlugin['name'] + '" cannot be opened')
			# Stop checking item used
			itemUsedByPlugin = None
	return True

# Called after teleporting
def teleported():
	if get_profile() != REQUIRED_PROFILE:
		return
	p = get_position()
	if p:
		dist = GetDistance(p['x'], p['y'], 17992, 3827)
		if dist < 50.0:
			log("Plugin: Teleported inside FGW spawn area (Distance: %.1f). Starting bot in 5.0 seconds..." % dist)
			Timer(5.0, start_bot).start()

# Plugin loaded
log('Plugin: ' + pName + ' v' + pVersion + ' succesfully loaded')
