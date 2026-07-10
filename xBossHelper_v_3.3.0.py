from phBot import *
import phBotChat
import QtBind
 
pName = 'xBossHelper'
pVersion = '3.3.0'
pUrl = ''

# GUI
gui = QtBind.init(__name__,pName)
QtBind.createLabel(gui,'● xBossHelper V'+pVersion+' \n● Edit by ❴ BossGame / Amr Mansour ❵ ✌\n● StaySrong family ♡ / LegionSRO ☺',525,270)
QtBind.createLabel(gui,'you dont need to write command on chat \n just click buttons using xBossHelper \n-(Party) mean command will send in party \n-(All) mean command will send in General \n-Lead Trace mean all trace on who leader \n-Lead Follow mean all follow on who leader \n Make Sure to have \n xBossControl v.3.0.0 Plugin Installed   ',515,165)
y = 5
 
# Add a ComboBox for commands
commands = ['S', 'SP', 'T', 'N', 'F', 'NF', 'M', 'D', 'MT', 'DS', 'R', 'Z', 'GO', 'GETPOS', 'DC', 'MN', 'TN', 'JUMP', 'SIT']
cb_commands = QtBind.createCombobox(gui, 2, y, 70, 18)
for cmd in commands:
    item = QtBind.append(gui, cb_commands, cmd)
 
y += 0
 
# Mount type combobox
mount_types = ['fellow', 'horse', 'pick', 'transport', 'wolf']
cb_mount_types = QtBind.createCombobox(gui, 2, y+60, 130, 18)
for mount_type in mount_types:
    QtBind.append(gui, cb_mount_types, mount_type)
 
# Cape type combobox
cape_types = ['off','red', 'gray', 'blue', 'white', 'yellow']
cb_cape = QtBind.createCombobox(gui, 2, y+200, 130, 18)
for cape_type in cape_types:
    QtBind.append(gui, cb_cape, cape_type)
 
# Reverse combobox
reverse_types = ['return', 'death', 'player', 'zone']
cb_reverse_types = QtBind.createCombobox(gui, 2, y+260, 57, 18)
for reverse_type in reverse_types:
    QtBind.append(gui, cb_reverse_types, reverse_type)
 
# TextBox Group 1
tb_trace = QtBind.createLineEdit(gui, "#Player Name", 2, y+20, 130, 18)
tb_tp1 = QtBind.createLineEdit(gui, "#A", 2, y+100, 60, 18)
tb_tp2 = QtBind.createLineEdit(gui, "#B", 70, y+100, 60, 18)
tb_moveon = QtBind.createLineEdit(gui, "#Radius", 2, y+80, 130, 18)
tb_radius = QtBind.createLineEdit(gui, "#Radius", 2, y+120, 130, 18)
tb_setscript = QtBind.createLineEdit(gui, "#Path", 2, y+140, 130, 18)
tb_setarea = QtBind.createLineEdit(gui, "#Name", 2, y+160, 130, 18)
tb_profile = QtBind.createLineEdit(gui, "#Name", 2, y+180, 130, 18)
 
# Seperate Line
QtBind.createLineEdit(gui,"",310,10,1,300)
QtBind.createLineEdit(gui,"",500,10,1,220)
 
# TextBox Group 2
tb_follow1 = QtBind.createLineEdit(gui, "#Player", 2, y+40, 60, 18)
tb_follow2 = QtBind.createLineEdit(gui, "#Distance", 70, y+40, 60, 18)
tb_equip = QtBind.createLineEdit(gui, "#ItemName ", 2, y+220, 130, 18)
tb_unequip = QtBind.createLineEdit(gui, "#ItemName ", 2, y+240, 130, 18)
tb_reverse = QtBind.createLineEdit(gui, "#Player/Zone", 62, y+260, 70, 18)
tb_use = QtBind.createLineEdit(gui, "#ItemName ", 2, y+280, 130, 18)
tb_opcode = QtBind.createLineEdit(gui, "#Opcode ", 315, y+260, 100, 18)
tb_data = QtBind.createLineEdit(gui, "#Data ", 315, y+280, 100, 18)

# Button 1
QtBind.createButton(gui, 'send_command_party_clicked', " Send Command (Party) ", 75, y)
QtBind.createButton(gui, 'send_command_All_clicked', " Send Command (All) ", 200, y)
QtBind.createButton(gui, 'send_command_party_trace_clicked'     , "    Trace (Party)    ", 140, y+20)
QtBind.createButton(gui, 'send_command_All_trace_clicked'     , "    Trace (All)    ", 230, y+20)
QtBind.createButton(gui, 'send_command_party_follow_clicked'    , "   Follow (Party)    ", 140, y+40)
QtBind.createButton(gui, 'send_command_All_follow_clicked'    , "   Follow (All)    ", 230, y+40)
QtBind.createButton(gui, 'send_command_party_tp_clicked'        , "      TP (Party)      ", 140, y+100)
QtBind.createButton(gui, 'send_command_All_tp_clicked'        , "      TP (All)      ", 230, y+100)
QtBind.createButton(gui, 'send_command_party_moveon_clicked'    , "  MoveOn (Party) ", 140, y+80)
QtBind.createButton(gui, 'send_command_All_moveon_clicked'    , "  MoveOn (All) ", 230, y+80)
QtBind.createButton(gui, 'send_command_party_mount_clicked'     , "    Mount (Party)   ", 140, y+60)
QtBind.createButton(gui, 'send_command_All_mount_clicked'     , "    Mount (All)   ", 230, y+60)
QtBind.createButton(gui, 'send_command_party_setradius_clicked' , "SetRadius (Party)", 140, y+120)
QtBind.createButton(gui, 'send_command_All_setradius_clicked' , "SetRadius (All)", 230, y+120)
QtBind.createButton(gui, 'send_command_party_setscript_clicked' , " SetScript (Party) ", 140, y+140)
QtBind.createButton(gui, 'send_command_All_setscript_clicked' , " SetScript (All) ", 230, y+140)
QtBind.createButton(gui, 'send_command_party_setarea_clicked'   , "  SetArea (Party) ", 140, y+160)
QtBind.createButton(gui, 'send_command_All_setarea_clicked'   , "  SetArea (All) ", 230, y+160)
QtBind.createButton(gui, 'send_command_party_profile_clicked'   , "    Profile (Party)  ", 140, y+180)
QtBind.createButton(gui, 'send_command_All_profile_clicked'   , "    Profile (All)  ", 230, y+180)
QtBind.createButton(gui, 'send_command_party_cape_clicked'    , "    Cape (Party)    ", 140, y+200)
QtBind.createButton(gui, 'send_command_All_cape_clicked'    , "    Cape (All)    ", 230, y+200)
QtBind.createButton(gui, 'send_command_party_equip_clicked'    , "   EQUIP (Party)   ", 140, y+220)
QtBind.createButton(gui, 'send_command_All_equip_clicked'    , "   EQUIP (All)   ", 230, y+220)
QtBind.createButton(gui, 'send_command_party_unequip_clicked' , " UNEQUIP (Party) ", 140, y+240)
QtBind.createButton(gui, 'send_command_All_unequip_clicked' , " UNEQUIP (All) ", 230, y+240)
QtBind.createButton(gui, 'send_command_party_reverse_clicked' , " REVERSE (Party) ", 140, y+260)
QtBind.createButton(gui, 'send_command_All_reverse_clicked' , " REVERSE (All) ", 230, y+260)
QtBind.createButton(gui, 'send_command_party_use_clicked' , " USE ITEM (Party) ", 140, y+280)
QtBind.createButton(gui, 'send_command_All_use_clicked' , " USE ITEM (All) ", 230, y+280)
 
# Button 2
QtBind.createButton(gui, 'send_command_start_party_clicked'  , " Start (Party) ", 315, y)
QtBind.createButton(gui, 'send_command_start_All_clicked'  , " Start (All) ", 415, y)
QtBind.createButton(gui, 'send_command_stop_party_clicked'  , " Stop (Party) ", 315, y+20)
QtBind.createButton(gui, 'send_command_stop_All_clicked'  , " Stop (All) ", 415, y+20)
QtBind.createButton(gui, 'send_command_leader_trace_party_clicked'  , "Lead Trace (Party)", 315, y+40)
QtBind.createButton(gui, 'send_command_leader_trace_All_clicked'  , "Lead Trace (All)", 415, y+40)
QtBind.createButton(gui, 'send_command_no_trace_party_clicked'  , " No Trace (Party) ", 315, y+60)
QtBind.createButton(gui, 'send_command_no_trace_All_clicked'  , "No Trace (All) ", 415, y+60)
QtBind.createButton(gui, 'send_command_leader_follow_party_clicked' , "Lead Follow (Party)", 315, y+80)
QtBind.createButton(gui, 'send_command_leader_follow_All_clicked' , "Lead Follow (All)", 415, y+80)
QtBind.createButton(gui, 'send_command_no_follow_party_clicked' , " No Follow (Party) ", 315, y+100)
QtBind.createButton(gui, 'send_command_no_follow_All_clicked' , " No Follow (All) ", 415, y+100)
QtBind.createButton(gui, 'send_command_GETPOS_party_clicked' , " Get Position (Party) ", 315, y+120)
QtBind.createButton(gui, 'send_command_GETPOS_All_clicked' , " Get Position (All) ", 415, y+120)
QtBind.createButton(gui, 'send_command_Devil_party_clicked' , " Devil skill (Party) ", 315, y+140)
QtBind.createButton(gui, 'send_command_Devil_All_clicked' , " Devil skill (All) ", 415, y+140)
QtBind.createButton(gui, 'send_command_Angle_party_clicked' , " Angle skill (Party) ", 315, y+160)
QtBind.createButton(gui, 'send_command_Angle_All_clicked' , " Angle skill (All) ", 415, y+160)
QtBind.createButton(gui, 'send_command_Hero_party_clicked' , " Hero skill (Party) ", 315, y+180)
QtBind.createButton(gui, 'send_command_Hero_All_clicked' , " Hero skill (All) ", 415, y+180)
QtBind.createButton(gui, 'send_command_party_sit_clicked'  , " SIT (Party) ", 315, y+200)
QtBind.createButton(gui, 'send_command_All_sit_clicked'  , " SIT (All) ", 415, y+200)
QtBind.createButton(gui, 'send_command_party_jump_clicked'  , " JUMP (Party) ", 315, y+220)
QtBind.createButton(gui, 'send_command_All_jump_clicked'  , " JUMP (All) ", 415, y+220)
QtBind.createButton(gui, 'send_command_party_zerk_clicked'  , " Zerk (Party) ", 315, y+240)
QtBind.createButton(gui, 'send_command_All_zerk_clicked'  , " Zerk (All) ", 415, y+240)
QtBind.createButton(gui, 'send_command_INJECT_party_clicked' , " INJECT (Party) ", 420, y+260)
QtBind.createButton(gui, 'send_command_INJECT_All_clicked' , " INJECT (All) ", 420, y+280)

# Button 3
QtBind.createButton(gui, 'ues_dino_Party_clicked'    , "   Dino (Party)    ", 505, y)
QtBind.createButton(gui, 'ues_dino_All_clicked'    , "   Dino (All)    ", 605, y)
QtBind.createButton(gui, 'ues_dark_Party_clicked'    , "   Dark (Party)    ", 505, y+20)
QtBind.createButton(gui, 'ues_dark_All_clicked'    , "   Dark (All)    ", 605, y+20)
QtBind.createButton(gui, 'send_command_party_M_mount_clicked'     , " Mount M (Party) ", 505, y+40)
QtBind.createButton(gui, 'send_command_All_M_mount_clicked'     , " Mount M (All) ", 605, y+40)
QtBind.createButton(gui, 'send_command_party_dismount_clicked'  , " Dismount (Party) ", 505, y+60)
QtBind.createButton(gui, 'send_command_All_dismount_clicked'  , " Dismount (All) ", 605, y+60)
QtBind.createButton(gui, 'send_command_party_GC_clicked'  , " Take GC (Party) ", 505, y+80)
QtBind.createButton(gui, 'send_command_All_GC_clicked'  , " Take GC (All) ", 605, y+80)
QtBind.createButton(gui, 'send_command_party_Q1_clicked'  , " TP Q1 (Party) ", 505, y+100)
QtBind.createButton(gui, 'send_command_All_Q1_clicked'  , " TP Q1 (All) ", 605, y+100)
QtBind.createButton(gui, 'send_command_party_Q2_clicked'  , " TP Q2 (Party) ", 505, y+120)
QtBind.createButton(gui, 'send_command_All_Q2_clicked'  , " TP Q2 (All) ", 605, y+120)
QtBind.createButton(gui, 'send_command_party_Q3_clicked'  , " TP Q3 (Party) ", 505, y+140)
QtBind.createButton(gui, 'send_command_All_Q3_clicked'  , " TP Q3 (All) ", 605, y+140)





#Buttons Functionality
def send_command_party_clicked():
    cmd = QtBind.text(gui, cb_commands)
    if cmd:
        phBotChat.Party(cmd)
        log('[BossHelper] Sent [' + cmd + '] command to party')
 
def send_command_All_clicked():
    cmd = QtBind.text(gui, cb_commands)
    if cmd:
        phBotChat.All(cmd)
        log('[BossHelper] Sent [' + cmd + '] command to all')
 
def send_command_party_trace_clicked():
    player = QtBind.text(gui, tb_trace)
    if player:
        phBotChat.Party("TT " + player)
        log('[BossHelper] Sent [TT ' + player + '] command to party')
 
def send_command_All_trace_clicked():
    player = QtBind.text(gui, tb_trace)
    if player:
        phBotChat.All("TT " + player)
        log('[BossHelper] Sent [TT ' + player + '] command to all')
 
def send_command_no_trace_party_clicked():
    phBotChat.Party("N")
    log('[BossHelper] Sent [N] command to party')
 
def send_command_no_trace_All_clicked():
    phBotChat.All("N")
    log('[BossHelper] Sent [N] command to all')
 
def send_command_party_tp_clicked():
    tp1 = QtBind.text(gui, tb_tp1)
    tp2 = QtBind.text(gui, tb_tp2)
    if tp1 and tp2:
        phBotChat.Party("TP " + tp1 + "," + tp2)
        log(f'[BossHelper] Sent [TP {tp1},{tp2}] command to party')
 
def send_command_All_tp_clicked():
    tp1 = QtBind.text(gui, tb_tp1)
    tp2 = QtBind.text(gui, tb_tp2)
    if tp1 and tp2:
        phBotChat.All("TP " + tp1 + "," + tp2)
        log(f'[BossHelper] Sent [TP {tp1},{tp2}] command to all')
 
def send_command_party_moveon_clicked():
    radius = QtBind.text(gui, tb_moveon)
    if radius:
        phBotChat.Party("MN " + radius)
        log('[BossHelper] Sent [MN ' + radius + '] command to party')
 
def send_command_All_moveon_clicked():
    radius = QtBind.text(gui, tb_moveon)
    if radius:
        phBotChat.All("MN " + radius)
        log('[BossHelper] Sent [MN ' + radius + '] command to all')
 
def send_command_party_mount_clicked():
    mount_type = QtBind.text(gui, cb_mount_types)
    if mount_type:
        phBotChat.Party("M " + mount_type)
        log('[BossHelper] Sent [M ' + mount_type + '] command to party')
 
def send_command_All_mount_clicked():
    mount_type = QtBind.text(gui, cb_mount_types)
    if mount_type:
        phBotChat.All("M " + mount_type)
        log('[BossHelper] Sent [M ' + mount_type + '] command to all')
 
def send_command_party_dismount_clicked():
    mount_type = QtBind.text(gui, cb_mount_types)
    if mount_type:
        phBotChat.Party("D")
        log('[BossHelper] Sent [D] command to party')
 
def send_command_All_dismount_clicked():
    mount_type = QtBind.text(gui, cb_mount_types)
    if mount_type:
        phBotChat.All("D")
        log('[BossHelper] Sent [D] command to all')
 
def send_command_party_setradius_clicked():
    radius = QtBind.text(gui, tb_radius)
    if radius:
        phBotChat.Party("SETR " + radius)
        log('[BossHelper] Sent [SETR ' + radius + '] command to party')
 
def send_command_All_setradius_clicked():
    radius = QtBind.text(gui, tb_radius)
    if radius:
        phBotChat.All("SETR " + radius)
        log('[BossHelper] Sent [SETR ' + radius + '] command to all')
 
def send_command_party_setscript_clicked():
    script = QtBind.text(gui, tb_setscript)
    if script:
        phBotChat.Party("SETS " + script)
        log('[BossHelper] Sent [SETS ' + script + '] command to party')
 
def send_command_All_setscript_clicked():
    script = QtBind.text(gui, tb_setscript)
    if script:
        phBotChat.All("SETS " + script)
        log('[BossHelper] Sent [SETS ' + script + '] command to all')
 
def send_command_party_setarea_clicked():
    area = QtBind.text(gui, tb_setarea)
    if area:
        phBotChat.Party("SETA " + area)
        log('[BossHelper] Sent [SETA ' + area + '] command to party')
 
def send_command_All_setarea_clicked():
    area = QtBind.text(gui, tb_setarea)
    if area:
        phBotChat.All("SETA " + area)
        log('[BossHelper] Sent [SETA ' + area + '] command to all')
 
def send_command_party_profile_clicked():
    profile = QtBind.text(gui, tb_profile)
    if profile:
        phBotChat.Party("PROFILE " + profile)
        log('[BossHelper] Sent [PROFILE ' + profile + '] command to party')
 
def send_command_All_profile_clicked():
    profile = QtBind.text(gui, tb_profile)
    if profile:
        phBotChat.All("PROFILE " + profile)
        log('[BossHelper] Sent [PROFILE ' + profile + '] command to all')
 
def send_command_party_follow_clicked():
    follow = QtBind.text(gui, tb_follow1)
    distance = QtBind.text(gui, tb_follow2)
    if follow and distance:
        phBotChat.Party("F " + follow + " " + distance)
        log(f'[BossHelper] Sent [F {follow} {distance}] command to party')
 
def send_command_All_follow_clicked():
    follow = QtBind.text(gui, tb_follow1)
    distance = QtBind.text(gui, tb_follow2)
    if follow and distance:
        phBotChat.All("F " + follow + " " + distance)
        log(f'[BossHelper] Sent [F {follow} {distance}] command to all')
 
def send_command_no_follow_party_clicked():
    phBotChat.Party("NF")
    log('[BossHelper] Sent [NF] command to party')
 
def send_command_no_follow_All_clicked():
    phBotChat.All("NF")
    log('[BossHelper] Sent [NF] command to all')
 
def send_command_party_cape_clicked():
    cape = QtBind.text(gui, cb_cape)
    if cape:
        phBotChat.Party("CAPE " + cape)
        log('[BossHelper] Sent [CAPE ' + cape + '] command to party')
 
def send_command_All_cape_clicked():
    cape = QtBind.text(gui, cb_cape)
    if cape:
        phBotChat.All("CAPE " + cape)
        log('[BossHelper] Sent [CAPE ' + cape + '] command to all')

def send_command_party_equip_clicked():
    equip = QtBind.text(gui, tb_equip)
    if equip:
        phBotChat.Party("EQUIP " + equip)
        log('[BossHelper] Sent [EQUIP ' + equip + '] command to party')

def send_command_All_equip_clicked():
    equip = QtBind.text(gui, tb_equip)
    if equip:
        phBotChat.All("EQUIP " + equip)
        log('[BossHelper] Sent [EQUIP ' + equip + '] command to all')

def send_command_party_unequip_clicked():
    unequip = QtBind.text(gui, tb_unequip)
    if unequip:
        phBotChat.Party("UNEQUIP " + unequip)
        log('[BossHelper] Sent [UNEQUIP ' + unequip + '] command to party')

def send_command_All_unequip_clicked():
    unequip = QtBind.text(gui, tb_unequip)
    if unequip:
        phBotChat.All("UNEQUIP " + unequip)
        log('[BossHelper] Sent [UNEQUIP ' + unequip + '] command to all')

def send_command_party_use_clicked():
    use = QtBind.text(gui, tb_use)
    if use:
        phBotChat.Party("USE " + use)
        log('[BossHelper] Sent [USE ' + use + '] command to party')

def send_command_All_use_clicked():
    use = QtBind.text(gui, tb_use)
    if use:
        phBotChat.All("USE " + use)
        log('[BossHelper] Sent [USE ' + use + '] command to all')

def send_command_party_reverse_clicked():
    reverse_type = QtBind.text(gui, cb_reverse_types)
    reverse_player_or_zone = QtBind.text(gui, tb_reverse)
    if reverse_type:
        phBotChat.Party("REVERSE " + reverse_type + " " + (reverse_player_or_zone or ''))
        log(f'[BossHelper] Sent [REVERSE {reverse_type} {reverse_player_or_zone or ""}] command to party')

def send_command_All_reverse_clicked():
    reverse_type = QtBind.text(gui, cb_reverse_types)
    reverse_player_or_zone = QtBind.text(gui, tb_reverse)
    if reverse_type:
        phBotChat.All("REVERSE " + reverse_type + " " + (reverse_player_or_zone or ''))
        log(f'[BossHelper] Sent [REVERSE {reverse_type} {reverse_player_or_zone or ""}] command to all')

def ues_dino_Party_clicked():
    phBotChat.Party("PET1")
    log('[BossHelper] Sent [PET1] command to party')

def ues_dino_All_clicked():
    phBotChat.All("PET1")
    log('[BossHelper] Sent [PET1] command to all')

def ues_dark_Party_clicked():
    phBotChat.Party("PET2")
    log('[BossHelper] Sent [PET2] command to party')

def ues_dark_All_clicked():
    phBotChat.All("PET2")
    log('[BossHelper] Sent [PET2] command to all')

def send_command_leader_trace_party_clicked():
    phBotChat.Party("T")
    log('[BossHelper] Sent [T] command to party')

def send_command_leader_trace_All_clicked():
    phBotChat.All("T")
    log('[BossHelper] Sent [T] command to all')

def send_command_leader_follow_party_clicked():
    phBotChat.Party("F")
    log('[BossHelper] Sent [F] command to party')

def send_command_leader_follow_All_clicked():
    phBotChat.All("F")
    log('[BossHelper] Sent [F] command to all')

def send_command_start_party_clicked():
    phBotChat.Party("S")
    log('[BossHelper] Sent [S] command to party')

def send_command_start_All_clicked():
    phBotChat.All("S")
    log('[BossHelper] Sent [S] command to all')

def send_command_stop_party_clicked():
    phBotChat.Party("SP")
    log('[BossHelper] Sent [SP] command to party')

def send_command_stop_All_clicked():
    phBotChat.All("SP")
    log('[BossHelper] Sent [SP] command to all')

def send_command_party_M_mount_clicked():
    phBotChat.Party("M")
    log('[BossHelper] Sent [M] command to party')

def send_command_All_M_mount_clicked():
    phBotChat.All("M")
    log('[BossHelper] Sent [M] command to all')

def send_command_party_GC_clicked():
    phBotChat.Party("INJECT 0x7417 true 02 00 00 00")
    log('[BossHelper] Sent [Take GC] command to party')

def send_command_All_GC_clicked():
    phBotChat.All("INJECT 0x7417 true 02 00 00 00")
    log('[BossHelper] Sent [Take GC] command to all')

def send_command_party_zerk_clicked():
    phBotChat.Party("Z")
    log('[BossHelper] Sent [Z] command to party')

def send_command_All_zerk_clicked():
    phBotChat.All("Z")
    log('[BossHelper] Sent [Z] command to all')

def send_command_party_sit_clicked():
    phBotChat.Party("SIT")
    log('[BossHelper] Sent [SIT] command to party')

def send_command_All_sit_clicked():
    phBotChat.All("SIT")
    log('[BossHelper] Sent [SIT] command to all')

def send_command_party_jump_clicked():
    phBotChat.Party("JUMP")
    log('[BossHelper] Sent [JUMP] command to party')

def send_command_All_jump_clicked():
    phBotChat.All("JUMP")
    log('[BossHelper] Sent [JUMP] command to all')

def send_command_GETPOS_party_clicked():
    phBotChat.Party("GETPOS")
    log('[BossHelper] Sent [GETPOS] command to party')

def send_command_GETPOS_All_clicked():
    phBotChat.All("GETPOS")
    log('[BossHelper] Sent [GETPOS] command to all')

def send_command_INJECT_party_clicked():
    opcode = QtBind.text(gui, tb_opcode)
    data = QtBind.text(gui, tb_data)
    if opcode and data:
        phBotChat.Party("INJECT " + opcode + " true " + data)
        log(f'[BossHelper] Sent [INJECT {opcode} true {data}] command to party')
 
def send_command_INJECT_All_clicked():
    opcode = QtBind.text(gui, tb_opcode)
    data = QtBind.text(gui, tb_data)
    if opcode and data:
        phBotChat.Party("INJECT " + opcode + " true " + encrypted)
        log(f'[BossHelper] Sent [INJECT {opcode} true {data}] command to all')

def send_command_Hero_party_clicked():
    phBotChat.Party("INJECT 0x7074 true 01 04 25 94 00 00 00")
    log('[BossHelper] Sent [Hero Skill] command to party')

def send_command_Hero_All_clicked():
    phBotChat.All("INJECT 0x7074 true 01 04 25 94 00 00 00")
    log('[BossHelper] Sent [Hero Skill] command to all')

def send_command_Devil_party_clicked():
    phBotChat.Party("INJECT 0x7074 true 01 04 A8 79 00 00 00")
    log('[BossHelper] Sent [Devil Skill] command to party')

def send_command_Devil_All_clicked():
    phBotChat.All("INJECT 0x7074 true 01 04 A8 79 00 00 00")
    log('[BossHelper] Sent [Devil Skill] command to all')

def send_command_Angle_party_clicked():
    phBotChat.Party("INJECT 0x7074 true 01 04 02 84 00 00 00")
    log('[BossHelper] Sent [Angle Skill] command to party')

def send_command_Angle_All_clicked():
    phBotChat.All("INJECT 0x7074 true 01 04 02 84 00 00 00")
    log('[BossHelper] Sent [Angle Skill] command to all')

def send_command_party_Q1_clicked():
    phBotChat.Party("Q1")
    log('[BossHelper] Sent [Q1] command to party')

def send_command_All_Q1_clicked():
    phBotChat.All("Q1")
    log('[BossHelper] Sent [Q1] command to all')

def send_command_party_Q2_clicked():
    phBotChat.Party("Q2")
    log('[BossHelper] Sent [Q2] command to party')

def send_command_All_Q2_clicked():
    phBotChat.All("Q2")
    log('[BossHelper] Sent [Q2] command to all')

def send_command_party_Q3_clicked():
    phBotChat.Party("Q3")
    log('[BossHelper] Sent [Q3] command to party')

def send_command_All_Q3_clicked():
    phBotChat.All("Q3")
    log('[BossHelper] Sent [Q3] command to all')

# Plugin loaded
log("Plugin: "+pName+" ❴ BossGame / Amr Mansour ❵ v"+pVersion+" successfully loaded ✔")