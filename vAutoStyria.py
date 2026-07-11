from phBot import *
import QtBind
from threading import Timer
import struct

pVersion = '1.3.0'
pName = 'vAutoStyria'

REQUIRED_PROFILE = 'Styria'

# State variables for smart movement
check_timer = 0
cooldown_timer = 0
skip_first_scan = True
original_training_area = None
shifting_training_area = False

# Graphic user interface
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'vAutoStyria detects teleportation. If character is found outside Styria Room,\n'
                                 'it waits few seconds then teleports out to Hotan.\n\n'
                                 'Smart Movement: Every 1 minute, it scans the training area and switches to\n'
                                 'temp training area "temp" to move character to the densest mob cluster.\n\n'
                                 'By: H Y P E R V I S O R', 10, 10)

# Calculate the distance from point A to B
def GetDistance(ax, ay, bx, by):
	return ((bx - ax) ** 2 + (by - ay) ** 2) ** (0.5)

# Switches the training area back to "Styria"
def restore_original_training_area():
	global original_training_area
	if original_training_area:
		log("Plugin: Restoring active training area to 'Styria'...")
		if not set_training_area("Styria"):
			log("Plugin: Error - Original training area 'Styria' not found in phBot list!")
		original_training_area = None

# Restores shifting state and starts botting
def do_start_bot():
	global shifting_training_area
	start_bot()
	shifting_training_area = False

# Injects the second packet to the server
def inject_second_packet():
	log("Plugin: Injecting second packet (0x705A)")
	# Opcode: 0x705A, Data: 14 00 00 00 02 05 00 00 00
	opcode = 0x705A
	data = struct.pack('I', 20) + struct.pack('B', 2) + struct.pack('I', 5)
	inject_joymax(opcode, data, False)

# Injects the first packet to the server and schedules the second packet
def inject_first_packet():
	log("Plugin: Injecting first packet (0x7C45)")
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
			log("Plugin: Teleported outside Styria Room (confidence: with distance %.1f.) Restoring training area to 'Styria' and teleporting out..." % dist)
			restore_original_training_area()
			Timer(2.0, stop_bot).start()
			# Schedule the first packet with 2.0 seconds delay
			Timer(3.0, inject_first_packet).start()

# Called when the plugin is unloaded
def finished():
	restore_original_training_area()

# Called every 500ms
def event_loop():
	global check_timer, cooldown_timer, skip_first_scan, original_training_area, shifting_training_area

	if get_profile() != REQUIRED_PROFILE:
		return

	# We must be botting to check density and move (reset timer if not botting to delay by 1 min on start)
	if get_status() != 'botting':
		if not shifting_training_area:
			restore_original_training_area()
			skip_first_scan = True
		check_timer = 0
		return

	# Check every 1 minute (60,000 ms)
	check_timer += 500
	if check_timer < 60000:
		return
	check_timer = 0

	# Skip the very first scan when botting starts
	if skip_first_scan:
		skip_first_scan = False
		log("Plugin: Skipping the first density scan to allow character to fight at the initial landing spot.")
		return

	log("Plugin: Starting Smart Movement density check...")

	# Get training area info
	area = get_training_area()
	if not area or (area['x'] == 0 and area['y'] == 0) or area['radius'] <= 0:
		log("Plugin: No training area or radius configured. Skipping scan.")
		return

	# Store original training area center if not already stored
	# We expect the bot to start in "Styria" training area, so this saves "Styria" coordinates
	if original_training_area is None:
		original_training_area = area
		log("Plugin: Saved original training center 'Styria' at (%.1f, %.1f) with radius %.1f." % (original_training_area['x'], original_training_area['y'], original_training_area['radius']))

	# Get character position
	char_pos = get_position()
	if not char_pos:
		return

	# Only check if character is inside the ORIGINAL training area ("Styria") bounds
	dist_to_center = GetDistance(char_pos['x'], char_pos['y'], original_training_area['x'], original_training_area['y'])
	if dist_to_center > original_training_area['radius']:
		log("Plugin: Character is outside original training area (distance: %.1f, radius: %.1f). Skipping scan." % (dist_to_center, original_training_area['radius']))
		return

	# Get monsters nearby
	monsters = get_monsters()
	if not monsters:
		log("Plugin: No monsters found nearby. Skipping scan.")
		return

	# Filter monsters inside ORIGINAL training area ("Styria") bounds
	valid_monsters = []
	for key, mob in monsters.items():
		mob_dist_to_center = GetDistance(mob['x'], mob['y'], original_training_area['x'], original_training_area['y'])
		if mob_dist_to_center <= original_training_area['radius']:
			valid_monsters.append(mob)

	if not valid_monsters:
		log("Plugin: No monsters inside the original training area. Skipping scan.")
		return

	log("Plugin: Found %d monsters inside the original training area." % len(valid_monsters))

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

	# 3. Switch to temp area and set coordinates if another spot has higher density and is at a reasonable distance (> 5.0 units)
	if best_mob and max_density > current_mobs_count:
		dist_to_mob = GetDistance(char_pos['x'], char_pos['y'], best_mob['x'], best_mob['y'])
		if dist_to_mob > 5.0:
			log("Plugin: Switching to training area 'temp' (current spot: %d mobs vs cluster: %d mobs at %.1f units away)." % (current_mobs_count, max_density, dist_to_mob))
			stop_bot()
			
			# Helper function to change training area and position with delay
			def do_shift(region, x, y, z):
				if set_training_area("temp"):
					set_training_position(region, x, y, z)
				else:
					log("Plugin: Error - Temporary training area 'temp' not found in phBot list! Cannot shift position.")

			# Set the shifting flag to prevent event_loop from restoring original area during stop
			shifting_training_area = True

			# Schedule training area change after 1.0 second
			target_z = best_mob.get('z', char_pos['z'])
			Timer(1.0, do_shift, [best_mob['region'], best_mob['x'], best_mob['y'], target_z]).start()
			
			# Schedule bot start after 2.0 seconds
			Timer(2.0, do_start_bot).start()
		else:
			log("Plugin: Densest cluster is too close (%.1f units). Skipping shift." % dist_to_mob)
	else:
		log("Plugin: Current spot is already the densest or equal (current: %d mobs, max cluster: %d mobs). Skipping shift." % (current_mobs_count, max_density))

# Plugin loaded
log('Plugin: ' + pName + ' v' + pVersion + ' successfully loaded')
