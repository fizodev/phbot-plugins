from phBot import *
import QtBind
from threading import Timer
import json
import os

pName = 'xHWT'
pVersion = '1.0.0'
pUrl = 'https://github.com/fizodev/phbot-plugins/tree/main/xHWT'

# Initialize GUI
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui, 'Welcome to xHWT plugin, it\'s a simple plugin to manage micro tasks for HWT daily entries. '+
'\n\n It will skip the existing run if you reach the max entries limit. '+
'\n\n You have to be using the HWT scripts from the repository here (https://github.com/fizodev/phbot-plugins). '+
'\n\n Developed by ViRUS (Shadows <3)',
6, 10)


# Create the enable/disable checkbox
cbxEnabled = QtBind.createCheckBox(gui, 'cbxEnabled_checked', 'Enable plugin', 6, 140)
pluginEnabled = False

# target OP codes for max entries
target_op_code = '0xB05A'
target_data_part1 = '02 01 00'
target_data_part2 = '02 27 1C'

# booleans to track if the target op code and data are found
found_op_code = False
found_data_part1 = False
found_data_part2 = False

# Return plugin configs path (JSON)
def getConfig():
    return get_config_dir() + pName + ".json"

# Load configs
def loadConfigs():
    if os.path.exists(getConfig()):
        data = {}
        with open(getConfig(), "r") as f:
            data = json.load(f)
        # Load enabled state
        if "Enabled" in data:
            global pluginEnabled
            pluginEnabled = data["Enabled"]
            QtBind.setChecked(gui, cbxEnabled, pluginEnabled)

# Save configs
def saveConfigs():
    data = {}
    data['Enabled'] = pluginEnabled

    with open(getConfig(), "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))

# Checkbox handler
def cbxEnabled_checked(checked):
    global pluginEnabled
    pluginEnabled = checked
    saveConfigs()
    log("Plugin: " + pName + " has been " + ("enabled" if checked else "disabled"))

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

        if opcode_hex == target_op_code:
            global found_op_code
            found_op_code = True
            # Check if the target data part 1 is found
            if target_data_part1 in data_hex:
                global found_data_part1
                found_data_part1 = True
            # Check if the target data part 2 is found
            if target_data_part2 in data_hex:
                global found_data_part2
                found_data_part2 = True
            # If both target data parts are found, print a message
            if found_data_part1 and found_data_part2:
                log("xHWT: Max entries reached. Skipping existing run...")
                # Reset the flags
                found_op_code = False
                found_data_part1 = False
                found_data_part2 = False
                skip_existing_run_method_2()

    return True

# skip the existing run by switching to the next script
def skip_existing_run_method_1():
    # stop the bot
    if stop_bot():
        log('Stopping bot...')
        # get the current training script
        current_script = get_training_area()['path']
        log('Current training script: ' + current_script)
        # get the next training script path
        next_script = get_next_training_script(current_script)
        log('Next training script: ' + next_script)

        # Helper function to set the script
        def set_script():
            # set the next training script path
            set_training_script(next_script)
            log('Setting next training script...')

        # Add delay before setting the next training script (2 seconds)
        Timer(1.0, set_script, ()).start()
        # start the bot after a delay of 1 second
        Timer(2.0, start_bot, ()).start()
    else:
        log('Failed to stop the bot. Please try again.')

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
    log('Stopping bot...')
    # stop the bot
    if stop_bot():
        # walk away
        log('Walking away to -11642,-3278')
        Timer(1.0, move_away, ()).start()
        # leave the party after 30 seconds
        Timer(30.0, leave_party, ()).start()
        # Add delay before starting the bot again (31 seconds)
        Timer(31.0, start_bot, ()).start()
    else:
        log('Failed to stop the bot. Please try again.')

def move_away():
    move_to(-11642.0, -3278.0, 0.0)

def leave_party():
    log('Leaving party...')
    inject_joymax(0x7061, bytearray(), True)

# Plugin loaded
log('Plugin: ' + pName + ' (By Virus) v' + pVersion + ' successfully loaded')
loadConfigs()
