from phBot import *
import struct
import binascii
import QtBind
from time import sleep
from threading import Timer
import json
import os
import random

pName = 'vLegionAuto20kGoods'
pVersion = '1.0.1'
pUrl = ''

# ==============================================================================
# Global Variable for Session Token
# ==============================================================================
# IMPORTANT: This token is session-specific and CHANGES every time you restart
# the game or potentially after a certain period.
# You MUST update this variable with the CURRENT valid token for your session
session_token = ""
# ==============================================================================


# Initialize GUI
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui,
                             'Welcome to vLegionAuto20kGoods plugin, it\'s a simple plugin to finish the 20k goods AP quest.\n' +
                             'It will buy and sell the goods and solve captcha automatically.\n' +
                             'Please make sure to have the session token captured by answering the captcha yourself manually for the first time.\n' +
                             'You will see in the logs \'Extracted new token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx\''
                             '\n\nDeveloped by ViRUS (Legion Online | Shadows <3)',
                             6, 10)

# Create the enable/disable checkbox
cbxEnabled = QtBind.createCheckBox(gui, 'cbxEnabled_checked', 'Enable plugin', 6, 130)
# Create Start and Stop buttons for buy/sell loop
btnStartLoop = QtBind.createButton(gui, 'btnStartLoop_clicked', 'Start Buy/Sell Loop', 6, 160)
btnStopLoop = QtBind.createButton(gui, 'btnStopLoop_clicked', 'Stop Buy/Sell Loop', 150, 160)
# Add this after the other GUI elements are created
lblLoopStatus = QtBind.createLabel(gui, 'Loop Status: Disabled', 6, 200)
lblOperationStatus = QtBind.createLabel(gui, 'Next Operation: Buy', 150, 200)
lblTokenStatus = QtBind.createLabel(gui, 'Session Token: Not Available', 6, 230)

pluginEnabled = False
buy_sell_loop_enabled = False
buy_sell_state = False  # True = buy, False = sell

# OP Codes for captcha related operations (using integers instead of hex strings)
answer_captcha_op_code = 0x7055
received_captcha_op_code = 0x5055


# centralized logger
def xlog(message):
    log('Plugin (vLegionAuto20kGoods): ' + message)


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


def btnStartLoop_clicked():
    global buy_sell_loop_enabled, buy_sell_state
    if not pluginEnabled:
        xlog("Plugin is not enabled. Please enable it first.")
        return

    buy_sell_loop_enabled = True
    buy_sell_state = False  # Start with sell
    xlog("Buy/Sell loop started!")
    update_status_labels()  # Update labels
    toggle_buy_sell()  # Start the loop


def btnStopLoop_clicked():
    global buy_sell_loop_enabled
    buy_sell_loop_enabled = False
    xlog("Buy/Sell loop stopped!")
    update_status_labels()  # Update labels


def update_token_status():
    """Updates the token status label and enables/disables buttons based on token availability"""
    global lblTokenStatus, session_token

    # Check if token is valid
    token_valid = isinstance(session_token, str) and len(session_token) == 32

    # Update token status label
    status_text = "Session Token: Available" if token_valid else "Session Token: Not Available"
    QtBind.setText(gui, lblTokenStatus, status_text)

    # Enable/disable buttons based on token availability
    QtBind.setEnabled(gui, btnStartLoop, token_valid and pluginEnabled)
    QtBind.setEnabled(gui, btnStopLoop, token_valid and pluginEnabled)


def toggle_buy_sell():
    global buy_sell_state, buy_sell_loop_enabled

    if not buy_sell_loop_enabled:
        return

    if buy_sell_state:  # True = buy, False = sell
        buy_item()
        buy_sell_state = False
    else:
        sell_item()
        buy_sell_state = True

    update_status_labels()  # Update labels

    random_delay = generate_random_delay(1.0, 1.5)
    Timer(random_delay, toggle_buy_sell).start()


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
        if opcode == received_captcha_op_code:
            global buy_sell_loop_enabled
            if not buy_sell_loop_enabled:
                xlog("Received CAPTCHA, but buy/sell loop is already stopped.")
                return True
            xlog("Received CAPTCHA, stopping buy/sell loop.")
            buy_sell_loop_enabled = False
            handle_captcha_question(data)

    return True


def handle_captcha_question(data):
    decoded_question = decode_captcha_question(data)

    if decoded_question is None:
        xlog("Error: Failed to decode CAPTCHA question.")
        return

    captcha_answer = solve_captcha_question(decoded_question)

    if captcha_answer is None:
        xlog("Error: Failed to solve CAPTCHA question.")
        return

    xlog(f"CAPTCHA question: {decoded_question} - Answer: {captcha_answer}")

    def helper_send_captcha_answer_to_server():
        send_captcha_answer_to_server(captcha_answer)

    # Send the answer to the server after a short delay
    random_delay = generate_random_delay(1.0, 1.5)
    Timer(random_delay, helper_send_captcha_answer_to_server).start()

    random_delay_2 = generate_random_delay(2.0, 2.5)
    Timer(random_delay_2, resume_buy_sell_loop).start()


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
    if pluginEnabled:
        if opcode == answer_captcha_op_code:
            update_token_from_payload(data)  # Pass the raw bytearray

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


def resume_buy_sell_loop():
    xlog('Resuming buy/sell loop...')
    global buy_sell_loop_enabled
    buy_sell_loop_enabled = True
    btnStartLoop_clicked()


def buy_item():
    # (Opcode) 0x7034 (Data) 13 00 00 00 00 00 03 28 00 5C 01 00 00
    # (Opcode) 0x7034 (Data) 13 00 00 00 00 00 03 28 00 5C 01 00 00
    xlog('Buying item...')
    data = struct.pack('13B', 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x28, 0x00, 0x5C, 0x01, 0x00, 0x00)
    inject_joymax(0x7034, data, False)


def sell_item():
    # (Opcode) 0x7034 (Data) 14 1A 40 35 00 00 28 00 5C 01 00 00
    # (Opcode) 0x7034 (Data) 14 ED 41 2E 00 00 28 00 5C 01 00 00
    xlog('Selling item...')
    data = struct.pack('12B', 0x14, 0x1A, 0x40, 0x35, 0x00, 0x00, 0x28, 0x00, 0x5C, 0x01, 0x00, 0x00)
    inject_joymax(0x7034, data, False)


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


def update_status_labels():
    global lblLoopStatus, lblOperationStatus

    # Update loop status label
    loop_status = "Enabled" if buy_sell_loop_enabled else "Disabled"
    QtBind.setText(gui, lblLoopStatus, f"Loop Status: {loop_status}")

    # Update operation status label
    operation = "Buy" if buy_sell_state else "Sell"
    QtBind.setText(gui, lblOperationStatus, f"Next Operation: {operation}")


def disconnected():
    global pluginEnabled, buy_sell_loop_enabled, session_token
    xlog("Plugin disabled due to disconnection.")
    pluginEnabled = False
    buy_sell_loop_enabled = False
    session_token = ""
    QtBind.setChecked(gui, cbxEnabled, pluginEnabled)
    update_status_labels()
    update_token_status()


# Plugin loaded
log('Plugin: ' + pName + ' (by ViRUS) v' + pVersion + ' successfully loaded')
loadConfigs()
update_status_labels()
update_token_status()
