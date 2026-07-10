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

pName = 'vAutoFkThief'
pVersion = '1.0.0'

received_captcha_op_code = 0x5055
answer_captcha_op_code = 0x7055

buy_sell_stopped = False

# Initialize GUI
gui = QtBind.init(__name__, pName)
lblInfo = QtBind.createLabel(gui,
                             'Welcome to vAutoFkThief plugin, It\'s simple, they can\'t sell 39 goods stacks, '
                             '\nand that\'s what are going to give them xD\n' +
                             'Answer the math question, then click buy here to start buying goods.\n'
                             '\n\nDeveloped by *** (Legion Online | Guild ***)',
                             6, 10)

btnBuyJG = QtBind.createButton(gui, 'btnBuyJG_clicked', 'Start Buy JG', 6, 130)
btnBuyDW = QtBind.createButton(gui, 'btnBuyDW_clicked', 'Start Buy DW', 120, 130)
btnBuyHT = QtBind.createButton(gui, 'btnBuyHT_clicked', 'Start Buy HT', 236, 130)
btnBuySMK = QtBind.createButton(gui, 'btnBuySMK_clicked', 'Start Buy SMK', 6, 190)
btnBuyConst = QtBind.createButton(gui, 'btnBuyConst_clicked', 'Start Buy Const', 120, 190)
btnBuyMaze = QtBind.createButton(gui, 'btnBuyMaze_clicked', 'Start Buy Maze', 236, 190)

btnBuyAlx = QtBind.createButton(gui, 'btnBuyAlx_clicked', 'Start Buy Alex', 6, 240)

btnStopBuy = QtBind.createButton(gui, 'btnStopBuy_clicked', 'Stop Buying Goods', 236, 240)


# centralized logger
def xlog(message):
    log('Plugin (vAutoFkThief): ' + message)

def btnBuyJG_clicked():
    xlog("Button clicked: Start Buy JG")
    def start_jg_buy():
        start_buy_goods('JG')

    Timer(1.5, start_jg_buy).start()

def btnBuyDW_clicked():
    xlog("Button clicked: Start Buy DW")
    def start_dw_buy():
        start_buy_goods('DW')
    Timer(1.5, start_dw_buy).start()

def btnBuyHT_clicked():
    xlog("Button clicked: Start Buy HT")
    def start_ht_buy():
        start_buy_goods('HT')
    Timer(1.5, start_ht_buy).start()

def btnBuySMK_clicked():
    xlog("Button clicked: Start Buy SMK")
    def start_smk_buy():
        start_buy_goods('SMK')
    Timer(1.5, start_smk_buy).start()

def btnBuyConst_clicked():
    xlog("Button clicked: Start Buy Const")
    def start_const_buy():
        start_buy_goods('Const')
    Timer(1.5, start_const_buy).start()

def btnBuyMaze_clicked():
    xlog("Button clicked: Start Buy Maze")
    def start_maze_buy():
        start_buy_goods('Maze')
    Timer(1.5, start_maze_buy).start()

def btnBuyAlx_clicked():
    xlog("Button clicked: Start Buy Alex")
    def start_alx_buy():
        start_buy_goods('Alex')
    Timer(1.5, start_alx_buy).start()

def btnStopBuy_clicked():
    global buy_sell_stopped
    xlog("Button clicked: Stop Buying Goods")
    buy_sell_stopped = True

def start_buy_goods(town_code):
    xlog("Starting to buy goods...")

    # Maximum number of attempts to avoid infinite loops
    max_attempts = 250
    attempts = 0

    sleep(1.0)
    global buy_sell_stopped
    while attempts < max_attempts and not buy_sell_stopped:
        # Check if transport pet is full
        pet_status = is_trans_pet_full()

        # If pet_status is None, it means no transport pet was found
        if pet_status is None:
            xlog("Error: No transport pet found. Stopping purchase process.")
            return False

        # If pet is full, we're done
        if pet_status is True:
            xlog("Transport pet inventory is full. Stopping purchase process.")
            return True

        if not buy_sell_stopped:
            buy_item_by_town(town_code_to_item_packet(town_code))

        # Add a small random delay between purchases
        delay = generate_random_delay(0.3, 0.5)
        ## add to seconds to the delay if this is the first buy to give time to solve captcha
        if attempts == 0:
            delay += 1.5
        sleep(delay)

        attempts += 1

    xlog(f"Reached maximum attempts ({max_attempts}) or stopped by user.")
    return False

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
    if opcode == received_captcha_op_code:
        global buy_sell_stopped
        buy_sell_stopped = True

    return True

def handle_silkroad(opcode, data):
    if opcode == answer_captcha_op_code:
        global buy_sell_stopped
        buy_sell_stopped = False

    return True


def buy_item_by_town(itemPacket):
    data = struct.pack('13B', 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x27, 0x00, itemPacket[0], itemPacket[1], itemPacket[2], itemPacket[3])
    inject_joymax(0x7034, data, False)

def town_code_to_item_packet(town_code):
    if town_code == 'JG':
        return [0x5C, 0x01, 0x00, 0x00]
    elif town_code == 'DW':
        return [0x1E, 0x00, 0x00, 0x00]
    elif town_code == 'HT':
        return [0x69, 0x03, 0x00, 0x00]
    elif town_code == 'SMK':
        return [0x5C, 0x02, 0x00, 0x00]
    elif town_code == 'Const':
        return [0x3D, 0x01, 0x00, 0x00]
    elif town_code == 'Maze':
        return [0x32, 0x00, 0x00, 0x00]
    elif town_code == 'Alex':
        return [0x9B, 0x04, 0x00, 0x00]
    else:
        xlog(f"Unknown town code: {town_code}")
        return None

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

def disconnected():
    global buy_sell_stopped
    buy_sell_stopped = True

# Plugin loaded
log('Plugin: ' + pName + ' (by ***) v' + pVersion + ' successfully loaded')
