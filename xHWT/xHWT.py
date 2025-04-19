from phBot import *
import struct
import QtBind
from threading import Timer
import json
import os

pName = 'xHWT'
pVersion = '1.1.0'
pUrl = 'https://github.com/fizodev/phbot-plugins/tree/main/xHWT'

# Initialize GUI
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'Welcome to xHWT plugin, it\'s a simple plugin to manage micro tasks for HWT daily entries. '+
'\n\n It will do the following: \n\t- Skip Run: Will skip the existing run if you reach the max entries limit.\n\t- Disconnect: Will disconnect you if you reach the max entries limit 6 times.'+
'\n\n You have to be using the HWT scripts from the repository here (https://github.com/fizodev/phbot-plugins). '+
'\n\n Developed by ViRUS (Legion Online | Shadows <3)',
6, 10)


# Create the enable/disable checkbox
cbxEnabled = QtBind.createCheckBox(gui, 'cbxEnabled_checked', 'Enable plugin', 6, 170)
pluginEnabled = False

# OP code for HWT
hwt_op_code = '0xB05A' # refactor this to be integer instead of hex string
# a packet that is received if the char in party and ready to enter the HWT
hwt_response_ok = '02 01 00'
hwt_response_ok_received = False
# a packet that is received if the char in party and reached the max entries for the day
hwt_response_max_entries = '02 27 1C'
# a packet that is received if the char in party and just entered the HWT
hwt_response_entered = '01'
# a packet that is received if the char not in party and can not enter the HWT
hwt_response_not_in_party = '02 2A 1C'

# a counter to track how many times we reached the max entries, and make action if it's equal to 6 times
# the counter will be reset to 0 if the character entered the HWT
max_entries_reached_counter = 0

# centralized logger
def xHWT_log(message):
    log('Plugin (xHWT): '+message)

# Return plugin configs path (JSON)
def getConfig():
    return get_config_dir() + pName + ".json"

# Load configs
def loadConfigs():
    # Load character data
    char_name = get_character_data()['name']
    # Load plugin configs
    if os.path.exists(getConfig()):
        with open(getConfig(), "r") as f:
            data = json.load(f)
        # Load enabled state based on the char name
        if char_name in data:
            global pluginEnabled
            pluginEnabled = data[char_name]
            QtBind.setChecked(gui, cbxEnabled, pluginEnabled)

# Save configs
def saveConfigs():
    # Get character name
    char_name = get_character_data()['name']

    # Initialize data dictionary
    data = {}

    # Load existing config if it exists
    if os.path.exists(getConfig()):
        with open(getConfig(), "r") as f:
            data = json.load(f)

    # Update the character's enabled state
    data[char_name] = pluginEnabled

    # Save the updated config
    with open(getConfig(), "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))
    xHWT_log("Plugin configs saved successfully.")

# Checkbox handler
def cbxEnabled_checked(checked):
    global pluginEnabled
    pluginEnabled = checked
    saveConfigs()
    xHWT_log("The plugin has been " + ("enabled" if checked else "disabled"))

# All packets received from game server will be passed to this function
def handle_joymax(opcode, data):
    if pluginEnabled:
        # Format the opcode as a hexadecimal string
        opcode_hex = '0x{:02X}'.format(opcode)

        # Format the data as a space-separated string of hexadecimal values
        if data:
            data_hex = ' '.join('{:02X}'.format(x) for x in data)
        else:
            data_hex = "None"

        if opcode_hex == hwt_op_code:
            handle_hwt_packet(data_hex)

    return True

def handle_hwt_packet(data_hex):
    global max_entries_reached_counter, hwt_response_ok_received

    if hwt_response_not_in_party in data_hex:
        xHWT_log('You are not in party.')
        return

    # Check if the packet is the HWT response
    if hwt_response_ok in data_hex:
        hwt_response_ok_received = True
        return

    if hwt_response_entered in data_hex and hwt_response_ok_received:
        max_entries_reached_counter = 0
        hwt_response_ok_received = False
        xHWT_log('You have entered the HWT. Resetting the counter.')
        return

    if hwt_response_max_entries in data_hex and hwt_response_ok_received:
        hwt_response_ok_received = False
        max_entries_reached_counter += 1
        xHWT_log("Max entries reached for this level. Skipping existing run...")
        # check if the counter reached 6 times
        if max_entries_reached_counter >= 6:
            # reset the counter and disconnect
            max_entries_reached_counter = 0
            xHWT_log('Max entries reached 6 or more times. Disconnecting...')
            disconnect()
        else:
            # skip the existing run by stopping the bot and walking away and starting again
            skip_existing_run_method_1()

# skip the existing run by switching to the next script
def skip_existing_run_method_1():
    # stop the bot
    xHWT_log('Stopping bot...')
    if stop_bot():
        # get the current training script
        current_script = get_training_area()['path']
        xHWT_log('Current training script: ' + current_script)
        # get the next training script path
        next_script = get_next_training_script(current_script)
        xHWT_log('Next training script: ' + next_script)

        # Helper function to set the script
        def set_script():
            # set the next training script path
            set_training_script(next_script)
            xHWT_log('Setting next training script...')

        # Add delay before setting the next training script (2 seconds)
        Timer(1.0, set_script, ()).start()
        # start the bot after a delay of 1 second
        Timer(2.0, start_bot, ()).start()
    else:
        xHWT_log('Failed to stop the bot. Please try again.')

# Get the next training script path based on the current script
# example: if the current script is 'HWT_1.txt', the next script will be 'HWT_2.txt'
# if the current script is 'HWT_6.txt', the next script will be 'HWT_1.txt' back again
def get_next_training_script(current_script):
    # Get directory containing the current script
    script_dir = os.path.dirname(current_script)
    # Get the current script name without the extension
    script_name = os.path.splitext(os.path.basename(current_script))[0]
    # Get the current script number
    script_number = int(script_name.split('_')[1])
    # Get the next script number
    next_script_number = (script_number % 6) + 1
    # Get the next script name
    next_script_name = 'HWT_' + str(next_script_number) + '.txt'
    # Get the next script path
    next_script_path = os.path.join(script_dir, next_script_name)
    return next_script_path

# skip the existing run by stopping the bot and walking away and starting again
def skip_existing_run_method_2():
    xHWT_log('Stopping bot...')
    # stop the bot
    if stop_bot():
        # walk away
        xHWT_log('Walking away to -11642,-3278')
        Timer(1.0, move_away, ()).start()
        # leave the party after 40 seconds
        Timer(40.0, leave_party, ()).start()
        # Add delay before starting the bot again (31 seconds)
        Timer(41.0, start_bot, ()).start()
    else:
        xHWT_log('Failed to stop the bot. Please try again.')

def move_away():
    move_to(-11642.0, -3278.0, 0.0)

def leave_party():
    xHWT_log('Leaving party...')
    inject_joymax(0x7061, bytearray(), True)

# Plugin loaded
log('Plugin: ' + pName + ' (by ViRUS) v' + pVersion + ' successfully loaded')
loadConfigs()
