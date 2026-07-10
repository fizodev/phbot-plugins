from phBot import *
import struct
import binascii
import QtBind
import time
from threading import Timer
import json
import os
import random
from time import sleep

pName = 'vAutoCaravan'
pVersion = '1.1.0'
pUrl = ''

# ==============================================================================
# Global Variable for Session Token
# ==============================================================================
# IMPORTANT: This token is session-specific and CHANGES every time you restart
# the game or potentially after a certain period.
# You MUST update this variable with the CURRENT valid token for your session
session_token = ""
# OP Codes for captcha related operations
answer_captcha_op_code = 0x7055
received_captcha_op_code = 0x5055
# ==============================================================================

pluginEnabled = False
buy_sell_paused = False

# Initialize GUI
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui,
                             'Welcome to vAutoCaravan plugin, it\'s a simple plugin to resolve the captcha everytime it appears.\n' +
                             'Please make sure to have the session token captured by answering the captcha yourself manually for the first time.\n' +
                             'You will see in the logs \'Extracted new token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx\''
                             '\n\nDeveloped by ViRUS (Legion Online | Shadows <3)',
                             6, 10)

# Create the enable/disable checkbox
cbxEnabled = QtBind.createCheckBox(gui, 'cbxEnabled_checked', 'Enable plugin', 6, 110)
lblTokenStatus = QtBind.createLabel(gui, 'Session Token: Not Available', 6, 150)
btnBuy = QtBind.createButton(gui, 'btnBuy_clicked', 'Start Buy', 6, 170)
btnSell = QtBind.createButton(gui, 'btnSell_clicked', 'Start Sell', 6, 210)

# centralized logger
def xlog(message):
    log('Plugin (vAutoCaravan): ' + message)

# bandit
# [14:47:49] Client: (Opcode) 0x7C45 (Data) 77 01 00 00
# [14:47:51] Client: (Opcode) 0x704B (Data) 77 01 00 00
# [14:47:51] Client: (Opcode) 0x7046 (Data) 77 01 00 00 0C
# [14:47:54] Client: (Opcode) 0x7034 (Data) 14 49 76 47 00 00 28 00 77 01 00 00
# [14:47:55] Client: (Opcode) 0x704B (Data) 77 01 00 00


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
    xlog("Plugin configs saved successfully.")


# Checkbox handler
def cbxEnabled_checked(checked):
    global pluginEnabled
    pluginEnabled = checked
    xlog("The plugin has been " + ("enabled" if checked else "disabled"))
    saveConfigs()
    update_token_status()


def btnBuy_clicked():
    start_jg_buy()
    # try:
    #     inject_joymax(0x7194, struct.pack('8B', 0x01, 0x00, 0x00, 0x00, 0x14, 0x2B, 0xA7, 0x0D), False)
    #     inject_joymax(0x34B6, None, False)
    #     inject_joymax(0x3012, None, False)
    #     inject_joymax(0x750E, None, False)
    # except Exception as e:
    #     xlog(f"Error processing answer: {e}")
    #     return None
    # open_samarkand_trader_npc()
    # Timer(1.0, start_buy_goods).start()
    # open_dw_trader_npc()
    # monsters = get_monsters()
    # log(f"Monsters: {monsters}")

def b_jg(args):
    xlog("Script: starting JG Buy process...")
    start_jg_buy()
    return 2*60* 1000  # Return the time in milliseconds to wait before the next execution

def s_bandit(args):
    xlog("Script: starting Bandit Sell process...")
    start_bandit_sell()
    return 90 * 1000  # Return the time in milliseconds to wait before the next execution

def restart_trade_loop(args):
    Timer(3.0, start_bot).start()
    return 0

def start_jg_buy():
    open_jangan_trader_npc()
    Timer(1.5, start_buy_goods).start()

def start_bandit_sell():
    open_bandit_trader_npc()
    Timer(1.5, start_sell_goods).start()

def btnSell_clicked():
    # slot_index_decimal = get_first_item_index_in_trans_pet()
    # index_byte = struct.pack('B', slot_index_decimal)
    #
    # xlog(f"{slot_index_decimal} - {index_byte}")
    # xlog(f"Hex value: {binascii.hexlify(index_byte).decode('ascii')}")  # Shows 0a

    start_bandit_sell()

def is_trans_pet_full():
    pets = get_pets()
    if not pets:
        xlog("No pets found")
        return None

    # Find transport pet
    for pet_id, pet_data in pets.items():
        if pet_data['type'] == 'transport':
            # Check if any slot is empty (None)
            for item in pet_data['items']:
                if item is None:
                    return False  # Found an empty slot

            # If we got here, all slots are filled
            return True

    xlog("No transport pet found")
    return None

def get_first_item_index_in_trans_pet():
    pets = get_pets()
    if not pets:
        xlog("No pets found")
        return None

    # Find transport pet
    for pet_id, pet_data in pets.items():
        if pet_data['type'] == 'transport':
            # Check for the first item index
            for index, item in enumerate(pet_data['items']):
                if item is not None:
                    return index  # Found the first item index
            # If we got here, all slots are empty
            xlog("Transport pet is empty")
            return None

    xlog("No transport pet found")
    return None

def start_buy_goods():
    xlog("Starting to buy goods...")

    # Maximum number of attempts to avoid infinite loops
    max_attempts = 250
    attempts = 0

    sleep(1.0)
    while attempts < max_attempts:
        # Check if transport pet is full
        pet_status = is_trans_pet_full()

        # If pet_status is None, it means no transport pet was found
        if pet_status is None:
            xlog("Error: No transport pet found. Stopping purchase process.")
            return False

        # If pet is full, we're done
        if pet_status is True:
            xlog("Transport pet inventory is full. Stopping purchase process.")
            Timer(0.5, close_JG_trader_npc).start()
            return True

        # Buy goods, only If buy/sell paused for captcha solving
        if not buy_sell_paused:
            buy_JG_item()

        # Add a small random delay between purchases
        delay = generate_random_delay(0.5, 0.7)
        ## add to seconds to the delay if this is the first buy to give time to solve captcha
        if attempts == 0:
            delay += 1.5
        sleep(delay)

        attempts += 1

    xlog(f"Reached maximum attempts ({max_attempts}). Stopping purchase process.")
    close_JG_trader_npc()
    return False

def start_sell_goods():
    xlog("Starting to sell goods...")

    # Maximum number of attempts to avoid infinite loops
    max_attempts = 250
    attempts = 0

    while attempts < max_attempts:
        # Check if any goods left in the transport pet
        item_index = get_first_item_index_in_trans_pet()

        # If pet_status is None, it means no transport pet was found
        if item_index is None:
            xlog("No items or trans pets found, stopping selling process.")
            Timer(0.5, close_bandit_trader_npc()).start()
            return False

        # Buy goods, only If buy/sell paused for captcha solving
        if not buy_sell_paused:
            sell_bandit_item_at_index(item_index)
        else :
            xlog("Buy/Sell process paused due to CAPTCHA. Waiting...")

        # Add a small random delay between sells
        delay = generate_random_delay(0.3, 0.5)
        ## add to seconds to the delay if this is the first buy to give time to solve captcha
        if attempts == 0:
            delay += 1.0

        sleep(delay)

        attempts += 1

    xlog(f"Reached maximum attempts ({max_attempts}). Stopping selling process.")
    close_bandit_trader_npc()
    return False

def open_jangan_trader_npc():
    xlog("Opening JG Trader NPC...")
    # talk to the JG Trader NPC
    inject_joymax(0x7C45, struct.pack('4B', 0x5C, 0x01, 0x00, 0x00), True)

    def open_jg_trader_npc_trade_option():
        inject_joymax(0x704B, struct.pack('4B', 0x5C, 0x01, 0x00, 0x00), True)
        sleep(0.5)
        inject_joymax(0x7046, struct.pack('5B', 0x5C, 0x01, 0x00, 0x00, 0x0C), True)

    # select trade option after 1 second
    Timer(1.0, open_jg_trader_npc_trade_option).start()

def open_bandit_trader_npc():
    xlog("Opening Bandit Trader NPC...")
    # talk to the Bandit Trader NPC
    inject_joymax(0x7C45, struct.pack('4B', 0x77, 0x01, 0x00, 0x00), True)

    def open_bandit_trader_npc_trade_option():
        inject_joymax(0x704B, struct.pack('4B', 0x77, 0x01, 0x00, 0x00), True)
        sleep(0.5)
        inject_joymax(0x7046, struct.pack('5B', 0x77, 0x01, 0x00, 0x00, 0x0C), True)

    # select trade option after 1 second
    Timer(1.0, open_bandit_trader_npc_trade_option).start()

def open_dw_trader_npc():
    # Example:
    # (Opcode) 0x7C45 (Data) 1E 00 00 00
    # (Opcode) 0x704B (Data) 1E 00 00 00
    # (Opcode) 0x7046 (Data) 1E 00 00 00 0C
    xlog("Opening DW Trader NPC...")
    # talk to the DW Trader NPC
    inject_joymax(0x7C45, struct.pack('4B', 0x1E, 0x00, 0x00, 0x00), True)
    inject_joymax(0x704B, struct.pack('4B', 0x1E, 0x00, 0x00, 0x00), True)
    inject_joymax(0x7046, struct.pack('5B', 0x1E, 0x00, 0x00, 0x00, 0x0C), True)

def open_samarkand_trader_npc():
    xlog("Opening Samarkand Trader NPC...")
    # talk to the Samarkand Trader NPC
    inject_joymax(0x7C45, struct.pack('4B', 0x5C, 0x02, 0x00, 0x00), True)
    inject_joymax(0x704B, struct.pack('4B', 0x5C, 0x02, 0x00, 0x00), True)
    inject_joymax(0x7046, struct.pack('5B', 0x5C, 0x02, 0x00, 0x00, 0x0C), True)

def open_hotan_trader_npc():
    # Example:
    # (Opcode) 0x7C45 (Data) 69 03 00 00
    # (Opcode) 0x704B (Data) 69 03 00 00
    # (Opcode) 0x7046 (Data) 69 03 00 00 0C
    xlog("Opening HT Trader NPC...")
    # talk to the HT Trader NPC
    inject_joymax(0x7C45, struct.pack('4B', 0x69, 0x03, 0x00, 0x00), True)
    inject_joymax(0x704B, struct.pack('4B', 0x69, 0x03, 0x00, 0x00), True)
    inject_joymax(0x7046, struct.pack('5B', 0x69, 0x03, 0x00, 0x00, 0x0C), True)

def close_JG_trader_npc():
    xlog("Closing JG Trader NPC...")
    # close the JG Trader NPC
    inject_joymax(0x704B, struct.pack('4B', 0x5C, 0x01, 0x00, 0x00), True)

def close_bandit_trader_npc():
    xlog("Closing Bandit Trader NPC...")
    # close the Bandit Trader NPC
    inject_joymax(0x704B, struct.pack('4B', 0x77, 0x01, 0x00, 0x00), True)

def close_DW_trader_npc():
    xlog("Closing DW Trader NPC...")
    inject_joymax(0x704B, struct.pack('4B', 0x1E, 0x00, 0x00, 0x00), True)

def close_samarkand_trader_npc():
    xlog("Closing Samarkand Trader NPC...")
    # close the Samarkand Trader NPC
    inject_joymax(0x704B, struct.pack('4B', 0x5C, 0x02, 0x00, 0x00), True)

def close_hotan_trader_npc():
    xlog("Closing HT Trader NPC...")
    # close the HT Trader NPC
    inject_joymax(0x704B, struct.pack('4B', 0x69, 0x03, 0x00, 0x00), True)


def update_token_status():
    """Updates the token status label and enables/disables buttons based on token availability"""
    global lblTokenStatus, session_token

    # Check if token is valid
    token_valid = isinstance(session_token, str) and len(session_token) == 32

    # Update token status label
    status_text = f"Session Token: {session_token}" if token_valid else "Session Token: Not Available"
    QtBind.setText(gui, lblTokenStatus, status_text)


def generate_random_delay(min_delay, max_delay):
    """
      Generates a random delay between min_delay and max_delay.

      Args:
          min_delay: Minimum delay in seconds.
          max_delay: Maximum delay in seconds.

      Returns:
          float: Random delay between min_delay and max_delay.
      """
    return random.uniform(min_delay, max_delay)


# All packets received from game server will be passed to this function
def handle_joymax(opcode, data):
    if pluginEnabled:
        if opcode == received_captcha_op_code and len(session_token) == 32:
            handle_captcha_question(data)

    return True


def handle_captcha_question(data):
    global buy_sell_paused
    buy_sell_paused_for_captcha = True
    decoded_question = decode_captcha_question(data)

    if decoded_question is None:
        xlog("Error: Failed to decode CAPTCHA question.")
        return

    captcha_answer = solve_captcha_question(decoded_question)

    if captcha_answer is None:
        xlog("Error: Failed to solve CAPTCHA question.")
        return

    xlog(f"Received CAPTCHA - question: {decoded_question} - Answer: {captcha_answer}")

    def helper_send_captcha_answer_to_server():
        send_captcha_answer_to_server(captcha_answer)

    # Send the answer to the server after a short delay
    random_delay = generate_random_delay(1.0, 1.5)
    Timer(random_delay, helper_send_captcha_answer_to_server).start()


def solve_captcha_question(question_string):
    """
      Solves simple math CAPTCHA questions based on the observed pattern.

      Expected format: "What is num1 operator num2"
      Supported operators: 'plus', '*'

      Args:
          question_string: The decoded CAPTCHA question (e.g., "What is 8 plus 7").

      Returns:
          str: The calculated answer as a string.
          None: If the question format is unrecognized, numbers are invalid,
                or the operator is unsupported.
      """

    if not isinstance(question_string, str):
        xlog("Error: Input must be a string.")
        return None

    parts = question_string.split(' ')
    # Expected structure needs at least 5 parts: "What", "is", num1, operator, num2
    if len(parts) < 5:
        xlog(f"Error: Unexpected question format (too few parts): '{question_string}'")
        return None

    # Extract the assumed number strings and operator string
    num1_str = parts[-3]
    operator = parts[-2]
    num2_str = parts[-1]

    try:
        # Convert number strings to integers
        num1 = int(num1_str)
        num2 = int(num2_str)
    except ValueError:
        xlog(f"Error: Could not parse numbers from question: '{question_string}' "
             f"(extracted '{num1_str}', '{num2_str}')")
        return None

    # Perform calculation based on the operator
    result = None
    if operator == "plus":
        result = num1 + num2
    elif operator == "*":
        result = num1 * num2
    else:
        xlog(f"Error: Unsupported or unrecognized operator '{operator}' in question: '{question_string}'")
        return None

    # Convert the numerical result back to a string
    return str(result)


def handle_silkroad(opcode, data):
    if opcode == answer_captcha_op_code:
        update_token_from_payload(data)

    return True


def create_captcha_answer_payload(answer):
    global session_token

    # --- Input Validation ---
    try:
        answer_str = str(answer)
        if not answer_str.isdigit():
            xlog(f"Error: Answer '{answer_str}' must contain only digits.")
            return None
    except Exception as e:
        xlog(f"Error processing answer: {e}")
        return None

    # --- Session Token Validation ---
    if not isinstance(session_token, str) or len(session_token) != 32:
        xlog(f"Error: Invalid session_token (should be 32-character hex string).")
        xlog(f"Current value: {session_token}")
        reset("Invalid session token")
        return None

    # --- Payload Construction ---
    try:
        # 1. Answer Length (2 bytes, little-endian)
        answer_len = len(answer_str)
        length_bytes = struct.pack('<H', answer_len)

        # 2. Answer String (ASCII codes as bytes)
        answer_bytes = bytearray()
        for digit in answer_str:
            answer_bytes.append(ord(digit))  # Convert each digit to its ASCII code

        # 3. Space byte (0x20) and Null byte (0x00)
        space_null_bytes = bytearray([0x20, 0x00])

        # 4. Session Token (each character as its ASCII code)
        token_bytes = bytearray()
        for char in session_token:
            token_bytes.append(ord(char))

        # --- Concatenate all parts ---
        payload = length_bytes + answer_bytes + space_null_bytes + token_bytes

        return payload
    except Exception as e:
        xlog(f"Error during payload construction: {e}")
        return None


def send_captcha_answer_to_server(answer):
    """
       Injects the CAPTCHA answer into the game client.

       Args:
           answer: The numerical answer to the CAPTCHA (e.g., 15). Can be int or str.
    """
    # Generate the payload
    xlog('Sending CAPTCHA answer...')
    payload = create_captcha_answer_payload(answer)

    if payload is None:
        xlog("Error: Failed to generate payload. Aborting injection.")
        return

    # Inject the payload into the game client
    inject_joymax(0x7055, payload, True)

    # resume buy/sell process if paused
    global buy_sell_paused
    buy_sell_paused_for_captcha = False


def update_token_from_payload(payload_input):
    global session_token
    payload_bytes = None

    # --- Input Handling ---
    if isinstance(payload_input, str):
        try:
            clean_hex = payload_input.replace(' ', '')
            payload_bytes = bytes.fromhex(clean_hex)
        except ValueError:
            xlog(f"Error: Input string is not a valid hexadecimal string.")
            return False
    elif isinstance(payload_input, (bytes, bytearray)):
        payload_bytes = payload_input
    else:
        xlog(f"Error: Invalid input type. Expected bytes or hex string, got {type(payload_input)}.")
        return False

    # --- Extract Token ---
    try:
        # The token is the ASCII representation of the hex string (last 32 bytes)
        token_bytes = payload_bytes[-32:]
        token_str = token_bytes.decode('ascii')

        xlog(f"Extracted new token: {token_str}")
        session_token = token_str
        update_token_status()
        return True
    except Exception as e:
        xlog(f"Error during token extraction: {e}")
        return False


def buy_JG_item():
    # (Opcode) 0x7034 (Data) 13 00 00 00 00 00 03 28 00 5C 01 00 00
    data = struct.pack('13B', 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x28, 0x00, 0x5C, 0x01, 0x00, 0x00)
    inject_joymax(0x7034, data, False)


def buy_samarkand_item():
    # (Opcode) 0x7034 (Data) 13 00 00 00 00 00 03 28 00 5C 02 00 00
    data = struct.pack('13B', 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x28, 0x00, 0x5C, 0x02, 0x00, 0x00)
    inject_joymax(0x7034, data, False)

def buy_hotan_item():
    # (Opcode) 0x7034 (Data) 13 00 00 00 00 00 03 28 00 69 03 00 00
    data = struct.pack('13B', 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x28, 0x00, 0x69, 0x03, 0x00, 0x00)
    inject_joymax(0x7034, data, False)

def sell_JG_item_at_index(indexDecimal):
    # [12:47:16] Client: (Opcode) 0x7034 (Data) 14 BD CB 44 00 05 28 00 5C 01 00 00
    # [12:47:16] Client: (Opcode) 0x7034 (Data) 14 BD CB 44 00 06 28 00 5C 01 00 00
    # [12:47:17] Client: (Opcode) 0x7034 (Data) 14 BD CB 44 00 07 28 00 5C 01 00 00
    # [12:47:17] Client: (Opcode) 0x7034 (Data) 14 BD CB 44 00 08 28 00 5C 01 00 00
    # [12:47:18] Client: (Opcode) 0x7034 (Data) 14 BD CB 44 00 09 28 00 5C 01 00 00
    data = struct.pack('12B', 0x14, 0x8D, 0x4D, 0x39, 0x00, indexDecimal, 0x28, 0x00, 0x5C, 0x01, 0x00, 0x00)
    inject_joymax(0x7034, data, False)
    return True

def sell_samarkand_item_at_index(indexDecimal):
    # examples:
    # [23:23:06] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 00 28 00 5C 02 00 00
    # [23:23:06] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 01 28 00 5C 02 00 00
    # [23:23:07] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 02 28 00 5C 02 00 00
    # [23:23:07] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 03 28 00 5C 02 00 00
    # [23:23:07] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 04 28 00 5C 02 00 00
    # [23:23:08] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 05 28 00 5C 02 00 00
    # [23:23:08] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 06 28 00 5C 02 00 00
    # [23:23:08] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 07 28 00 5C 02 00 00
    # [23:23:09] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 08 28 00 5C 02 00 00
    # [23:23:09] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 09 28 00 5C 02 00 00
    # [23:23:10] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 0A 28 00 5C 02 00 00
    # ....
    # [23:24:12] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 9C 28 00 5C 02 00 00
    # [23:24:12] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 9D 28 00 5C 02 00 00
    # [23:24:12] Client: (Opcode) 0x7034 (Data) 14 32 73 E8 01 9E 28 00 5C 02 00 00

    data = struct.pack('12B', 0x14, 0x32, 0x73, 0xE8, 0x01, indexDecimal, 0x28, 0x00, 0x5C, 0x02, 0x00, 0x00)
    inject_joymax(0x7034, data, False)
    return True

def sell_hotan_item_at_intex(indexDecimal):
    # Examples:
    # [23:55:14] Client: (Opcode) 0x7034 (Data) 14 4D 2D A4 00 00 28 00 69 03 00 00
    # [23:55:14] Client: (Opcode) 0x7034 (Data) 14 4D 2D A4 00 01 28 00 69 03 00 00
    data = struct.pack('12B', 0x14, 0x4D, 0x2D, 0xA4, 0x00, indexDecimal, 0x28, 0x00, 0x69, 0x03, 0x00, 0x00)
    inject_joymax(0x7034, data, False)
    return True

def sell_bandit_item_at_index(indexDecimal):
    # Examples:
    # (Opcode) 0x7034 (Data) 14 49 76 47 00 01 28 00 77 01 00 00
    # (Opcode) 0x7034 (Data) 14 49 76 47 00 02 28 00 77 01 00 00
    data = struct.pack('12B', 0x14, 0x49, 0x76, 0x47, 0x00, indexDecimal, 0x28, 0x00, 0x77, 0x01, 0x00, 0x00)
    inject_joymax(0x7034, data, False)
    return True

def decode_captcha_question(payload_input):
    """
      Decodes the data payload from a server CAPTCHA question packet (Opcode 0x5055).

      Args:
          payload_input: The data payload, either as a bytes object or
                         a hexadecimal string.

      Returns:
          str: The decoded CAPTCHA question string.
          None: If decoding fails due to invalid input, format errors,
                or decoding issues.
      """

    payload_bytes = None

    # --- Input Handling ---
    if isinstance(payload_input, str):
        try:
            # Handle space-separated hex string
            clean_hex = payload_input.replace(' ', '')
            payload_bytes = bytes.fromhex(clean_hex)
        except ValueError:
            xlog(f"Error: Input string is not a valid hexadecimal string.")
            return None
    elif isinstance(payload_input, (bytes, bytearray)):
        payload_bytes = payload_input
    else:
        xlog(f"Error: Invalid input type. Expected bytes or hex string, got {type(payload_input)}.")
        return None

    # --- Basic Payload Validation ---
    # Structure: Length(2) + Question String (L bytes)
    # Minimum length is 2 bytes for the length field itself.
    min_expected_length = 2
    if len(payload_bytes) < min_expected_length:
        xlog(f"Error: Payload length ({len(payload_bytes)}) is less than minimum expected ({min_expected_length}).")
        return None

    try:
        # --- Decode Length Field ---
        # '<H' means unsigned short (2 bytes), little-endian
        # We unpack the first 2 bytes. The result is a tuple, so we take the first element [0].
        expected_string_length = struct.unpack('<H', payload_bytes[0:2])[0]

        # --- Extract String Bytes ---
        question_bytes = payload_bytes[2:]
        actual_string_length = len(question_bytes)

        # --- Validate Length Consistency ---
        if actual_string_length != expected_string_length:
            xlog(f"Error: Length mismatch. Header indicates {expected_string_length} bytes, "
                 f"but found {actual_string_length} bytes of string data.")
            return None

        # --- Decode String ---
        # Assume the question is always ASCII based on previous examples
        decoded_question = question_bytes.decode('ascii')

        return decoded_question

    except struct.error as e:
        xlog(f"Error unpacking length field: {e}. Payload might be too short or malformed.")
        return None
    except IndexError:
        # Should be caught by length check, but good practice
        xlog(f"Error accessing payload bytes (IndexError).")
        return None
    except UnicodeDecodeError:
        xlog(f"Error decoding question string as ASCII. Payload might contain non-ASCII characters.")
        return None
    except Exception as e:
        xlog(f"An unexpected error occurred during decoding: {e}")
        return None

def reset(reason):
    global pluginEnabled, session_token
    xlog(f"Plugin disabled due to: {reason}.")
    pluginEnabled = False
    session_token = ""
    QtBind.setChecked(gui, cbxEnabled, pluginEnabled)
    update_token_status()

def disconnected():
    reset('disconnection')

# Plugin loaded
log('Plugin: ' + pName + ' (by ViRUS) v' + pVersion + ' successfully loaded')
loadConfigs()
update_token_status()
