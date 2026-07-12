from phBot import *
import QtBind
from threading import Timer
import struct
import os
import sqlite3
import json
from time import sleep

pVersion = '3.0.0'
pName = 'vAutoStyria'

REQUIRED_PROFILE = 'Styria'
DEFAULT_COIN_LIMIT = 250

# Looping state
teleporting_to_hotan = False

# AttackAreaFor state and constants
attack_for_session_id = 0
COUNT_MOBS_DELAY = 1.0
WAIT_DROPS_DELAY_MAX = 90

# Checkbox handlers
def cbxEnableLoop_checked(checked):
	log("Plugin: Hotan looping has been " + ("enabled" if checked else "disabled"))

def cbxIncreaseSleep_checked(checked):
	log("Plugin: Arena Coins low sleeping increase has been " + ("enabled" if checked else "disabled"))

# Graphic user interface
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'vAutoStyria detects teleportation. If character is found outside Styria Room,\n'
                                 'it waits few seconds then teleports out to Hotan.\n\n'
                                 'By: H Y P E R V I S O R', 10, 10)

cbxEnableLoop = QtBind.createCheckBox(gui, 'cbxEnableLoop_checked', 'Enable Hotan Looping', 10, 75)
QtBind.setChecked(gui, cbxEnableLoop, True)

lblMinSleep = QtBind.createLabel(gui, 'Min sleep time (minutes):', 10, 100)
tbxMinSleep = QtBind.createLineEdit(gui, '5.0', 160, 97, 40, 20)

cbxIncreaseSleep = QtBind.createCheckBox(gui, 'cbxIncreaseSleep_checked', 'Increase sleep if Arena Coins are low', 10, 125)
QtBind.setChecked(gui, cbxIncreaseSleep, False)

lblIncreaseMin = QtBind.createLabel(gui, 'Increase sleep to (min):', 25, 150)
tbxIncreaseSleepMin = QtBind.createLineEdit(gui, '10.0', 160, 147, 40, 20)

lblCoinLimit = QtBind.createLabel(gui, 'when Arena Coins <:', 215, 150)
tbxArenaCoinLimit = QtBind.createLineEdit(gui, str(DEFAULT_COIN_LIMIT), 335, 147, 40, 20)

# Calculate the distance from point A to B
def GetDistance(ax, ay, bx, by):
	return ((bx - ax) ** 2 + (by - ay) ** 2) ** (0.5)

# Retrieve character db file path
def get_character_db_path():
	char_data = get_character_data()
	if char_data and "server" in char_data and "name" in char_data:
		return get_config_dir() + char_data['server'] + '_' + char_data['name'] + '.db3'
	return None

# Create a database connection to config filter
def GetFilterConnection():
	db_path = get_character_db_path()
	if db_path and os.path.exists(db_path):
		return sqlite3.connect(db_path)
	return None

# Check existence of pickable item by character
def IsPickable(filterCursor, ItemID):
	try:
		return filterCursor.execute('SELECT EXISTS(SELECT 1 FROM pickfilter WHERE id=? AND pick=1 LIMIT 1)', (ItemID,)).fetchone()[0]
	except Exception:
		return False

# Sleep the thread while waiting for pickable drops
def WaitPickableDrops(filterCursor, waiting=0):
	if not filterCursor:
		return
	if waiting >= WAIT_DROPS_DELAY_MAX:
		log("Plugin: Timeout for picking up drops!")
		return
	drops = get_drops()
	if drops:
		drop = None
		for key, value in drops.items():
			if IsPickable(filterCursor, value['model']):
				drop = value
				break
		if drop:
			log('Plugin: Waiting for picking up "' + drop['name'] + '"...')
			sleep(1.0)
			WaitPickableDrops(filterCursor, waiting + 1)

# Count all mobs around the character within the specified radius
def getMobCount(position, radius):
	count = 0
	p = position if radius is not None else None
	monsters = get_monsters()
	if monsters:
		for key, mob in monsters.items():
			if radius is not None:
				if round(GetDistance(p['x'], p['y'], mob['x'], mob['y']), 2) > radius:
					continue
			count += 1
	return count

# Custom script command: AttackAreaFor, radius, time
def AttackAreaFor(args):
	if len(args) < 3:
		log("Plugin error: AttackAreaFor requires 2 arguments (radius, time). Command skipped.")
		return 0
	
	try:
		radius = round(float(args[1]), 2)
		duration = round(float(args[2]), 2)
	except ValueError:
		log("Plugin error: AttackAreaFor arguments must be numbers. Command skipped.")
		return 0
		
	if radius <= 0 or duration <= 0:
		log("Plugin error: AttackAreaFor arguments must be positive numbers. Command skipped.")
		return 0
		
	# Cap duration at 10 minutes (600 seconds)
	if duration > 600.0:
		log("Plugin: AttackAreaFor duration of %.1f seconds exceeds limit. Capping at 600.0 seconds." % duration)
		duration = 600.0
		
	p = get_position()
	if not p:
		log("Plugin error: Could not retrieve current position. Command skipped.")
		return 0
		
	# Check initial mob count
	mobs_count = getMobCount(p, radius)
	if mobs_count == 0:
		log("Plugin: No monsters found at this area (radius: %.1f). Skipping command." % radius)
		return 0
		
	log("Plugin: Starting AttackAreaFor (radius: %.1f, duration: %.1f seconds)." % (radius, duration))
	
	# Stop script execution
	stop_bot()
	
	# Set training area
	set_training_position(p['region'], p['x'], p['y'], p['z'])
	set_training_radius(radius)
	
	global attack_for_session_id
	attack_for_session_id += 1
	current_session = attack_for_session_id
	
	# Start the loop timer immediately on a background thread to allow stop_bot state transition to settle
	Timer(0.5, AttackAreaFor_Loop, [0.0, duration, p, radius, current_session, True]).start()
	return 0

def AttackAreaFor_Loop(elapsed_time, total_time, position, radius, session_id, first_run=False):
	global attack_for_session_id
	if session_id != attack_for_session_id:
		return
		
	if first_run:
		# Execute start_bot in background thread
		start_bot()
		Timer(1.0, AttackAreaFor_Loop, [1.0, total_time, position, radius, session_id, False]).start()
		return
		
	# Check if duration reached
	if elapsed_time >= total_time:
		log("Plugin: AttackAreaFor duration of %.1f seconds has elapsed. Stopping attack." % total_time)
		finish_attack_area_for(position, session_id)
		return
		
	# Check current mob count for early termination
	mobs_count = getMobCount(position, radius)
	if mobs_count == 0:
		log("Plugin: All monsters killed. Stopping AttackAreaFor early.")
		finish_attack_area_for(position, session_id)
		return
		
	# Continue loop
	Timer(1.0, AttackAreaFor_Loop, [elapsed_time + 1.0, total_time, position, radius, session_id, False]).start()

def finish_attack_area_for(position, session_id):
	global attack_for_session_id
	if session_id != attack_for_session_id:
		return
		
	# Invalidate the session
	attack_for_session_id += 1
	
	# Stop botting
	stop_bot()
	
	# Wait for pickable drops
	db_path = get_character_db_path()
	if db_path and os.path.exists(db_path):
		try:
			conn = sqlite3.connect(db_path)
			cursor = conn.cursor()
			WaitPickableDrops(cursor)
			conn.close()
		except Exception as e:
			log("Plugin: Error checking pickable drops: %s" % str(e))
			
	# Reset training position
	set_training_position(0, 0, 0, 0)
	
	# Move back to starting position
	log("Plugin: Returning back to script starting position...")
	Timer(2.5, move_to, [position['x'], position['y'], position['z']]).start()
	
	# Resume script
	Timer(5.0, start_bot).start()

# Helper to count total Arena Coins in inventory and pets
def count_arena_coins():
	total_coins = 0
	# Inventory check
	inventory = get_inventory()
	if inventory and 'items' in inventory:
		for item in inventory['items']:
			if item and item.get('name') == 'Arena Coin':
				total_coins += item.get('quantity', 0)
	# Pets check
	pets = get_pets()
	if pets:
		for pet_id, pet_data in pets.items():
			if pet_data and 'items' in pet_data:
				for item in pet_data['items']:
					if item and item.get('name') == 'Arena Coin':
						total_coins += item.get('quantity', 0)
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
	global teleporting_to_hotan, attack_for_session_id
	attack_for_session_id += 1
	if get_profile() != REQUIRED_PROFILE:
		return
	p = get_position()
	if p:
		dist = GetDistance(p['x'], p['y'], -20161, -177)
		if dist <= 10.0:
			log("Plugin: Teleported outside Styria Room (confidence: with distance %.1f.) Stopping bot and teleporting out..." % dist)
			if QtBind.isChecked(gui, cbxEnableLoop):
				teleporting_to_hotan = True
			Timer(2.0, stop_bot).start()
			# Schedule the first packet with 3.0 seconds delay
			Timer(3.0, inject_first_packet).start()
		elif teleporting_to_hotan:
			teleporting_to_hotan = False
			if QtBind.isChecked(gui, cbxEnableLoop):
				char_data = get_character_data()
				zone_name = char_data.get("zone_name", "") if char_data else ""
				log("Plugin: Teleported to %s (flag teleporting_to_hotan is active)" % zone_name)
				if "Hotan" in zone_name:
					sleep_minutes = get_sleep_minutes()
					sleep_seconds = sleep_minutes * 60.0
					log("Plugin: Arrived in Hotan. Sleeping %.1f minutes before starting the bot again..." % sleep_minutes)
					Timer(sleep_seconds, start_bot).start()

# Called every 500ms
def event_loop():
	pass

# Plugin loaded
log('Plugin: ' + pName + ' v' + pVersion + ' successfully loaded')
