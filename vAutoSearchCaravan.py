from phBot import *
import QtBind
from datetime import datetime
from threading import Timer
import urllib.request
import urllib.parse
import struct
import json
import time
import os
import re

pName = 'vAutoCaravanNotify'
pVersion = '1.2.1'
pUrl = ''

# ______________________________ Initializing ______________________________ #

URL_HOST = "https://discord-production-2346.up.railway.app"  # API server
URL_REQUEST_TIMEOUT = 15  # sec
DISCORD_FETCH_DELAY = 5000  # ms
CHANNEL_ID = "1429534058991583384"  #"799071867512029217"
TOKEN = "XenoXN"
TRADER_HUNTER_EVENT_ID = 1

# Globals

''''''''''''
character_data = None
char_names = []  # Buffer to store detected hunters/traders
buffer_timer = None  # Timer for the buffer
BUFFER_DELAY = 1.0  # seconds to wait before sending notification
enable_notifications = False  # Default: notifications disabled
stop_bot_on_detect = False  # Default: don't stop bot
include_player_name = False  # Default: don't include player name
town_zones = ["Alexandria", "Jangan", "Western China Donwhang", "Hotan Kingdom", "Samarkand", "Constantinople"]
zone_names_readable = {
    "Alexandria": "Alex",
    "Jangan": "JG",
    "Western China Donwhang": "DW",
    "Hotan Kingdom": "HT",
    "Samarkand": "SMK",
    "Constantinople": "Const"
}

# Graphic user interface
gui = QtBind.init(__name__, pName)

QtBind.createLabel(gui, pName + " is a plugin that reports caravans around to Discord! Made for Shadows members <3", 6,
                   10)
# Simple one-line logo in gui
QtBind.createLabel(gui, "By:\nE n c r y p t\nS h a d o w s", 640, 100)

# Checkbox to enable/disable notifications
cbxEnableNotifications = QtBind.createCheckBox(gui, 'cbxEnableNotifications_checked', 'Enable Discord Notifications', 6, 30)

# Checkbox to enable/disable bot stopping
cbxStopBot = QtBind.createCheckBox(gui, 'cbxStopBot_checked', 'Stop Bot on Detection', 6, 50)

# Checkbox to include player name in notifications
cbxIncludePlayerName = QtBind.createCheckBox(gui, 'cbxIncludePlayerName_checked', 'Include Player Name in Notification', 6, 70)


def getConfig():
    return get_config_dir() + pName + ".json"


# Checkbox handler for enable notifications
def cbxEnableNotifications_checked(checked):
    global enable_notifications
    enable_notifications = checked
    saveConfigs()
    log("Plugin: Discord notifications have been " + ("enabled" if checked else "disabled"))


# Checkbox handler for stop bot on detection
def cbxStopBot_checked(checked):
    global stop_bot_on_detect
    stop_bot_on_detect = checked
    saveConfigs()
    log("Plugin: Stop bot on detection has been " + ("enabled" if checked else "disabled"))


# Checkbox handler for include player name
def cbxIncludePlayerName_checked(checked):
    global include_player_name
    include_player_name = checked
    saveConfigs()
    log("Plugin: Include player name in notification has been " + ("enabled" if checked else "disabled"))


# Load configs
def loadConfigs():
    # Load character data
    char_name = get_character_data()['name']
    # Load plugin configs
    if os.path.exists(getConfig()):
        with open(getConfig(), "r") as f:
            data = json.load(f)
        # Load settings for this character
        if char_name in data:
            global enable_notifications, stop_bot_on_detect, include_player_name
            char_data = data[char_name]

            # Load each setting with default values if not found
            enable_notifications = char_data.get('enable_notifications', False)
            stop_bot_on_detect = char_data.get('stop_bot_on_detect', False)
            include_player_name = char_data.get('include_player_name', False)

            # Update GUI checkboxes to reflect loaded settings
            QtBind.setChecked(gui, cbxEnableNotifications, enable_notifications)
            QtBind.setChecked(gui, cbxStopBot, stop_bot_on_detect)
            QtBind.setChecked(gui, cbxIncludePlayerName, include_player_name)


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

    # Update the character's settings
    data[char_name] = {
        'enable_notifications': enable_notifications,
        'stop_bot_on_detect': stop_bot_on_detect,
        'include_player_name': include_player_name
    }

    # Save the updated config
    with open(getConfig(), "w") as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))
    log("Plugin: configs saved successfully.")


# ______________________________ Methods ______________________________ #

# Remove duplicate char names and group similar names with wildcards
# Example: ["anotherPlayer", "caravan1", "caravan2", "caravan3"] -> ["anotherPlayer", "caravan*"]
def remove_duplicate_names(names):
    if not names:
        return []

    # Find common prefixes
    prefix_groups = {}
    standalone = []

    for name in names:
        # Try to find a base name by removing trailing digits
        match = re.match(r'^(.+?)\d+$', name)
        if match:
            prefix = match.group(1)
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(name)
        else:
            standalone.append(name)

    # Build result list
    result = []

    # Add standalone names (no pattern detected)
    result.extend(standalone)

    # Add grouped names with wildcard if there are multiple with same prefix
    for prefix, group in prefix_groups.items():
        if len(group) > 1:
            # Multiple names with same prefix, use wildcard
            result.append(f"{prefix}*")
        else:
            # Only one name with this prefix, keep it as is
            result.append(group[0])

    return result

# Get readable town names
def get_zone_name_readable(zone_name):
    global zone_names_readable
    return zone_names_readable.get(zone_name, zone_name)

# Send buffered events as a single notification
def send_buffered_notification():
    global char_names, buffer_timer, character_data, enable_notifications, stop_bot_on_detect, include_player_name

    discord_message= "\n---------\n"

    if not char_names:
        char_names = []
        buffer_timer = None
        return

    # Check if notifications are enabled using global variable
    if not enable_notifications:
        # Notifications disabled, just reset buffer
        char_names = []
        buffer_timer = None
        return

    # Count the total entities detected
    players_count = len(char_names)

    # Get character data if not already available
    character_data = get_character_data()

    char_name_prefix = ""
    # Use global variable instead of checking GUI
    if include_player_name:
        if players_count == 1:
            char_name_prefix = f"{character_data['name']}: "
        else:
            char_name_prefix = f"**Reporter:** {character_data['name']}\n"

    zone_name = character_data['zone_name']
    # Skip notifications if in town zones and number less than 12 players
    if zone_name in town_zones and players_count < 12:
        char_names = []
        buffer_timer = None
        return

    position_info = get_position()
    x = int(position_info['x'])
    y = int(position_info['y'])
    readable_zone_name = get_zone_name_readable(zone_name)
    # Build the message
    if players_count == 1:
        discord_message += f"{char_name_prefix}**1 Hunter/Trader** ({char_names[0]}) detected at **{readable_zone_name}**"
    else:
        discord_message += f"{char_name_prefix}**Number:** {players_count} Hunter(s)/Trader(s)\n**Location: **{readable_zone_name}"
        if not zone_name in town_zones:
            # If outside town, remove duplicate names and group similar ones
            unique_names = remove_duplicate_names(char_names)
            if unique_names and len(unique_names) > 0:
                unique_names_limited = unique_names[:20]  # Limit to first 20 names
                if len(unique_names) > 20:
                    unique_names_limited.append(f"...and {len(unique_names) - 20} more")
                # Append names to the message
                names_list = ", ".join(unique_names_limited)
                discord_message += f"\n**Names:** {names_list}"

    # Send the notification to Discord if outside town
    if not zone_name in town_zones:
        discord_message+= f"\nLocation link: https://fizodev.github.io/xSROMap?x={x}&y={y}"
    Notify(message=discord_message, colour=0xFF5722)

    # Stop bot using global variable instead of checking GUI
    if stop_bot_on_detect:
        stop_bot()

    # Reset buffer
    char_names = []
    buffer_timer = None


# Send a notification to discord channel
# message : Text shown as discord notification
# info : Extra data used at server for some notifications
def Notify(message, info=None, colour=None):
    global CHANNEL_ID, TOKEN
    # Run this in another thread to avoid locking the client/bot and wait more time for the response
    Timer(0.001, _Notify, (CHANNEL_ID, TOKEN, message, info, colour)).start()


# Send a notification to discord channel
def _Notify(channel_id, token, message, info, colour):
    # Check if there is enough data to create a notification
    if not channel_id or not message:
        return
    url = URL_HOST
    if not url:
        return
    # Try to send notification
    try:
        # Create json to send
        data = {"token": token, "channel": channel_id, "message": message}
        if info:
            data["info"] = info
        if colour is not None:
            data["colour"] = colour
        # Prepare data to send through POST method
        params = json.dumps(data).encode('utf8')
        if not url.endswith("/"):
            url += "/"
        req = urllib.request.Request(url + "api/notify", data=params, headers={'content-type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as f:
            try:
                msg = f.read().decode('utf-8')
                if msg == 'true' or msg == 'success':
                    log("Plugin: notify sent to Discord!")
                else:
                    if msg == 'true' or msg == 'success' or '"status":"success"' in msg:
                        log("Plugin: Discord notification successfully sent.")
                    else:
                        log("Plugin: notify failed [" + msg + "]")
            except Exception as ex2:
                log("Plugin: Error reading response from server [" + str(ex2) + "]")
    except Exception as ex:
        log("Plugin: Error loading url [" + str(ex) + "] to Notify")


# ______________________________ Events ______________________________ #

# Called when the character enters the game world
def joined_game():
    global character_data
    character_data = get_character_data()
    loadConfigs()


# Called when the character has been disconnected
def disconnected():
    global character_data, char_names, buffer_timer
    character_data = None
    char_names = []
    if buffer_timer:
        buffer_timer.cancel()
        buffer_timer = None


# Called for specific events. data field will always be a string.
def handle_event(t, data):
    global TRADER_HUNTER_EVENT_ID, char_names, buffer_timer, BUFFER_DELAY

    if t == TRADER_HUNTER_EVENT_ID:
        # Add entity to buffer
        char_names.append(data)

        # If this is the first event in the buffer, start the timer
        if buffer_timer is None:
            buffer_timer = Timer(BUFFER_DELAY, send_buffered_notification)
            buffer_timer.start()
    # If timer is already running, just add to buffer (timer will handle it)


# Plugin loaded
log('Plugin: ' + pName + ' (by Encrypt) v' + pVersion + ' successfully loaded')
