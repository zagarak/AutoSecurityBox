# asb_auth.py
## Authentication and Security Functions Module for AutoSecurityBox.
# Written for Micropython.

__version__ = "0.0.7"

import machine
import asb_fman # Depends on v2.0.7
import asb_crypt # Depends on v0.0.5
from time import sleep
from mfrc522 import MFRC522 # Wendlers Micropython MFRC522 library.

## Pin declarations.
relay0 = machine.Pin(15, machine.Pin.OUT) # Declare starter circuit relay.
secLight = machine.Pin(12, machine.Pin.OUT) # Declare security/status light.
reader = MFRC522(spi_id=0,sck=18,miso=20,mosi=19,cs=2,rst=22) # Declare reader Antenna.

# Status light function.
def blink_sec_led(blinks): # Blinks security light to indicate exit or status code.
    ledState = secLight.value()
    if ledState == 1:
        secLight.value(0)
        sleep(0.4)
    for i in range(blinks): # Number of blinks as int.
        secLight.value(1)
        sleep(0.3)
        secLight.value(0)
        sleep(0.3)

# Config file setup function.
def check_config():
    if asb_fman.read_file("config.json", True) == False: 
        print("[MEM] Generating default config...")
        # JSON format is fname, mode0, disarmed-ul-timeout, armed-ul-timeout, reader-sleep, reader-timeout.
        # Default setup values. Adjust in config.json after generation.
        asb_fman.gen_config("config.json", "standby", 11, 7, 1.2, 12)
        sleep(1)
        asb_fman.reboot(False)
    else:
        global mode
        global sHangA
        global sHangB
        global rSleep
        global rTimeout
        mode = asb_fman.load_json_obj("config.json", "m0")
        sHangA = asb_fman.load_json_obj("config.json", "arm_sleep")
        sHangB = asb_fman.load_json_obj("config.json", "disarm_sleep")
        rSleep = asb_fman.load_json_obj("config.json", "reader_sleep")
        rTimeout = asb_fman.load_json_obj("config.json", "reader_timeout")
    if asb_fman.read_file("keys.json", True) == False:
        print("[MEM] Generating default keys...")
        asb_fman.gen_keys("keys.json", "k0", "k1", "k2")
        sleep(1)
        asb_fman.reboot(False)
    else:
        global keyRecordA
        global keyRecordB
        global keyRecordC
        keyRecordA = asb_fman.load_json_obj("keys.json", "k0")
        keyRecordB = asb_fman.load_json_obj("keys.json", "k1")
        keyRecordC = asb_fman.load_json_obj("keys.json", "k2")

# Starter unlock function.
def unlock_starter(sHold): # Unlock starter for the specified amount of time.
    print("[AUTH] Starter will unlock in 200ms!")
    sleep(0.2)
    relay0.value(1)
    print("[AUTH] Unlocked for " + str(float(sHold * 1000)) + "ms...")
    secLight.value(0) # Turn security light off while starter is unlocked.
    sleep(float(sHold))
    relay0.value(0)
    print("[AUTH] Locked! Security light will illuminate briefly before")
    print("[AUTH] exit-code flashes are displayed.")
    print("")
    sleep(0.1)
    secLight.value(1) # Once relocked, reactivate security light.

# Initialize Reader Function.
def poll_reader(cycles):
    global card
    card = 0 # Set default card value to 0 for detecting no card state.
    tick = 0
    for i in range(cycles):
        reader.init()
        print("[AUTH] Reader initialised succesfully.")
        print("")
        (stat, tag_type) = reader.request(reader.REQIDL)
        sleep(float(rSleep))
        tick += 1
        if stat == reader.OK:
            print("[AUTH] Card detected! Attempting read, please wait...")
            (stat, uid) = reader.SelectTagSN()
            if stat == reader.OK:
                cuid = int.from_bytes(bytes(uid), "little", False)
                card = asb_crypt.cnv_uid(str(cuid))
                print("[AUTH] Card read successfully.")
                print("")
                print("[AUTH] =======================")
                print("[AUTH]   SCAN RESULTS")
                print("[AUTH] -----------------------")
                print("[AUTH]   CARD UID: " + str(card))
                print("[AUTH] =======================")
                print("")
                break
            else: # Card unreadable or absent while resolving uid.
                print("[WARN] Read Error! | Presented card is unreadable or was removed before read completed.")
        else: # No card detected or no reader state change. ptick goes here.
            print("[WARN] No card detected during this cycle. | Cycle: (" + str(tick) + "/" + str(cycleLimit) + ")")

# Handle Authorization Function.
def start_auth_proto():
    global errLvl
    global cycleLimit
    errLvl = 0 # Set initial error level.
    relay0.value(0) # Set initial relay state.
    secLight.value(1)
    print("[MEM] Free Heap RAM: " + str(asb_fman.get_heap_fram()) + " | Flash Memory: " + str(asb_fman.get_nor_fbytes()))
    print("")
    print("[ASB] Done.")
    print("")
    if mode == "standby": # Standby-mode.
        cycleLimit = rTimeout / 4 # Shorten cycle limit to one-quarter of normal when in standby-mode.
        print("[MODE] Standby-mode active, system disarmed.")
        print("")
        print("[MODE] Starter will unlock for " + str(sHangB) + "s and then once locked,")
        print("[MODE] you will have " + str(cycleLimit * rSleep) + "s to scan a registered")
        print("[MODE] card and switch to auth-mode. Otherwise, system will exit with no change.")
        print("")
        sleep(0.2)
        unlock_starter(sHangB)
        poll_reader(cycleLimit) # Reader cycles as int.
        if card == keyRecordA:
            print("[AUTH] Card Detected! | System switched to auth-mode.")
            asb_fman.amend_json_obj("config.json", "m0", "auth")
            errLvl = 31
        elif card == keyRecordB:
            print("[AUTH] Card Detected! | System switched to auth-mode.")
            asb_fman.amend_json_obj("config.json", "m0", "auth")
            errLvl = 31
        elif card == keyRecordC:
            print("[AUTH] Card Detected! | System switched to auth-mode.")
            asb_fman.amend_json_obj("config.json", "m0", "auth")
            errLvl = 31
        elif card == 0: # If no card was scanned, exit on timeout.
            print("[WARN] Reader timed out.")
            errLvl = 22
        else: # If card is anything other than 0 or registered card, warn card is unregistered.
            print("[AUTH] Invalid Card! | Presented card is unregistered.")
    elif mode == "auth": # Auth-mode.
        cycleLimit = rTimeout
        print("[MODE] Auth-mode active, system armed. ")
        print("")
        print("[MODE] Reader will initialize and you will have ~28s to scan a registered")
        print("[MODE] card. Once a valid card has been scanned, starter will unlock for " + str(sHangA) + "s")
        print("[MODE] and then once locked, mode will be set to standby-mode and then")
        print("[MODE] system will exit.")
        print("")
        poll_reader(cycleLimit) # Reader cycles as int.
        if card == keyRecordA:
            print("[AUTH] Access Granted! | Presented card matches a valid record.")
            print("")
            blink_sec_led(2) # Blink light twice to indicate card read.
            unlock_starter(sHangA)
            asb_fman.amend_json_obj("config.json", "m0", "standby")
            errLvl = 33
        elif card == keyRecordB:
            print("[AUTH] Access Granted! | Presented card matches a valid record.")
            print("")
            blink_sec_led(2)
            unlock_starter(sHangA)
            asb_fman.amend_json_obj("config.json", "m0", "standby")
            errLvl = 33
        elif card == keyRecordC:
            print("[AUTH] Access Granted! | Presented card matches a valid record.")
            print("")
            blink_sec_led(2)
            unlock_starter(sHangA)
            asb_fman.amend_json_obj("config.json", "m0", "standby")
            errLvl = 33
        elif card == 0:
            print("[ASB] Reader timed out.")
            errLvl = 22
        else:
            print("[AUTH] Invalid Card! | Presented card is unregistered.")
            print("[AUTH] System will PANIC!")
            blink_sec_led(3)
            asb_fman.amend_json_obj("config.json", "m0", "panic")
            sleep(2)
            asb_fman.suspend_exec(True)
    elif mode == "panic": # Panic-mode.
        print("[MODE] System panicked!")
        errLvl = 44

if __name__ == "__main__":
    print("[ASB] asb_auth.py should be frozen in firmware and imported by asb.py!")
    sleep(3)
    machine.reset()
# EOF
