from phBot import *
import QtBind
from threading import Timer
import struct

pVersion = '3.1.0'
pName = 'vAutoStyria'

REQUIRED_PROFILE = 'Styria'
DEFAULT_COIN_LIMIT = 250

# Looping state
teleporting_to_hotan = False
current_loop = 1


# Checkbox handlers
def cbxIncreaseSleep_checked(checked):
	log("Plugin: Arena Coins low sleeping increase has been " + ("enabled" if checked else "disabled"))

def btnGetPosition_clicked():
	p = get_position()
	log("Plugin: Debug get_position() -> %s" % str(p))

# Graphic user interface
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'vAutoStyria detects teleportation. If character is found outside Styria Room,\n'
                                 'it waits few seconds then teleports out to Hotan.\n\n'
                                 'By: H Y P E R V I S O R', 10, 10)

lblLoopCount = QtBind.createLabel(gui, 'Hotan Loop Count (1 = No loop):', 10, 75)
tbxLoopCount = QtBind.createLineEdit(gui, '1', 190, 72, 40, 20)

lblMinSleep = QtBind.createLabel(gui, 'Min sleep time (minutes):', 10, 100)
tbxMinSleep = QtBind.createLineEdit(gui, '5.0', 160, 97, 40, 20)

cbxIncreaseSleep = QtBind.createCheckBox(gui, 'cbxIncreaseSleep_checked', 'Increase sleep if Arena Coins are low', 10, 125)
QtBind.setChecked(gui, cbxIncreaseSleep, False)

lblIncreaseMin = QtBind.createLabel(gui, 'Increase sleep to (min):', 25, 150)
tbxIncreaseSleepMin = QtBind.createLineEdit(gui, '10.0', 160, 147, 40, 20)

lblCoinLimit = QtBind.createLabel(gui, 'when Arena Coins <:', 215, 150)
tbxArenaCoinLimit = QtBind.createLineEdit(gui, str(DEFAULT_COIN_LIMIT), 335, 147, 40, 20)

btnGetPosition = QtBind.createButton(gui, 'btnGetPosition_clicked', '  Get Position  ', 10, 180)

# Helper to retrieve configured maximum loop count
def get_loop_count():
	try:
		val = int(QtBind.text(gui, tbxLoopCount))
		if val >= 1:
			return val
	except Exception:
		pass
	return 1

# Calculate the distance from point A to B
def GetDistance(ax, ay, bx, by):
	return ((bx - ax) ** 2 + (by - ay) ** 2) ** (0.5)

# Helper to count total Arena Coins in inventory and pets
def count_arena_coins():
	total_coins = 0
	inv_coins = 0
	# Inventory check
	inventory = get_inventory()
	if inventory and 'items' in inventory:
		for item in inventory['items']:
			if item and item.get('name') == 'Arena Coin':
				inv_coins += item.get('quantity', 0)
	log("Plugin: count_arena_coins - Arena Coins in inventory: %d" % inv_coins)
	total_coins += inv_coins

	# Pets check
	pets = get_pets()
	if pets:
		log("Plugin: count_arena_coins - Found %d pet(s) to check" % len(pets))
		for pet_id, pet_data in pets.items():
			if pet_data:
				pet_name = pet_data.get('name', 'Unknown')
				pet_type = pet_data.get('type', 'Unknown')
				pet_coins = 0
				if 'items' in pet_data and pet_data['items']:
					for item in pet_data['items']:
						if item and item.get('name') == 'Arena Coin':
							pet_coins += item.get('quantity', 0)
					log("Plugin: count_arena_coins - Pet ID: %s (%s, type: %s) has %d Arena Coins" % (str(pet_id), pet_name, pet_type, pet_coins))
				else:
					log("Plugin: count_arena_coins - Pet ID: %s (%s, type: %s) has no items list" % (str(pet_id), pet_name, pet_type))
				total_coins += pet_coins
			else:
				log("Plugin: count_arena_coins - Pet ID: %s has null data" % str(pet_id))
	else:
		log("Plugin: count_arena_coins - No pets found (get_pets returned None or empty)")
	
	log("Plugin: count_arena_coins - Total Arena Coins counted: %d" % total_coins)
	return total_coins

# Helper to retrieve configured min sleep time
def get_min_sleep_minutes():
	try:
		val = float(QtBind.text(gui, tbxMinSleep))
		if val >= 0:
			return val
	except Exception:
		pass
	return 5.0

# Helper to retrieve final sleep time based on configuration and Arena Coin count
def get_sleep_minutes():
	min_sleep = get_min_sleep_minutes()
	
	if QtBind.isChecked(gui, cbxIncreaseSleep):
		try:
			coin_limit = int(QtBind.text(gui, tbxArenaCoinLimit))
		except Exception:
			coin_limit = DEFAULT_COIN_LIMIT
			
		try:
			increased_sleep = float(QtBind.text(gui, tbxIncreaseSleepMin))
		except Exception:
			increased_sleep = 10.0
			
		coins_count = count_arena_coins()
		log("Plugin: Checking Arena Coins: count is %d (limit is %d)" % (coins_count, coin_limit))
		if coins_count < coin_limit:
			log("Plugin: Arena Coins count (%d) is less than limit (%d). Increasing sleep time to %.1f minutes." % (coins_count, coin_limit, increased_sleep))
			return increased_sleep
			
	return min_sleep

# Injects the second packet to the server
def inject_second_packet():
	# Opcode: 0x705A, Data: 14 00 00 00 02 05 00 00 00
	opcode = 0x705A
	data = struct.pack('I', 20) + struct.pack('B', 2) + struct.pack('I', 5)
	inject_joymax(opcode, data, False)

# Injects the first packet to the server and schedules the second packet
def inject_first_packet():
	# Opcode: 0x7C45, Data: 14 00 00 00
	opcode = 0x7C45
	data = struct.pack('I', 20)
	inject_joymax(opcode, data, False)
	
	# Schedule the second packet with 1.0 second delay
	Timer(1.0, inject_second_packet).start()

# Called after teleporting
def teleported():
	global teleporting_to_hotan, current_loop
	if get_profile() != REQUIRED_PROFILE:
		return
	p = get_position()
	log("Plugin: Teleported: " + str(p))
	if p:
		dist = GetDistance(p['x'], p['y'], -20161, -177)
		if dist <= 10.0:
			max_loops = get_loop_count()
			if max_loops > 1 and current_loop < max_loops:
				teleporting_to_hotan = True
				log("Plugin: Teleported outside Styria Room (distance: %.1f). Completed run %d of %d. Stopping bot and teleporting out..." % (dist, current_loop, max_loops))
			else:
				teleporting_to_hotan = False
				log("Plugin: Teleported outside Styria Room (distance: %.1f). Completed run %d of %d. Stopping bot and teleporting out..." % (dist, current_loop, max_loops))
				current_loop = 1
			Timer(2.0, stop_bot).start()
			# Schedule the first packet with 3.0 seconds delay
			Timer(3.0, inject_first_packet).start()
		elif teleporting_to_hotan:
			teleporting_to_hotan = False
			max_loops = get_loop_count()
			if max_loops > 1 and current_loop < max_loops:
				current_loop += 1
				char_data = get_character_data()
				zone_name = char_data.get("zone_name", "") if char_data else ""
				log("Plugin: Teleported to %s (flag teleporting_to_hotan is active)" % zone_name)
				if "Hotan" in zone_name:
					sleep_minutes = get_sleep_minutes()
					sleep_seconds = sleep_minutes * 60.0
					log("Plugin: Arrived in Hotan. Preparing run %d of %d. Sleeping %.1f minutes before starting the bot again..." % (current_loop, max_loops, sleep_minutes))
					Timer(sleep_seconds, start_bot).start()
			else:
				current_loop = 1

# Called every 500ms
def event_loop():
	pass

# Plugin loaded
log('Plugin: ' + pName + ' v' + pVersion + ' successfully loaded')
