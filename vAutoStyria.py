from phBot import *
import QtBind
from threading import Timer
import struct

pVersion = '2.0.0'
pName = 'vAutoStyria'

REQUIRED_PROFILE = 'Styria'

# State variables for smart movement
moving_to_dense_spot = False
target_x = 0.0
target_y = 0.0
target_z = 0.0
move_timeout = 0
check_timer = 0
skip_first_scan = True

# Graphic user interface
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'vAutoStyria detects teleportation. If character is found outside Styria Room,\n'
                                 'it waits few seconds then teleports out to Hotan.\n\n'
                                 'Smart Movement: Every 30 seconds, it scans the training area and moves the\n'
                                 'character to the densest mob area if it has more mobs than the current spot.\n\n'
                                 'By: H Y P E R V I S O R', 10, 10)

cbxSmartMovement = QtBind.createCheckBox(gui, 'cbx_smart_movement_clicked', 'Enable Smart Movement', 10, 110)
QtBind.setChecked(gui, cbxSmartMovement, True)

def cbx_smart_movement_clicked(checked):
	pass

# Calculate the distance from point A to B
def GetDistance(ax, ay, bx, by):
	return ((bx - ax) ** 2 + (by - ay) ** 2) ** (0.5)

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
	if get_profile() != REQUIRED_PROFILE:
		return
	p = get_position()
	if p:
		dist = GetDistance(p['x'], p['y'], -20161, -177)
		if dist <= 10.0:
			log("Plugin: Teleported outside Styria Room (confidence: with distance %.1f.) Stopping bot and teleporting out..." % dist)
			Timer(2.0, stop_bot).start()
			# Schedule the first packet with 2.0 seconds delay
			Timer(3.0, inject_first_packet).start()

# Called every 500ms
def event_loop():
	global moving_to_dense_spot, target_x, target_y, target_z, move_timeout
	global check_timer, skip_first_scan

	if get_profile() != REQUIRED_PROFILE:
		return

	# If Smart Movement GUI checkbox is not checked, disable logic and abort active movements
	if not QtBind.isChecked(gui, cbxSmartMovement):
		moving_to_dense_spot = False
		check_timer = 0
		skip_first_scan = True
		return

	# If we are currently moving to a dense spot
	if moving_to_dense_spot:
		char_pos = get_position()
		if char_pos:
			dist = GetDistance(char_pos['x'], char_pos['y'], target_x, target_y)
			move_timeout += 500
			# If reached target (dist <= 3.0) or timed out (6 seconds)
			if dist <= 3.0 or move_timeout >= 6000:
				log("Plugin: Reached target dense spot or timed out.")
				moving_to_dense_spot = False
			else:
				# Keep calling move_to to override botting engine actions
				move_to(target_x, target_y, target_z)
		return

	# We must be botting to check density and move
	if get_status() != 'botting':
		check_timer = 0
		skip_first_scan = True
		return

	# Get training area info
	area = get_training_area()
	if not area or (area['x'] == 0 and area['y'] == 0) or area['radius'] <= 0:
		check_timer = 0
		return

	# Get character position
	char_pos = get_position()
	if not char_pos:
		check_timer = 0
		return

	# Only check if character is inside the training area bounds
	dist_to_center = GetDistance(char_pos['x'], char_pos['y'], area['x'], area['y'])
	if dist_to_center > area['radius']:
		check_timer = 0
		return

	# Check every 30 seconds (30,000 ms)
	check_timer += 500
	if check_timer < 30000:
		return
	check_timer = 0

	# Skip the very first scan when botting starts inside the training area
	if skip_first_scan:
		skip_first_scan = False
		log("Plugin: Skipping the first density scan to allow character to fight at the initial landing spot.")
		return

	log("Plugin: Starting Smart Movement density check...")

	# Get monsters nearby
	monsters = get_monsters()
	if not monsters:
		return

	# Filter monsters inside training area bounds
	valid_monsters = []
	for key, mob in monsters.items():
		mob_dist_to_center = GetDistance(mob['x'], mob['y'], area['x'], area['y'])
		if mob_dist_to_center <= area['radius']:
			valid_monsters.append(mob)

	if not valid_monsters:
		return

	log("Plugin: Found %d monsters inside the training area." % len(valid_monsters))

	# 1. Count mobs near character's current position
	DENSITY_RADIUS = 15.0 # Radius to define density / proximity
	current_mobs_count = 0
	for mob in valid_monsters:
		if GetDistance(char_pos['x'], char_pos['y'], mob['x'], mob['y']) <= DENSITY_RADIUS:
			current_mobs_count += 1

	log("Plugin: Current position has %d mobs nearby." % current_mobs_count)

	# 2. Find the spot with the highest density of mobs
	best_mob = None
	max_density = 0

	for mob in valid_monsters:
		density = 0
		for other_mob in valid_monsters:
			if GetDistance(mob['x'], mob['y'], other_mob['x'], other_mob['y']) <= DENSITY_RADIUS:
				density += 1
		
		if density > max_density:
			max_density = density
			best_mob = mob
		elif density == max_density and best_mob:
			# Tie-breaker: choose the mob closer to the character
			dist_to_curr = GetDistance(char_pos['x'], char_pos['y'], mob['x'], mob['y'])
			dist_to_best = GetDistance(char_pos['x'], char_pos['y'], best_mob['x'], best_mob['y'])
			if dist_to_curr < dist_to_best:
				best_mob = mob

	if best_mob:
		log("Plugin: Densest spot found has %d mobs at (%.1f, %.1f)." % (max_density, best_mob['x'], best_mob['y']))

	# 3. Trigger move to dense spot if it has higher density and is at a reasonable distance (> 5.0 units)
	if best_mob and max_density > current_mobs_count:
		dist_to_mob = GetDistance(char_pos['x'], char_pos['y'], best_mob['x'], best_mob['y'])
		if dist_to_mob > 5.0:
			log("Plugin: Moving to dense cluster (current: %d mobs vs cluster: %d mobs at %.1f units away)." % (current_mobs_count, max_density, dist_to_mob))
			target_x = best_mob['x']
			target_y = best_mob['y']
			target_z = best_mob.get('z', char_pos['z'])
			moving_to_dense_spot = True
			move_timeout = 0
			# Call move immediately
			move_to(target_x, target_y, target_z)
		else:
			log("Plugin: Densest cluster is too close (%.1f units). Skipping movement." % dist_to_mob)
	else:
		log("Plugin: Current spot is already the densest or equal (current: %d mobs, max cluster: %d mobs). Skipping movement." % (current_mobs_count, max_density))

# Plugin loaded
log('Plugin: ' + pName + ' v' + pVersion + ' successfully loaded')
