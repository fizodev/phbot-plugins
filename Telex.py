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



pName = 'Telex'
pVersion = '0.3'
#pUrl = 'https://raw.githubusercontent.com/JellyBitz/phBot-xPlugins/master/JellyDix.py'
#video link  https://www.youtube.com/watch?v=LDNRgLq3Tt8
pUrl = 'https://github.com/EzKime/TelexPlugin/blob/main/Telex.py'

'''
pVersion = '0.2' Telegram channel support
pVersion = '0.3' Telegram api requests are set to 3 seconds, fixed issue with adding multiple plugins
'''
# ______________________________ Initializing ______________________________ #

URL_HOST = "https://api.telegram.org/bot" # API server
URL_REQUEST_TIMEOUT = 30 # sec
TELEGRAM_FETCH_DELAY = 5000 # ms

# Globals
character_data = None
party_data = None
update_id = None
chat_data = {}
isOnline = False
hasStall = False

telegram_fetch_counter = 0

# Graphic user interface
gui = QtBind.init(__name__,pName)

QtBind.createLabel(gui,"Telegram Channels ID",6,10)
tbxChannels = QtBind.createLineEdit(gui,"",6,25,80,19)
tbxSeconds = QtBind.createLineEdit(gui,"",6,278,30,19)
QtBind.createLabel(gui,"Write the time difference between your location and London in hours.\nIf it's the same, write 0.\nIf your time is behind, write the difference (e.g., -1).",40,272)
lstChannels = QtBind.createList(gui,6,46,156,90)
btnAddChannel = QtBind.createButton(gui,'btnAddChannel_clicked',"   Add   ",86,25)
btnChatId = QtBind.createButton(gui,'btnChatId_clicked',"   Show Chat ID   ",6,250)
btnRemChannel = QtBind.createButton(gui,'btnRemChannel_clicked',"     Remove     ",45,135)

# Telegram options
QtBind.createLabel(gui,"Token :",6,165)
tbxToken = QtBind.createLineEdit(gui,"",43,163,119,19)

cbxAddTimestamp = QtBind.createCheckBox(gui,'cbxDoNothing','Add phBot timestamp',6,185)
cbxTelegram_interactions = QtBind.createCheckBox(gui,'cbxDoNothing','Use Telegram interactions',6,205)
tbxTelegram_guild_id = QtBind.createLineEdit(gui,'',6,225,145,19)

# Separator line
QtBind.createLineEdit(gui,"",169,10,1,262)

# Triggers
QtBind.createLabel(gui,"Select the Telegram channel to send the notification ( Filters are using regex! )",175,10)
btnSaveConfig = QtBind.createButton(gui,'saveConfigs',"     Save Changes     ",615,4)

# Creating margins to locate all quickly
_x = 180
_y = 30
_Height = 19
_cmbxWidth = 131
_tbxWidth = 118

# login states
QtBind.createLabel(gui,'Joined to the game',_x+_cmbxWidth+4,_y+3)
cmbxEvtChar_joined = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Disconnected from game',_x+_cmbxWidth+4,_y+3)
cmbxEvtChar_disconnected = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20

# uniques
_y += 5
QtBind.createLabel(gui,'Unique spawn',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_uniqueSpawn = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
cbxEvtMessage_uniqueSpawn_filter = QtBind.createCheckBox(gui,'cbxDoNothing','',_x,_y+3)
tbxEvtMessage_uniqueSpawn_filter = QtBind.createLineEdit(gui,"",_x+13,_y,_tbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Unique killed',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_uniqueKilled = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
cbxEvtMessage_uniqueKilled_filter = QtBind.createCheckBox(gui,'cbxDoNothing','',_x,_y+3)
tbxEvtMessage_uniqueKilled_filter = QtBind.createLineEdit(gui,"",_x+13,_y,_tbxWidth,_Height)
_y+=20

# events
_y += 5
QtBind.createLabel(gui,'Capture the Flag',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_ctf = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Battle Arena',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_battlearena = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Fortress War',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_fortress = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Consignment Hunter',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_consignmenthunter = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Consignment Thief',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_consignmentthief = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)

# warnings
_x += _cmbxWidth * 2 + 10
_y = 30
QtBind.createLabel(gui,'GM near to you',_x+_cmbxWidth+4,_y+3)
cmbxEvtNear_gm = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Unique near to you',_x+_cmbxWidth+4,_y+3)
cmbxEvtNear_unique = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Hunter/Trader near',_x+_cmbxWidth+4,_y+3)
cmbxEvtNear_hunter = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Thief near',_x+_cmbxWidth+4,_y+3)
cmbxEvtNear_thief = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Character attacked',_x+_cmbxWidth+4,_y+3)
cmbxEvtChar_attacked = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Character died',_x+_cmbxWidth+4,_y+3)
cmbxEvtChar_died = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Transport/Horse died',_x+_cmbxWidth+4,_y+3)
cmbxEvtPet_died = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20

# misc
_y+=5
QtBind.createLabel(gui,'Quest completed',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_quest = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Alchemy completed',_x+_cmbxWidth+4,_y+3)
cmbxEvtBot_alchemy = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui,'Stall item sold',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_item_sold = QtBind.createCombobox(gui,_x,_y,_cmbxWidth,_Height)
_y+=20

# wrap to iterate
cmbxTriggers={'cmbxEvtChar_joined':cmbxEvtChar_joined,'cmbxEvtChar_disconnected':cmbxEvtChar_disconnected,'cmbxEvtMessage_uniqueSpawn':cmbxEvtMessage_uniqueSpawn,'cmbxEvtMessage_uniqueKilled':cmbxEvtMessage_uniqueKilled,'cmbxEvtMessage_ctf':cmbxEvtMessage_ctf,'cmbxEvtMessage_battlearena':cmbxEvtMessage_battlearena,'cmbxEvtMessage_fortress':cmbxEvtMessage_fortress,'cmbxEvtMessage_consignmenthunter':cmbxEvtMessage_consignmenthunter,'cmbxEvtMessage_consignmentthief':cmbxEvtMessage_consignmentthief,'cmbxEvtNear_gm':cmbxEvtNear_gm,'cmbxEvtNear_unique':cmbxEvtNear_unique,'cmbxEvtNear_hunter':cmbxEvtNear_hunter,'cmbxEvtNear_thief':cmbxEvtNear_thief,'cmbxEvtChar_attacked':cmbxEvtChar_attacked,'cmbxEvtChar_died':cmbxEvtChar_died,'cmbxEvtPet_died':cmbxEvtPet_died,'cmbxEvtMessage_quest':cmbxEvtMessage_quest,'cmbxEvtBot_alchemy':cmbxEvtBot_alchemy,'cmbxEvtMessage_item_sold':cmbxEvtMessage_item_sold}

# Graphic user interface (+)
gui_ = QtBind.init(__name__,pName+"(+)")

# Creating margins to locate columns quickly
_x = 6
_y = 7
_cmbxWidth = 131
_tbxWidth = 118

# chat messages
QtBind.createLabel(gui_,'General',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_all = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Private',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_private = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Stall',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_stall = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Party',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_party = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Academy',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_academy = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Guild',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_guild = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Union',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_union = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Global',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_global = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
cbxEvtMessage_global_filter = QtBind.createCheckBox(gui_,'cbxDoNothing','',_x,_y+3)
tbxEvtMessage_global_filter = QtBind.createLineEdit(gui_,"",_x+13,_y,_tbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Notice',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_notice = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
cbxEvtMessage_notice_filter = QtBind.createCheckBox(gui_,'cbxDoNothing','',_x,_y+3)
tbxEvtMessage_notice_filter = QtBind.createLineEdit(gui_,"",_x+13,_y,_tbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'GM Talk',_x+_cmbxWidth+4,_y+3)
cmbxEvtMessage_gm = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)

# party
_x += int(_cmbxWidth*1.5) 
_y = 7
QtBind.createLabel(gui_,'Party joined',_x+_cmbxWidth+4,_y+3)
cmbxEvtParty_joined = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Party left',_x+_cmbxWidth+4,_y+3)
cmbxEvtParty_left = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Party member joined',_x+_cmbxWidth+4,_y+3)
cmbxEvtParty_memberJoin = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Party member left',_x+_cmbxWidth+4,_y+3)
cmbxEvtParty_memberLeft = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Party member level up',_x+_cmbxWidth+4,_y+3)
cmbxEvtParty_memberLvlUp = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20

# guild
_y+=5
QtBind.createLabel(gui_,'Guild notice changed',_x+_cmbxWidth+4,_y+3)
cmbxEvtGuild_noticechanged = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Guild member login',_x+_cmbxWidth+4,_y+3)
cmbxEvtGuild_memberLogin = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Guild member logout',_x+_cmbxWidth+4,_y+3)
cmbxEvtGuild_memberLogout = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20

# picks
_x += _cmbxWidth * 2 + 10
_y = 7
QtBind.createLabel(gui_,'Item picked up (vSRO)',_x+_cmbxWidth+4,_y+3)
cmbxEvtPick_item = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
cbxEvtPick_name_filter = QtBind.createCheckBox(gui_,'cbxDoNothing','',_x,_y+3)
tbxEvtPick_name_filter = QtBind.createLineEdit(gui_,"",_x+13,_y,_tbxWidth,_Height)
_y+=20
cbxEvtPick_servername_filter = QtBind.createCheckBox(gui_,'cbxDoNothing','',_x,_y+3)
tbxEvtPick_servername_filter = QtBind.createLineEdit(gui_,"",_x+13,_y,_tbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Item (Rare) picked up',_x+_cmbxWidth+4,_y+3)
cmbxEvtPick_rare = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20
QtBind.createLabel(gui_,'Item (Equipable) picked up',_x+_cmbxWidth+4,_y+3)
cmbxEvtPick_equip = QtBind.createCombobox(gui_,_x,_y,_cmbxWidth,_Height)
_y+=20

# wrap to iterate
cmbxTriggers_={'cmbxEvtMessage_all':cmbxEvtMessage_all,'cmbxEvtMessage_private':cmbxEvtMessage_private,'cmbxEvtMessage_stall':cmbxEvtMessage_stall,'cmbxEvtMessage_party':cmbxEvtMessage_party,'cmbxEvtMessage_academy':cmbxEvtMessage_academy,'cmbxEvtMessage_guild':cmbxEvtMessage_guild,'cmbxEvtMessage_union':cmbxEvtMessage_union,'cmbxEvtMessage_global':cmbxEvtMessage_global,'cmbxEvtMessage_notice':cmbxEvtMessage_notice,'cmbxEvtMessage_gm':cmbxEvtMessage_gm,'cmbxEvtParty_joined':cmbxEvtParty_joined,'cmbxEvtParty_left':cmbxEvtParty_left,'cmbxEvtParty_memberJoin':cmbxEvtParty_memberJoin,'cmbxEvtParty_memberLeft':cmbxEvtParty_memberLeft,'cmbxEvtParty_memberLvlUp':cmbxEvtParty_memberLvlUp,'cmbxEvtGuild_noticechanged':cmbxEvtGuild_noticechanged,'cmbxEvtGuild_memberLogin':cmbxEvtGuild_memberLogin,'cmbxEvtGuild_memberLogout':cmbxEvtGuild_memberLogout,'cmbxEvtPick_item':cmbxEvtPick_item,'cmbxEvtPick_rare':cmbxEvtPick_rare,'cmbxEvtPick_equip':cmbxEvtPick_equip}

# ______________________________ Methods ______________________________ #

# Return folder path
def getPath():
	return get_config_dir()+pName+"\\"

# Return character configs path (JSON)
def getConfig():
	return getPath()+character_data['server'] + "_" + character_data['name'] + ".json"

# Load default configs
def loadDefaultConfig():
	# Clear data
	QtBind.setText(gui,tbxChannels,"")
	QtBind.setText(gui,tbxSeconds,"")
	QtBind.clear(gui,lstChannels)

	QtBind.setChecked(gui,cbxAddTimestamp,False)
	QtBind.setChecked(gui,cbxTelegram_interactions,False)
	QtBind.setText(gui,tbxTelegram_guild_id," Telegram Server ID...")

	QtBind.setText(gui,tbxToken,'')
	
	# Reset triggers
	for name,cmbx in cmbxTriggers.items():
		QtBind.clear(gui,cmbx)
		QtBind.append(gui,cmbx,"")

	QtBind.setChecked(gui,cbxEvtMessage_uniqueSpawn_filter,False)
	QtBind.setText(gui,tbxEvtMessage_uniqueSpawn_filter," Filter by name")
	QtBind.setChecked(gui,cbxEvtMessage_uniqueKilled_filter,False)
	QtBind.setText(gui,tbxEvtMessage_uniqueKilled_filter," Filter by name")

	for name,cmbx in cmbxTriggers_.items():
		QtBind.clear(gui_,cmbx)
		QtBind.append(gui_,cmbx,"")

	QtBind.setChecked(gui_,cbxEvtMessage_global_filter,False)
	QtBind.setText(gui_,tbxEvtMessage_global_filter," Filter by message")
	QtBind.setChecked(gui_,cbxEvtMessage_notice_filter,False)
	QtBind.setText(gui_,tbxEvtMessage_notice_filter," Filter by message")

	QtBind.setChecked(gui_,cbxEvtPick_name_filter,False)
	QtBind.setText(gui_,tbxEvtPick_name_filter," Filter by name")
	QtBind.setChecked(gui_,cbxEvtPick_servername_filter,False)
	QtBind.setText(gui_,tbxEvtPick_servername_filter," Filter by servername")

# Save all config
def saveConfigs():
	# Save if data has been loaded
	if isJoined():
		# Save all data
		data = {}
		data["Channels"] = QtBind.getItems(gui,lstChannels)

		data["AddTimeStamp"] = QtBind.isChecked(gui,cbxAddTimestamp)
		data["TelegramInteractions"] = QtBind.isChecked(gui,cbxTelegram_interactions)
		data["TelegramInteractionGuildID"] = QtBind.text(gui,tbxTelegram_guild_id)

		data["Token"] = QtBind.text(gui,tbxToken)
		data["Seconds"] = QtBind.text(gui,tbxSeconds)
		
		# Save triggers from tabs
		triggers = {}
		data["Triggers"] = triggers

		for name,cmbx in cmbxTriggers.items():
			triggers[name] = QtBind.text(gui,cmbx)

		triggers["cbxEvtMessage_uniqueSpawn_filter"] = QtBind.isChecked(gui,cbxEvtMessage_uniqueSpawn_filter)
		triggers["tbxEvtMessage_uniqueSpawn_filter"] = QtBind.text(gui,tbxEvtMessage_uniqueSpawn_filter)
		triggers["cbxEvtMessage_uniqueKilled_filter"] = QtBind.isChecked(gui,cbxEvtMessage_uniqueKilled_filter)
		triggers["tbxEvtMessage_uniqueKilled_filter"] = QtBind.text(gui,tbxEvtMessage_uniqueKilled_filter)

		for name,cmbx in cmbxTriggers_.items():
			triggers[name] = QtBind.text(gui_,cmbx)

		triggers["cbxEvtMessage_global_filter"] = QtBind.isChecked(gui_,cbxEvtMessage_global_filter)
		triggers["tbxEvtMessage_global_filter"] = QtBind.text(gui_,tbxEvtMessage_global_filter)
		triggers["cbxEvtMessage_notice_filter"] = QtBind.isChecked(gui_,cbxEvtMessage_notice_filter)
		triggers["tbxEvtMessage_notice_filter"] = QtBind.text(gui_,tbxEvtMessage_notice_filter)

		triggers["cbxEvtPick_name_filter"] = QtBind.isChecked(gui_,cbxEvtPick_name_filter)
		triggers["tbxEvtPick_name_filter"] = QtBind.text(gui_,tbxEvtPick_name_filter)
		triggers["cbxEvtPick_servername_filter"] = QtBind.isChecked(gui_,cbxEvtPick_servername_filter)
		triggers["tbxEvtPick_servername_filter"] = QtBind.text(gui_,tbxEvtPick_servername_filter)

		# Overrides
		with open(getConfig(),"w") as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))
		log("Plugin: "+pName+" configs has been saved")

# Loads all config previously saved
def loadConfigs():
	loadDefaultConfig()
	if isJoined():

		# Connection status
		global isOnline
		isOnline = True
        
		# Check config exists to load
		if os.path.exists(getConfig()):
			data = {}
			with open(getConfig(),"r") as f:
				data = json.load(f)
			# Load channels
			if "Channels" in data:
				for channel_id in data["Channels"]:
					QtBind.append(gui,lstChannels,channel_id)
					for name,cmbx in cmbxTriggers.items():
						QtBind.append(gui,cmbx,channel_id)
					for name,cmbx in cmbxTriggers_.items():
						QtBind.append(gui_,cmbx,channel_id)

			if "AddTimeStamp" in data and data["AddTimeStamp"]:
				QtBind.setChecked(gui,cbxAddTimestamp,True)
			if "TelegramInteractions" in data and data["TelegramInteractions"]:
				QtBind.setChecked(gui,cbxTelegram_interactions,True)
			if "TelegramInteractionGuildID" in data and data["TelegramInteractionGuildID"]:
				QtBind.setText(gui,tbxTelegram_guild_id,data["TelegramInteractionGuildID"])

			if "Token" in data:
				QtBind.setText(gui,tbxToken,data["Token"])
			if "Seconds" in data:
				QtBind.setText(gui,tbxSeconds,data["Seconds"])

			# Load triggers
			if "Triggers" in data:
				triggers = data["Triggers"]

				if "cmbxEvtChar_joined" in triggers:
					QtBind.setText(gui,cmbxEvtChar_joined,triggers["cmbxEvtChar_joined"])
				if "cmbxEvtChar_disconnected" in triggers:
					QtBind.setText(gui,cmbxEvtChar_disconnected,triggers["cmbxEvtChar_disconnected"])

				if "cmbxEvtMessage_uniqueSpawn" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_uniqueSpawn,triggers["cmbxEvtMessage_uniqueSpawn"])
				if "cbxEvtMessage_uniqueSpawn_filter" in triggers and triggers["cbxEvtMessage_uniqueSpawn_filter"]:
					QtBind.setChecked(gui,cbxEvtMessage_uniqueSpawn_filter,True)
				if "tbxEvtMessage_uniqueSpawn_filter" in triggers and triggers["tbxEvtMessage_uniqueSpawn_filter"]:
					QtBind.setText(gui,tbxEvtMessage_uniqueSpawn_filter,triggers["tbxEvtMessage_uniqueSpawn_filter"])
				if "cmbxEvtMessage_uniqueKilled" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_uniqueKilled,triggers["cmbxEvtMessage_uniqueKilled"])
				if "cbxEvtMessage_uniqueKilled_filter" in triggers and triggers["cbxEvtMessage_uniqueKilled_filter"]:
					QtBind.setChecked(gui,cbxEvtMessage_uniqueKilled_filter,True)
				if "tbxEvtMessage_uniqueKilled_filter" in triggers and triggers["tbxEvtMessage_uniqueKilled_filter"]:
					QtBind.setText(gui,tbxEvtMessage_uniqueKilled_filter,triggers["tbxEvtMessage_uniqueKilled_filter"])

				if "cmbxEvtMessage_battlearena" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_battlearena,triggers["cmbxEvtMessage_battlearena"])
				if "cmbxEvtMessage_ctf" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_ctf,triggers["cmbxEvtMessage_ctf"])
				if "cmbxEvtMessage_fortress" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_fortress,triggers["cmbxEvtMessage_fortress"])
				if "cmbxEvtMessage_consignmenthunter" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_consignmenthunter,triggers["cmbxEvtMessage_consignmenthunter"])
				if "cmbxEvtMessage_consignmentthief" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_consignmentthief,triggers["cmbxEvtMessage_consignmentthief"])

				if "cmbxEvtNear_gm" in triggers:
					QtBind.setText(gui,cmbxEvtNear_gm,triggers["cmbxEvtNear_gm"])
				if "cmbxEvtNear_unique" in triggers:
					QtBind.setText(gui,cmbxEvtNear_unique,triggers["cmbxEvtNear_unique"])
				if "cmbxEvtNear_hunter" in triggers:
					QtBind.setText(gui,cmbxEvtNear_hunter,triggers["cmbxEvtNear_hunter"])
				if "cmbxEvtNear_thief" in triggers:
					QtBind.setText(gui,cmbxEvtNear_thief,triggers["cmbxEvtNear_thief"])
				if "cmbxEvtChar_attacked" in triggers:
					QtBind.setText(gui,cmbxEvtChar_attacked,triggers["cmbxEvtChar_attacked"])
				if "cmbxEvtChar_died" in triggers:
					QtBind.setText(gui,cmbxEvtChar_died,triggers["cmbxEvtChar_died"])
				if "cmbxEvtPet_died" in triggers:
					QtBind.setText(gui,cmbxEvtPet_died,triggers["cmbxEvtPet_died"])

				if "cmbxEvtMessage_quest" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_quest,triggers["cmbxEvtMessage_quest"])
				if "cmbxEvtBot_alchemy" in triggers:
					QtBind.setText(gui,cmbxEvtBot_alchemy,triggers["cmbxEvtBot_alchemy"])
				if "cmbxEvtMessage_item_sold" in triggers:
					QtBind.setText(gui,cmbxEvtMessage_item_sold,triggers["cmbxEvtMessage_item_sold"])

				# (+)
				if "cmbxEvtMessage_all" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_all,triggers["cmbxEvtMessage_all"])
				if "cmbxEvtMessage_private" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_private,triggers["cmbxEvtMessage_private"])
				if "cmbxEvtMessage_stall" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_stall,triggers["cmbxEvtMessage_stall"])
				if "cmbxEvtMessage_party" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_party,triggers["cmbxEvtMessage_party"])
				if "cmbxEvtMessage_academy" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_academy,triggers["cmbxEvtMessage_academy"])
				if "cmbxEvtMessage_guild" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_guild,triggers["cmbxEvtMessage_guild"])
				if "cmbxEvtMessage_union" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_union,triggers["cmbxEvtMessage_union"])
				if "cmbxEvtMessage_global" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_global,triggers["cmbxEvtMessage_global"])
				if "cbxEvtMessage_global_filter" in triggers and triggers["cbxEvtMessage_global_filter"]:
					QtBind.setChecked(gui_,cbxEvtMessage_global_filter,True)
				if "tbxEvtMessage_global_filter" in triggers and triggers["tbxEvtMessage_global_filter"]:
					QtBind.setText(gui_,tbxEvtMessage_global_filter,triggers["tbxEvtMessage_global_filter"])
				if "cmbxEvtMessage_notice" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_notice,triggers["cmbxEvtMessage_notice"])
				if "cbxEvtMessage_notice_filter" in triggers and triggers["cbxEvtMessage_notice_filter"]:
					QtBind.setChecked(gui_,cbxEvtMessage_notice_filter,True)
				if "tbxEvtMessage_notice_filter" in triggers and triggers["tbxEvtMessage_notice_filter"]:
					QtBind.setText(gui_,tbxEvtMessage_notice_filter,triggers["tbxEvtMessage_notice_filter"])
				if "cmbxEvtMessage_gm" in triggers:
					QtBind.setText(gui_,cmbxEvtMessage_gm,triggers["cmbxEvtMessage_gm"])

				if "cmbxEvtParty_joined" in triggers:
					QtBind.setText(gui_,cmbxEvtParty_joined,triggers["cmbxEvtParty_joined"])
				if "cmbxEvtParty_left" in triggers:
					QtBind.setText(gui_,cmbxEvtParty_left,triggers["cmbxEvtParty_left"])
				if "cmbxEvtParty_memberJoin" in triggers:
					QtBind.setText(gui_,cmbxEvtParty_memberJoin,triggers["cmbxEvtParty_memberJoin"])
				if "cmbxEvtParty_memberLeft" in triggers:
					QtBind.setText(gui_,cmbxEvtParty_memberLeft,triggers["cmbxEvtParty_memberLeft"])
				if "cmbxEvtParty_memberLvlUp" in triggers:
					QtBind.setText(gui_,cmbxEvtParty_memberLvlUp,triggers["cmbxEvtParty_memberLvlUp"])

				if "cmbxEvtGuild_noticechanged" in triggers:
					QtBind.setText(gui_,cmbxEvtGuild_noticechanged,triggers["cmbxEvtGuild_noticechanged"])
				if "cmbxEvtGuild_memberLogin" in triggers:
					QtBind.setText(gui_,cmbxEvtGuild_memberLogin,triggers["cmbxEvtGuild_memberLogin"])
				if "cmbxEvtGuild_memberLogout" in triggers:
					QtBind.setText(gui_,cmbxEvtGuild_memberLogout,triggers["cmbxEvtGuild_memberLogout"])

				if "cmbxEvtPick_item" in triggers:
					QtBind.setText(gui_,cmbxEvtPick_item,triggers["cmbxEvtPick_item"])
				if "cbxEvtPick_name_filter" in triggers and triggers["cbxEvtPick_name_filter"]:
					QtBind.setChecked(gui_,cbxEvtPick_name_filter,True)
				if "tbxEvtPick_name_filter" in triggers and triggers["tbxEvtPick_name_filter"]:
					QtBind.setText(gui_,tbxEvtPick_name_filter,triggers["tbxEvtPick_name_filter"])
				if "cbxEvtPick_servername_filter" in triggers and triggers["cbxEvtPick_servername_filter"]:
					QtBind.setChecked(gui_,cbxEvtPick_servername_filter,True)
				if "tbxEvtPick_servername_filter" in triggers and triggers["tbxEvtPick_servername_filter"]:
					QtBind.setText(gui_,tbxEvtPick_servername_filter,triggers["tbxEvtPick_servername_filter"])
				if "cmbxEvtPick_rare" in triggers:
					QtBind.setText(gui_,cmbxEvtPick_rare,triggers["cmbxEvtPick_rare"])
				if "cmbxEvtPick_equip" in triggers:
					QtBind.setText(gui_,cmbxEvtPick_equip,triggers["cmbxEvtPick_equip"])

# Return True if the text exist at the array
def ListContains(list,text):
	text = text.lower()
	for i in range(len(list)):
		if list[i].lower() == text:
			return True
	return False

# Add telegram channel
def btnAddChannel_clicked():
	if character_data:
		channel_id = QtBind.text(gui, tbxChannels)
		if not channel_id:
			return
		if channel_id.lstrip('-').isnumeric():
			if not ListContains(QtBind.getItems(gui, lstChannels), channel_id):
				QtBind.append(gui, lstChannels, channel_id)
				for name, cmbx in cmbxTriggers.items():
					QtBind.append(gui, cmbx, channel_id)
				for name, cmbx in cmbxTriggers_.items():
					QtBind.append(gui_, cmbx, channel_id)
				QtBind.setText(gui, tbxChannels, "")
				log(f'Plugin: Channel added [{channel_id}]')
		else:
			log('Plugin: Error, the Telegram Channel ID must be a valid number (e.g., -100123456789)!')

# Remove telegram channel
def btnRemChannel_clicked():
	if character_data:
		channelItem = QtBind.text(gui,lstChannels)
		# if the list has something selected
		if channelItem:
			# Remove channel from all comboboxes 
			# and leave it as default if is necessary
			for name,cmbx in cmbxTriggers.items():
				channelReset = False
				if QtBind.text(gui,cmbx) == channelItem:
					channelReset = True
				QtBind.remove(gui,cmbx,channelItem)
				if channelReset:
					QtBind.setText(gui,cmbx,"")
			for name,cmbx in cmbxTriggers_.items():
				channelReset = False
				if QtBind.text(gui_,cmbx) == channelItem:
					channelReset = True
				QtBind.remove(gui_,cmbx,channelItem)
				if channelReset:
					QtBind.setText(gui_,cmbx,"")
			# Remove from list
			QtBind.remove(gui,lstChannels,channelItem)
			log('Plugin: Channel removed ['+channelItem+']')

# Create an info package to send through notify
def CreateInfo(t,data):
	info = {}
	info["type"] = t
	info["data"] = data
	info["source"] = 'phBot'
	return info

# Send a notification to telegram channel
# channel_id : ID from channel to be sent
# message : Text shown as telegram notification
# info : Extra data used at server for some notifications
def Notify(channel_id,message,info=None,colour=None):
	# Run this in another thread to avoid locking the client/bot and wait more time for the response
	Timer(0.001,_Notify,(channel_id,message,info,colour)).start()

# Send a notification to Telegram channel
def _Notify(channel_id, message, info=None, colour=None):
    # Check if there is enough data to create a notification
    if not channel_id or not message:
        return
    
    url = URL_HOST
    if not url:
        return    
    token = QtBind.text(gui, tbxToken)
    if not token:
        return    

    # Try to send notification
    try:
        # Add timestamp if option is enabled
        if QtBind.isChecked(gui, cbxAddTimestamp):
            message = "||" + datetime.now().strftime('%H:%M:%S') + "|| " + message
        
        # Create the URL for the Telegram API request
        url = f"{url}{token}/sendMessage"
        
        # Prepare the request data
        data = {
            "chat_id": channel_id,
        }
        
        # Function to send the message in chunks if the length exceeds 4000 characters
        def send_message_chunked(message):
            max_length = 4000  # Maximum message length
            for i in range(0, len(message), max_length):
                data['text'] = message[i:i+max_length]
                
                # Encode the data to be sent with POST
                encoded_data = urllib.parse.urlencode(data).encode("utf-8")
                
                # Create and send the request
                req = urllib.request.Request(url, data=encoded_data)
                with urllib.request.urlopen(req) as response:
                    # Parse the response
                    result = json.loads(response.read().decode("utf-8"))
                
                # Check if the message was sent successfully
                if result.get("ok"):
                    log("Message sent successfully!")
                else:
                    log("An error occurred while sending the message:", result)

        # Send the message in chunks
        send_message_chunked(message)
        
    except Exception as ex:
        log(f"Plugin: Error sending notification - {str(ex)}")

# Fetch messages on telegram (queue) from the guild server indicated
def Fetch(guild_id):
	# Run this in another thread to avoid locking the client/bot and wait more time for the response
	Timer(0.001,_Fetch,(guild_id,)).start()

# Fetch messages on telegram (queue) from the guild server indicated
def _Fetch(guild_id):
    # Check if there is enough data to fetch
    if not guild_id or not guild_id.isnumeric():
        return

    token = QtBind.text(gui, tbxToken)
    url = f"{URL_HOST}{token}/getUpdates"

    try:
        # Prepare the request to Telegram API
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=URL_REQUEST_TIMEOUT) as f:
            try:
                # Parse the response from the server
                resp = json.loads(f.read().decode())

                # API yanıtını kontrol et
                if resp and resp.get("ok") and len(resp.get("result", [])) > 0:
                    # En son gelen mesajı al
                    last_message = resp['result'][-1]
                    on_telegram_fetch(last_message)
                else:
                    log("Plugin: Fetch failed with error from Telegram API.")
            except Exception as ex2:
                log(f"Plugin: Error reading response from Telegram API [{str(ex2)}]")
    except Exception as ex:
        log(f"Plugin: Error loading URL [{str(ex)}] for Telegram Fetch")

# Check if character is ingame
def isJoined():
	global character_data
	character_data = get_character_data()
	if not (character_data and "name" in character_data and character_data["name"]):
		character_data = None
	return character_data

# Get battle arena text by type
def getBattleArenaText(t):
	if t == 0:
		return 'Random'
	if t == 1:
		return 'Party'
	if t == 2:
		return 'Guild'
	if t == 3:
		return 'Job'
	return 'Unknown['+str(t)+']'

# Get Fortress text by id
def getFortressText(code):
	if code == 1:
		return "Jangan"
	if code == 3:
		return "Hotan"
	if code == 6:
		return "Bandit"
	return 'Fortress #'+str(code)

# Get the party list as telegram formatted text
def getPartyTextList(party):
	if not party:
		return ''
	txt = '```\n'
	for joinId, member in party.items():
		# name + padding
		txt += member['name'].ljust(13)
		# lvl. + padding
		txt += (' (Lvl.'+str(member['level'])+')').ljust(10)
		# guild name
		if member['guild']:
			txt += ' ['+member['guild']+']'
		txt += '\n'
	txt += '```'
	return txt

# Get the guild list as telegram formatted text
def getGuildTextList(guild):
	if not guild:
		return ''
	txt = '\n'
	for memberID, member in guild.items():
		if member['online']:
			txt += '\U0001F7E9'.ljust(5)
		else:
			txt += '\U0001F7E5'.ljust(5)
		# name + padding
		txt += member['name'].ljust(8)
		# lvl. + padding
		txt += (' (Lvl.'+str(member['level'])+')')
		txt += '\n'
	return txt
    
def inventory(env):

    # Envanter bilgilerini formatla
    txt = '```\n'
    txt += f"\U0001F4BC : {env['size']}".ljust(25) + f"\U0001F4B0: {env['gold']:,}\n\n"

    for item in env['items']:
        if item:  # Bu kontrol None veya boş olmayanları işler
            # Name + padding
            txt += item['name'].ljust(1)+"-"
            # Quantity + padding
            txt += f"Quantity: {item['quantity']}".ljust(1)+"-"
            # Plus + padding
            txt += f"Plus: {item['plus']}".ljust(10) +"\n\n"

    txt += '```'
    return txt
# Returns the current gold as text
def getGoldText():
	global character_data
	character_data = get_character_data()
	return "{:,}".format(character_data['gold'])

# Return the race type as text, empty if cannot be found
def getRaceText(servername):
	if '_CH_' in servername:
		return '(CH)'
	if '_EU_' in servername:
		return '(EU)'
	return ''

# Return the genre type as text, empty if cannot be found
def getGenreText(servername):
	if '_M_' in servername:
		return '[M]'
	if '_W_' in servername:
		return '[F]'
	return ''

# Return the sox type as text, empty if none is found
def getSoXText(servername,level):
	if level < 101:
		if servername.endswith('A_RARE'):
			return '^Star'
		elif servername.endswith('B_RARE'):
			return '^Moon'
		elif servername.endswith('C_RARE'):
			return '^Sun'
	else:
		if servername.endswith('A_RARE'):
			return '^Nova'
		elif servername.endswith('B_RARE'):
			return '^Rare'
		elif servername.endswith('C_RARE'):
			return '^Legend'
		elif servername.endswith('SET_A'):
			return '^Egy A'
		elif servername.endswith('SET_B'):
			return '^Egy B'
	return ''

# Returns the town name from consignment id
def getConsignmentTownText(code):
	if code == 0:
		return 'Jangan'
	if code == 1:
		return 'Donwhang'
	return 'Town #'+str(code)

# Analyze and extract item information from the index given
def ParseItem(data,index):
	rentID = struct.unpack_from('<I', data, index)[0]
	index += 4 # Rent id
	# TO DO: Parse rentability stuffs
	index += 4 # UnkUInt01
	itemID = struct.unpack_from('<I', data, index)[0]
	index += 4 # Item ID
	itemData = get_item(itemID)
	# IsEquipable
	if itemData['tid1'] == 1:
		index += 1 # plus
		index += 8 # stats
		index += 4 # durability
		count = data[index]
		index += 1 # magic options
		for i in range(count):
			index += 4 # id
			index += 4 # value
		index += 1 # (1)
		count = data[index]
		index += 1 # sockets
		for i in range(count):
			index += 1 # slot
			index += 4 # id
			index += 4 # value
		index += 1 # (2)
		count = data[index]
		index += 1 # adv
		for i in range(count):
			index += 1 # slot
			index += 4 # id
			index += 4 # value
		index += 4 # UnkUint02
	# IsCOS
	elif itemData['tid1'] == 2:
		# IsPet
		if itemData['tid2'] == 1:
			state = data[index]
			index += 1 # state
			if state != 1:
				index += 4 # model
				index += 2 + struct.unpack_from('<H', data, index)[0] # name
				# NeedsTime
				if data['tid3'] == 2:
					index += 4 # endtime
				index += 1 # UnkByte01
		# IsTransform
		elif itemData['tid2'] == 2:
			index += 4 # model
		# IsCube?
		elif itemData['tid2'] == 3:
			index += 4 # quantity
	# IsETC
	elif itemData['tid1'] == 3:
		index += 2 # quantity
		# IsAlchemy
		if itemData['tid2'] == 11:
			# IsStone
			if itemData['tid3'] == 1 or itemData['tid3'] == 2:
				index += 1 # assimilation
		# IsCard
		elif itemData['tid2'] == 14 and itemData['tid3'] == 2:
			count = data[index]
			index += 1 # params
			for i in range(count):
				index += 4 # id
				index += 4 # value
	return index,itemData

# ______________________________ Events ______________________________ #

# Scripting support to send notifications like "Telex,Channel ID,Message"
# Usage example "Telex,010010000110100100100001,This is a script notification"
def Telex(args):
	if len(args) >= 3:
		Notify(args[1],"|`"+character_data['name']+"`| - "+args[2])
	return 0

# Called when the character enters the game world
def joined_game():
	loadConfigs()
	Notify(QtBind.text(gui,cmbxEvtChar_joined),"|`"+character_data['name']+"`| - Joined to the game")

# Called when the character has been disconnected
def disconnected():
	global isOnline
	if isOnline:
		isOnline = False
		channel_id = QtBind.text(gui,cmbxEvtChar_disconnected)
		if channel_id:
			Notify(channel_id,"|`"+character_data['name']+"`| You has been disconnected")

# All chat messages received are sent to this function
def handle_chat(t,player,msg):
	# Check if contains item linking
	itemLink = re.search('([0-9]*)',msg)
	if itemLink:
		global chat_data
		links = itemLink.groups()
		for i in range(len(links)):
			uid = int(links[i])
			if uid in chat_data:
				item = chat_data[uid]
				race = getRaceText(item['servername'])
				genre = getGenreText(item['servername'])
				sox = getSoXText(item['servername'],item['level'])
				msg = msg.replace(''+links[i]+'','`< '+item['name']+(' '+race if race else '')+(' '+genre if genre else '')+(' '+sox if sox else '')+' >`')
			else:
				msg = msg.replace(''+links[i]+'','`< '+links[i]+' >`')
	# Check message type
	if t == 1:
		Notify(QtBind.text(gui_,cmbxEvtMessage_all),"|`"+character_data['name']+"`| - [**General**] from `"+player+"`: "+msg)
	elif t == 2:
		Notify(QtBind.text(gui_,cmbxEvtMessage_private),"|`"+character_data['name']+"`| - [**Private**] from `"+player+"`: "+msg)
	elif t == 9:
		Notify(QtBind.text(gui_,cmbxEvtMessage_stall),"|`"+character_data['name']+"`| - [**Stall**] from `"+player+"`: "+msg)
	elif t == 4:
		Notify(QtBind.text(gui_,cmbxEvtMessage_party),"|`"+character_data['name']+"`| - "+"[**Party**] `"+player+"`: "+msg)
	elif t == 16:
		Notify(QtBind.text(gui_,cmbxEvtMessage_academy),"|`"+character_data['name']+"`| - "+"[**Academy**] `"+player+"`: "+msg)
	elif t == 5:
		Notify(QtBind.text(gui_,cmbxEvtMessage_guild),"[**Guild**] `"+player+"`: "+msg)
	elif t == 11:
		Notify(QtBind.text(gui_,cmbxEvtMessage_union),"[**Union**] `"+player+"`: "+msg)
	elif t == 6:
		if QtBind.isChecked(gui_,cbxEvtMessage_global_filter):
			searchMessage = QtBind.text(gui_,tbxEvtMessage_global_filter)
			if searchMessage:
				try:
					if re.search(searchMessage,msg):
						Notify(QtBind.text(gui_,cmbxEvtMessage_global),"[**Global**] `"+player+"`: "+msg,colour=0xffeb3b)
				except Exception as ex:
					log("Plugin: Error at regex ["+str(ex)+"]")
		else:
			Notify(QtBind.text(gui_,cmbxEvtMessage_global),"[**Global**] `"+player+"`: "+msg,colour=0xffeb3b)
	elif t == 7:
		if QtBind.isChecked(gui_,cbxEvtMessage_notice_filter):
			searchMessage = QtBind.text(gui_,tbxEvtMessage_notice_filter)
			if searchMessage:
				try:
					if re.search(searchMessage,msg):
						Notify(QtBind.text(gui_,cmbxEvtMessage_notice),"[**Notice**] : "+msg)
				except Exception as ex:
					log("Plugin: Error at regex ["+str(ex)+"]")
		else:
			Notify(QtBind.text(gui_,cmbxEvtMessage_notice),"[**Notice**] : "+msg)
	elif t == 3:
		Notify(QtBind.text(gui_,cmbxEvtMessage_gm),"[**GameMaster**] `"+player+"`: "+msg)

# Called for specific events. data field will always be a string.
def handle_event(t, data):
	# Filter events
	if t == 9:
		Notify(QtBind.text(gui,cmbxEvtNear_gm),"|`"+character_data['name']+"`| - **GameMaster** `"+data+"` is near to you!",CreateInfo("position",get_position()))
	elif t == 0:
		Notify(QtBind.text(gui,cmbxEvtNear_unique),"|`"+character_data['name']+"`| - **"+data+"** unique is near to you!",CreateInfo("position",get_position()))
	elif t == 1:
		Notify(QtBind.text(gui,cmbxEvtNear_hunter),"|`"+character_data['name']+"`| - **Hunter/Trader** `"+data+"` is near to you!",CreateInfo("position",get_position()))
	elif t == 2:
		Notify(QtBind.text(gui,cmbxEvtNear_thief),"|`"+character_data['name']+"`| - **Thief** `"+data+"` is near to you!",CreateInfo("position",get_position()))
	elif t == 4:
		Notify(QtBind.text(gui,cmbxEvtChar_attacked),"|`"+character_data['name']+"`| - `"+data+"` is attacking you!",colour=0xFF5722)
	elif t == 7:
		Notify(QtBind.text(gui,cmbxEvtChar_died),"|`"+character_data['name']+"`| - You died",CreateInfo("position",get_position()))
	elif t == 3:
		pet = get_pets()[data]
		Notify(QtBind.text(gui,cmbxEvtPet_died),"|`"+character_data['name']+"`| - Your pet `"+(pet['type'].title())+"` died")
	elif t == 5:
		channel_id = QtBind.text(gui_,cmbxEvtPick_rare)
		if channel_id:
			item = get_item(int(data))
			race = getRaceText(item['servername'])
			genre = getGenreText(item['servername'])
			sox = getSoXText(item['servername'],item['level'])
			Notify(channel_id,"|`"+character_data['name']+"`| - **Item (Rare)** picked up ***"+item['name']+(' '+race if race else '')+(' '+genre if genre else '')+(' '+sox if sox else '')+"***")
	elif t == 6:
		channel_id = QtBind.text(gui_,cmbxEvtPick_equip)
		if channel_id:
			item = get_item(int(data))
			race = getRaceText(item['servername'])
			genre = getGenreText(item['servername'])
			sox = getSoXText(item['servername'],item['level'])
			Notify(channel_id,"|`"+character_data['name']+"`| - **Item (Equipable)** picked up ***"+item['name']+(' '+race if race else '')+(' '+genre if genre else '')+(' '+sox if sox else '')+"***")
	elif t == 8:
		Notify(QtBind.text(gui,cmbxEvtBot_alchemy),"|`"+character_data['name']+"`| - **Auto alchemy** has been completed")

# All packets received from game server will be passed to this function
# Returning True will keep the packet and False will not forward it to the game client
def handle_joymax(opcode, data):
	# globals used in more than one IF statement
	global party_data,hasStall

	# SERVER_NOTICE_UPDATE
	if opcode == 0x300C:
		updateType = data[0]
		if updateType == 5:
			channel_id = QtBind.text(gui,cmbxEvtMessage_uniqueSpawn)
			if channel_id:
				modelID = struct.unpack_from("<I",data,2)[0]
				uniqueName = get_monster(int(modelID))['name']
				if QtBind.isChecked(gui,cbxEvtMessage_uniqueSpawn_filter):
					searchName = QtBind.text(gui,tbxEvtMessage_uniqueSpawn_filter)
					if searchName:
						try:
							if re.search(searchName,uniqueName):
								Notify(channel_id,"**"+uniqueName+"** has appeared",colour=0x9C27B0)
						except Exception as ex:
							log("Plugin: Error at regex ["+str(ex)+"]")
				else:
					Notify(channel_id,"**"+uniqueName+"** has appeared",colour=0x9C27B0)
		elif updateType == 6:
			channel_id = QtBind.text(gui,cmbxEvtMessage_uniqueKilled)
			if channel_id:
				modelID = struct.unpack_from("<I",data,2)[0]
				killerNameLength = struct.unpack_from('<H', data, 6)[0]
				killerName = struct.unpack_from('<' + str(killerNameLength) + 's', data, 8)[0].decode('cp1252')
				uniqueName = get_monster(int(modelID))['name']
				if QtBind.isChecked(gui,cbxEvtMessage_uniqueKilled_filter):
					searchName = QtBind.text(gui,tbxEvtMessage_uniqueKilled_filter)
					if searchName:
						try:
							if re.search(searchName,uniqueName):
								Notify(channel_id,"**"+uniqueName+"** killed by `"+killerName+"`",colour=0x9C27B0)
						except Exception as ex:
							log("Plugin: Error at regex ["+str(ex)+"]")
				else:
					Notify(channel_id,"**"+uniqueName+"** killed by `"+killerName+"`",colour=0x9C27B0)
		elif updateType == 29:
			jobType = data[2]
			if jobType == 1:
				channel_id = QtBind.text(gui,cmbxEvtMessage_consignmenthunter)
				if channel_id:
					progressType = data[3]
					if progressType == 0:
						Notify(channel_id,"[**Consignment**] Hunter trade will start at 10 minutes")
					elif progressType == 1:
						Notify(channel_id,"[**Consignment**] Hunter trade started ("+getConsignmentTownText(data[4])+")")
					elif progressType == 2:
						Notify(channel_id,"[**Consignment**] Hunter trade has ended")
			elif jobType == 2:
				channel_id = QtBind.text(gui,cmbxEvtMessage_consignmentthief)
				if channel_id:
					progressType = data[3]
					if progressType == 0:
						Notify(channel_id,"[**Consignment**] Thief trade will start at 10 minutes")
					elif progressType == 1:
						Notify(channel_id,"[**Consignment**] Thief trade started ("+getConsignmentTownText(data[4])+")")
					elif progressType == 2:
						Notify(channel_id,"[**Consignment**] Thief trade has ended")
	# SERVER_BA_NOTICE
	elif opcode == 0x34D2:
		channel_id = QtBind.text(gui,cmbxEvtMessage_battlearena)
		if channel_id:
			updateType = data[0]
			if updateType == 2:
				Notify(channel_id,"[**Battle Arena**] ("+getBattleArenaText(data[1])+") will start at 10 minutes")
			elif updateType == 13:
				Notify(channel_id,"[**Battle Arena**] ("+getBattleArenaText(data[1])+") will start at 5 minutes")
			elif updateType == 14:
				Notify(channel_id,"[**Battle Arena**] ("+getBattleArenaText(data[1])+") will start at 1 minute")
			elif updateType == 3:
				Notify(channel_id,"[**Battle Arena**] registration period has ended")
			elif updateType == 4:
				Notify(channel_id,"[**Battle Arena**] started")
			elif updateType == 5:
				Notify(channel_id,"[**Battle Arena**] has ended")
	# SERVER_CTF_NOTICE
	elif opcode == 0x34B1:
		channel_id = QtBind.text(gui,cmbxEvtMessage_ctf)
		if channel_id:
			updateType = data[0]
			if updateType == 2:
				Notify(channel_id,"[**Capture the Flag**] will start at 10 minutes")
			elif updateType == 13:
				Notify(channel_id,"[**Capture the Flag**] will start at 5 minutes")
			elif updateType == 14:
				Notify(channel_id,"[**Capture the Flag**] will start at 1 minute")
			elif updateType == 3:
				Notify(channel_id,"[**Capture the Flag**] started")
			elif updateType == 9:
				Notify(channel_id,"[**Capture the Flag**] has ended")
	# SERVER_QUEST_UPDATE
	elif opcode == 0x30D5:
		channel_id = QtBind.text(gui,cmbxEvtMessage_quest)
		if channel_id:
			# Quest update & Quest completed
			if data[0] == 2 and data[10] == 2:
				questID = struct.unpack_from("<I",data,1)[0]
				quest = get_quests()[questID]
				Notify(channel_id,"|`"+character_data['name']+"`| - **Quest** has been completed ***"+quest['name']+"***")
	# SERVER_INVENTORY_ITEM_MOVEMENT
	elif opcode == 0xB034:
		# vSRO filter
		locale = get_locale()
		if locale == 22:
			# Check success
			if data[0] == 1:
				channel_id = QtBind.text(gui_,cmbxEvtPick_item)
				if channel_id:
					# parse
					updateType = data[1]
					if updateType == 6: # Ground
						notify_pickup(channel_id,struct.unpack_from("<I",data,7)[0])
					elif updateType == 17: # Pet
						notify_pickup(channel_id,struct.unpack_from("<I",data,11)[0])
					elif updateType == 28: # Pet (Full/Quest)
						slotInventory = data[6]
						if slotInventory != 254:
							notify_pickup(channel_id,struct.unpack_from("<I",data,11)[0])
	# SERVER_FW_NOTICE
	elif opcode == 0x385F:
		channel_id = QtBind.text(gui,cmbxEvtMessage_fortress)
		if channel_id:
			updateType = data[0]
			if updateType == 1:
				Notify(channel_id,"[**Fortress War**] will start in 30 minutes")
			elif updateType == 2:
				Notify(channel_id,"[**Fortress War**] started")
			elif updateType == 3:
				Notify(channel_id,"[**Fortress War**] has 30 minutes before the end")
			elif updateType == 4:
				Notify(channel_id,"[**Fortress War**] has 20 minutes before the end")
			elif updateType == 5:
				Notify(channel_id,"[**Fortress War**] has 10 minutes before the end")
			elif updateType == 8:
				fortressID = struct.unpack_from("<I",data,1)[0]
				guildNameLength = struct.unpack_from("<H",data,5)[0]
				guildName = data[7:7+guildNameLength].decode('cp1252')
				Notify(channel_id,"[**Fortress War**] "+getFortressText(fortressID)+" has been taken by `"+guildName+"`")
			elif updateType == 9:
				Notify(channel_id,"[**Fortress War**] has 1 minute before the end")
			elif updateType == 6:
				Notify(channel_id,"[**Fortress War**] has ended")
	# SERVER_PARTY_DATA
	elif opcode == 0x3065:
		party_data = get_party()
		channel_id = QtBind.text(gui_,cmbxEvtParty_joined)
		if channel_id:
			Notify(channel_id,"|`"+character_data['name']+"`| You has been joined to the party\n"+getPartyTextList(party_data))
	# SERVER_PARTY_UPDATE
	elif opcode == 0x3864:
		updateType = data[0]
		if updateType == 1:
			Notify(QtBind.text(gui_,cmbxEvtParty_left),"|`"+character_data['name']+"`| You left the party!")
		elif updateType == 2:
			party_data = get_party()
			channel_id = QtBind.text(gui_,cmbxEvtParty_memberJoin)
			if channel_id:
				memberNameLength = struct.unpack_from('<H',data,6)[0]
				memberName = struct.unpack_from('<'+str(memberNameLength)+'s',data,8)[0].decode('cp1252')
				Notify(channel_id,"|`"+character_data['name']+"`| `"+memberName+"` joined to the party\n"+getPartyTextList(party_data))
		elif updateType == 3:
			joinID = struct.unpack_from("<I",data,1)[0]
			memberName = party_data[joinID]['name']
			party_data = get_party()
			if memberName == character_data['name']:
				Notify(QtBind.text(gui_,cmbxEvtParty_left),"|`"+character_data['name']+"`| You left the party")
			else:
				channel_id = QtBind.text(gui_,cmbxEvtParty_memberLeft)
				if channel_id:
					Notify(channel_id,"|`"+character_data['name']+"`| `"+memberName+"` left the party\n"+getPartyTextList(party_data))
		elif updateType == 6: # update member
			if data[5] == 2: # level
				channel_id = QtBind.text(gui_,cmbxEvtParty_memberLvlUp)
				if channel_id:
					joinID = struct.unpack_from("<I",data,1)[0]
					newLevel = data[6]
					oldLevel = party_data[joinID]['level']
					party_data[joinID]['level'] = newLevel
					if oldLevel < newLevel:
						Notify(channel_id,"|`"+character_data['name']+"`| `"+party_data[joinID]['name']+"` level up!\n"+getPartyTextList(party_data))
	# SERVER_STALL_CREATE_RESPONSE
	elif opcode == 0xB0B1:
		if data[0] == 1:
			hasStall = True
	# SERVER_STALL_DESTROY_RESPONSE
	elif opcode == 0xB0B2:
		if data[0] == 1:
			hasStall = False
	# SERVER_STALL_ENTITY_ACTION
	elif opcode == 0x30B7:
		if data[0] == 3 and hasStall:
			channel_id = QtBind.text(gui,cmbxEvtMessage_item_sold)
			if channel_id:
				playerNameLength = struct.unpack_from('<H', data, 2)[0]
				playerName = struct.unpack_from('<' + str(playerNameLength) + 's', data, 4)[0].decode('cp1252')
				Notify(channel_id,"|`"+character_data['name']+"`| `"+playerName+"` bought an item from your stall\n```Your gold now: "+getGoldText()+"```")
	# SERVER_CHAT_ITEM_DATA
	elif opcode == 0xB504:
		global chat_data
		index = 2
		for i in range(data[1]):
			uid = struct.unpack_from('<I', data, index)[0]
			index += 4 # Unique ID
			try:
				index, item = ParseItem(data,index)
				chat_data[uid] = item
			except Exception as ex:
				log('Plugin: Saving error parsing item (Telex)...')
				# Make easy log file for user
				with open(getPath()+"error.log","a") as f:
					f.write("["+str(ex)+"] Server: (Opcode) 0x" + '{:02X}'.format(opcode) + " (Data) "+ ("None" if not data else ' '.join('{:02X}'.format(x) for x in data))+'\r\n')
				break
	# GUILD_INFO_UPDATE
	elif opcode == 0x38F5:
		updateType = data[0]
		if updateType == 6: # member update
			memberID = struct.unpack_from("<I",data,1)[0]
			infoType = data[5]
			if infoType == 2: # session
				if data[6]:
					channel_id = QtBind.text(gui_,cmbxEvtGuild_memberLogout)
					if channel_id:
						member = get_guild()[memberID]
						Notify(channel_id,"|`"+character_data['name']+"`| Guild member `"+member['name']+"` has logged off")
				else:
					channel_id = QtBind.text(gui_,cmbxEvtGuild_memberLogin)
					if channel_id:
						member = get_guild()[memberID]
						# Avoid myself
						if member['name'] != character_data['name']:
							Notify(channel_id,"|`"+character_data['name']+"`|  Guild member `"+member['name']+"` has logged on")
		elif updateType == 5: # general info
			infoType = data[1]
			if infoType == 16: # notice changed
				channel_id = QtBind.text(gui_,cmbxEvtGuild_noticechanged)
				if channel_id:
					index = 2
					titleLength = struct.unpack_from('<H', data, index)[0]
					title = struct.unpack_from('<' + str(titleLength) + 's', data,index+2)[0].decode('cp1252')
					index+=2+titleLength
					textLength = struct.unpack_from('<H', data,index)[0]
					text = struct.unpack_from('<' + str(textLength) + 's', data, index+2)[0].decode('cp1252')
					Notify(channel_id,"|`"+character_data['name']+"`| Guild notice updated : **`"+title+"`**\n"+text)
	return True

# All picked up items are sent to this function (only vSRO working at the moment) 
def notify_pickup(channel_id,itemID):
	item = get_item(itemID)
	# Check filters
	usefilterName = QtBind.isChecked(gui_,cbxEvtPick_name_filter)
	usefilterServerName = QtBind.isChecked(gui_,cbxEvtPick_servername_filter)
	if not usefilterName and not usefilterServerName:
		# No filters activated
		race = getRaceText(item['servername'])
		genre = getGenreText(item['servername'])
		sox = getSoXText(item['servername'],item['level'])
		Notify(channel_id,"|`"+character_data['name']+"`| - **Item** picked up ***"+item['name']+(' '+race if race else '')+(' '+genre if genre else '')+(' '+sox if sox else '')+"***")
		return
	# check filter name
	if usefilterName:
		searchName = QtBind.text(gui_,tbxEvtPick_name_filter)
		if searchName:
			try:
				if re.search(searchName,item['name']):
					# Filtered by Name
					race = getRaceText(item['servername'])
					genre = getGenreText(item['servername'])
					sox = getSoXText(item['servername'],item['level'])
					Notify(channel_id,"|`"+character_data['name']+"`| - **Item (Filtered)** picked up ***"+item['name']+(' '+race if race else '')+(' '+genre if genre else '')+(' '+sox if sox else '')+"***")
					return
			except Exception as ex:
				log("Plugin: Error at regex (name) ["+str(ex)+"]")
	# check filter servername
	if usefilterServerName:
		searchServername = QtBind.text(gui_,tbxEvtPick_servername_filter)
		if searchServername:
			try:
				if re.search(searchServername,item['servername']):
					# Filtered by server name
					race = getRaceText(item['servername'])
					genre = getGenreText(item['servername'])
					sox = getSoXText(item['servername'],item['level'])
					Notify(channel_id,"|`"+character_data['name']+"`| - **Item (Filtered)** picked up ***"+item['name']+(' '+race if race else '')+(' '+genre if genre else '')+(' '+sox if sox else '')+"***")
					return
			except Exception as ex:
				log("Plugin: Error at regex (servername) ["+str(ex)+"]")

def btnChatId_clicked():
    channel_id = QtBind.text(gui, tbxTelegram_guild_id)
    url = URL_HOST  
    token = QtBind.text(gui, tbxToken)
    url = f"{url}{token}/getUpdates"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=URL_REQUEST_TIMEOUT) as response:
            data = json.loads(response.read().decode())

            if data.get('ok') and len(data.get('result', [])) > 0:
                last_update = data['result'][-1]

                message = last_update.get('message') or last_update.get('channel_post')

                if message:
                    message_text = message.get('text', '').lower()
                    chat_id = message['chat'].get('id')
                    channelName = message['chat'].get('title')

                    if message_text == "/chatid":
                        if channelName != None:
                            log(f"{channelName}: {chat_id}")
                        else:
                            log(f"Bot chatId: {chat_id}")
                    else:
                        log("The last message is not /chatid.")
                else:
                    log("No message or channel post found.")
            else:
                log("No new messages or no data received.")
    except Exception as ex:
        log(f"Error: {ex}")

# Called every 500ms
last_fetch_time = 0
FETCH_INTERVAL = 3

def event_loop():
    global last_fetch_time
    
    if character_data:
        current_time = time.time()

        if current_time - last_fetch_time >= FETCH_INTERVAL:
            last_fetch_time = current_time
            if QtBind.isChecked(gui, cbxTelegram_interactions):
                Fetch(QtBind.text(gui, tbxTelegram_guild_id))

# Called everytime telegram has been fetch
def on_telegram_fetch(data):
    if not data:
        return
    global update_id
    hours = int(QtBind.text(gui, tbxSeconds))
    seconds = hours * 60 * 60
    channel_id = QtBind.text(gui, tbxTelegram_guild_id)
    mesajId = data.get('update_id')

    try:
        message = data.get('message')
        if not message:
            return

        telegram_timestamp = message['date'] + seconds
        telegramTime = datetime.utcfromtimestamp(telegram_timestamp)

        pcTime = datetime.now()
        time_difference = pcTime - telegramTime
        time_difference_seconds = time_difference.total_seconds()

        if time_difference_seconds <= 10 and (update_id is None or mesajId > update_id):
            update_id = mesajId
            text = message.get('text', '')
            on_telegram_message(text, channel_id)
    except Exception as ex:
        log(f"Plugin: Error processing fetched message [{str(ex)}]")


# Called everytime a telegram message is sent to bot
def on_telegram_message(msg, channel_id):
    msgLower = msg.lower()
    msgLower = msgLower[1:].rstrip()
    if msgLower == 'position':
        p = get_position()
        Notify(channel_id, '|`' + character_data['name'] + '`| - Your actual position is\n \U0001F4CD  X:%.1f, Y:%.1f,\n  \U0001F30D Region:%d' % (p['x'], p['y'], p['region']), CreateInfo('position', p))
    elif msgLower == 'party':
        party = get_party()
        if party:
            Notify(channel_id, '|`' + character_data['name'] + '`| - Your party members are :\n' + getPartyTextList(party))
        else:
            Notify(channel_id, '|`' + character_data['name'] + '`| - You are not in party!')
    elif msgLower == 'guild':
        guild = get_guild()
        if guild:
            Notify(channel_id, '|`'+ character_data['name'] + '`Guild list `' + character_data['guild'] + '` are :\n' + getGuildTextList(guild))
        else:
            Notify(channel_id, '|`' + character_data['name'] + '`| - You are not in a guild!') 		    		
    elif msgLower == 'inventory':
        env = get_inventory()
        if env:
            Notify(channel_id, '|`' + inventory(env) + '`')
    # elif msgLower == 'storage':
        # env = get_storage()
        # if env:
            # Notify(channel_id, '|`' + inventory(env) + '`')
    # elif msgLower == 'gstorage':
        # env = get_guild_storage()
        # if env:
            # Notify(channel_id, '|`' + inventory(env) + '`')

    elif msgLower == 'exp':
        data = get_character_data()
        percentExp = data['current_exp'] * 100 / data['max_exp'] 
        Notify(channel_id, '|`' + character_data['name'] + '`| - Your current exp is %.2f' % percentExp)
    elif msgLower == 'online':
        in_Game = isOnline
        yes = '\u2705'
        no = '\u274C'
        if in_Game:
            Notify(channel_id, f'{character_data["name"]} is in the game {yes}')
        else:
            Notify(channel_id, f'{character_data["name"]} is not in the game {no}')



if not os.path.exists(getPath()):
	# Creating configs folder
	os.makedirs(getPath())
	log('Plugin: '+pName+' folder has been created')
# Adding RELOAD plugin support
loadConfigs()

# Plugin loaded
log('Plugin: '+pName+' v'+pVersion+' successfully loaded')
