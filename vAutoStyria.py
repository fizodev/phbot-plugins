from phBot import *
import QtBind
from threading import Timer
import struct

pVersion = '2.2.0'
pName = 'vAutoStyria'

REQUIRED_PROFILE = 'Styria'

# Looping state
teleporting_to_hotan = False

# Checkbox handler
def cbxEnableLoop_checked(checked):
	log("Plugin: Hotan looping has been " + ("enabled" if checked else "disabled"))

# Graphic user interface
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'vAutoStyria detects teleportation. If character is found outside Styria Room,\n'
                                 'it waits few seconds then teleports out to Hotan.\n\n'
                                 'By: H Y P E R V I S O R', 10, 10)

cbxEnableLoop = QtBind.createCheckBox(gui, 'cbxEnableLoop_checked', 'Enable Hotan Looping (5 min sleep)', 10, 75)
QtBind.setChecked(gui, cbxEnableLoop, True)

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
	global teleporting_to_hotan
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
					log("Plugin: Arrived in Hotan. Sleeping 5 minutes before starting the bot again...")
					Timer(300.0, start_bot).start()

# Called every 500ms
def event_loop():
	pass

# Plugin loaded
log('Plugin: ' + pName + ' v' + pVersion + ' successfully loaded')
