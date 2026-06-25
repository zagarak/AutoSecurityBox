## AutoSecurityBox by Zagarak
# Written for Micropython on RP2040/Pico 2020/Arduino.

__version__ = "1.7.4"

import os
import sys
import asb_fman # Depends on asb_fman v2.0.2
import asb_hasher # Depends on asb_hasher v0.0.1
import machine
from utime import sleep
from machine import Pin, PWM
from mfrc522 import MFRC522 # Wendlers Micropython MFRC522 library.

## Pin declarations.
relay0 = Pin(15, Pin.OUT) # Declare starter circuit relay.
secLight = Pin(12, Pin.OUT) # Declare security/status light.
reader = MFRC522(spi_id=0,sck=18,miso=20,mosi=19,cs=2,rst=22) # Declare reader Antenna.

## Core Functions.

# Suspend function. (MP v1.28.0 breaks machine.reset halt from v1.23.0)
def suspend(secs):
    print("[BOARD] Board will reset. Power cycle required to continue.")
    sleep(secs)
    machine.reset()

# Status light function.
def blinkLight(blinks): # Blinks security light to indicate exit or status code.
    ledState = secLight.value() # Get current security light state.
    if ledState == 1: # If security light is on, turn it off to improve flash code readability.
        secLight.value(0)
        sleep(0.4) # Exit code flash delay for readability.
    for i in range(blinks): # Number of blinks as int.
        secLight.value(1)
        sleep(0.3)
        secLight.value(0)
        sleep(0.3)

# Print hardware and software info function.
def prInfo():
    print("[INFO] Hardware Information:")
    print("")
    print("[INFO] Microcontroller: Raspberry Pi Pico")
    print("[INFO] RFID Reader: MFRC522 (RFID-RC522)")
    print("[INFO] Relay Board: Single 3V3 SONGLE, Opti-Flyback")
    print("[INFO] Status LED: 5mm 3V 30mA White LED w/ 2Kohm Resistor")
    print("")
    print("[INFO] Software Information:")
    print("")
    print("[INFO] Firmware: Micropython")
    print("[INFO] Software: AutoSecurityBox-v" + str(__version__))
    print("[INFO] Author: Zagarak")
    print("")

# Config file setup function.
def setupConfig():
    global cMode
    global rSleep
    global sHangA
    global sHangB
    global rTimeout
    global accessCardA
    global accessCardB
    global accessCardC
    # Check that config.json exists.
    cfgExists = asb_fman.readFile("config.json", True) # Tuple is str(fname), bool(lookup).
    if cfgExists == True: # If exists, report exists and populate variables.
        cMode = asb_fman.readJSON("config.json", "m0")
        rSleep = asb_fman.readJSON("config.json", "reader_sleep")
        sHangA = asb_fman.readJSON("config.json", "arm_sleep")
        sHangB = asb_fman.readJSON("config.json", "disarm_sleep")
        rTimeout = asb_fman.readJSON("config.json", "reader_timeout")
        print("[MEM] Loaded config.")
        print("")
    elif cfgExists == False: # If not exists, create. 
        print("[MEM] Generating default config...")
        # JSON format is fname, mode0, disarmed-ul-timeout, armed-ul-timeout, reader-sleep, reader-timeout.
        # Default setup values. Adjust in config.json after generation.
        asb_fman.setupCFG("config.json", 1010, 11, 7, 1.2, 12)
    else:
        print("[MEM] An error occured while setting up config.")
    kfExists = asb_fman.readFile("keys.json", True)
    if kfExists == True:
        accessCardA = asb_fman.readJSON("keys.json", "c0")
        accessCardB = asb_fman.readJSON("keys.json", "c1")
        accessCardC = asb_fman.readJSON("keys.json", "c2")
        print("[MEM] Loaded keys.")
        print("")
    elif kfExists == False:
        print("[MEM] Generating default keys...")
        asb_fman.setupKF("keys.json", "K0", "K1", "K2")
    else:
        print("[MEM] An error occured while setting up config.")
# Starter unlock function.
def unlockStarter(sHold): # Unlock starter for the specified amount of time.
    print("[AUTH] Starter will unlock in 200ms!")
    sleep(0.2)
    relay0.value(1)
    # Moved parenthesis in v1.5.4. Old statement: str(float(sHold) * 100)
    # New statement: str(float(sHold * 1000))
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
def initReader(cycles):
    global card
    card = 0 # Set default card value to 0 for detecting no card state.
    tick = 0
    for i in range(cycles):
        reader.init()
        print("[ASB] Reader initialised succesfully.")
        print("")
        (stat, tag_type) = reader.request(reader.REQIDL)
        sleep(float(rSleep))
        tick += 1
        if stat == reader.OK:
            print("[RDR] Card detected! Attempting read, please wait...")
            (stat, uid) = reader.SelectTagSN()
            if stat == reader.OK:
                cuid = int.from_bytes(bytes(uid), "little", False)
                card = asb_hasher.cnv_uid(str(cuid))
                print("[RDR] Card read successfully.")
                print("")
                print("[RDR] =======================")
                print("[RDR]   SCAN RESULTS")
                print("[RDR] -----------------------")
                print("[RDR]   CARD UID: " + str(cuid))
                print("[RDR] =======================")
                print("")
                break
            else: # Card unreadable or absent while resolving uid.
                print("[RDR] Read Error! | Presented card is unreadable or was removed before read completed.")
        else: # No card detected or no reader state change. ptick goes here.
            print("[RDR] No card detected during this cycle. | Cycle: (" + str(tick) + "/" + str(cycleLimit) + ")")
            
# Handle Authorization Function.
def initAuth():
    global errLvl
    global cycleLimit
    errLvl = 0 # Starting error level.
    if cMode == 1010: # Standby-mode call unlockStarter() and then set reader cycle limit.
        cycleLimit = rTimeout / 4 # Shorten cycle limit to one-quarter when in standby-mode.
        print("[MODE] Standby-mode active, system disarmed.")
        print("")
        print("[MODE] Starter will unlock for " + str(sHangB) + "s and then once locked,")
        print("[MODE] you will have " + str(cycleLimit * rSleep) + "s to scan a registered")
        print("[MODE] card and switch to auth-mode. Otherwise, system will exit with no change.")
        print("")
        sleep(0.2) # Security light flash buffer sleep.
        unlockStarter(sHangB) # Initiate standby-mode unlock before reader initializes.
        # Then initialize reader briefly for mode change requests.
        initReader(cycleLimit) # Reader cycles as int.
        if card == accessCardA:
            print("[AUTH] Card Detected! | System switched to auth-mode.")
            asb_fman.amendJSON("config.json", "m0", 3040)
            errLvl = 31
        elif card == accessCardB:
            print("[AUTH] Card Detected! | System switched to auth-mode.")
            asb_fman.amendJSON("config.json", "m0", 3040)
            errLvl = 31
        elif card == accessCardC:
            print("[AUTH] Card Detected! | System switched to auth-mode.")
            asb_fman.amendJSON("config.json", "m0", 3040)
            errLvl = 31
        elif card == 0: # If no card was scanned, exit on timeout.
            print("[ASB] Reader timed out.")
            errLvl = 22
        else: # If card is anything other than 0 or registered card, warn card is unregistered.
            print("[AUTH] Invalid Card! | Presented card is unregistered.")
            # No panic required when requesting auth-mode from standby-mode.
    elif cMode == 4003: # If in panic-mode, break before reader.init().
        print("[MODE] System panicked.")
        errLvl = 44
    elif cMode == 3040: # Auth-mode cycle limit set.
        cycleLimit = rTimeout # Get cycleLimit from config.
        print("[MODE] Auth-mode active, system armed. ")
        print("")
        print("[MODE] Reader will initialize and you will have ~28s to scan a registered")
        print("[MODE] card. Once a valid card has been scanned, starter will unlock for " + str(sHangA) + "s")
        print("[MODE] and then once locked, mode will be set to standby-mode and then")
        print("[MODE] system will exit.")
        print("")
        initReader(cycleLimit) # Reader cycles as int.
        if card == accessCardA:
            print("[AUTH] Access Granted! | Presented card matches a valid record.")
            print("")
            blinkLight(2) # Blink light twice to indicate card read.
            unlockStarter(sHangA)
            asb_fman.amendJSON("config.json", "m0", 1010)
            errLvl = 33
        elif card == accessCardB:
            print("[AUTH] Access Granted! | Presented card matches a valid record.")
            print("")
            blinkLight(2)
            unlockStarter(sHangA)
            asb_fman.amendJSON("config.json", "m0", 1010)
            errLvl = 33
        elif card == accessCardC:
            print("[AUTH] Access Granted! | Presented card matches a valid record.")
            print("")
            blinkLight(2)
            unlockStarter(sHangA)
            asb_fman.amendJSON("config.json", "m0", 1010)
            errLvl = 33
        elif card == 0: # If no card was scanned, exit on timeout.
            print("[ASB] Reader timed out.")
            errLvl = 22
        else: # If card is anything other than 0 or registered card, panic system.
            print("[AUTH] Invalid Card! | Presented card is unregistered.")
            print("[AUTH] System will PANIC!")
            blinkLight(3) # Blink light thrice to indicate invalid card.
            asb_fman.amendJSON("config.json", "m0", 4003)
            sleep(2)
            suspend(180)

# ------------------------- ASB MAIN -------------------------

if __name__ == "asb":
    ## Setup main.
    # Setup config file with default settings or get existing config.
    setupConfig()
    # Print hardware and software info to debug console.
    prInfo()
    # Get and print the board's current memory info.
    hRam = asb_fman.getRAM()
    fBlocks = asb_fman.getNOR()
    print("[MEM] Free Heap RAM: " + str(hRam) + " | Flash Memory: " + str(fBlocks))
    print("")
    # Ensure relay is in the correct starting state (open).
    relay0.value(0)

    ## Main.
    # Turn security light on, initialize authentication routine, catch exit code.
    try:
        print("[ASB] Initializing...")
        print("")
        secLight.value(1)
        initAuth()
        sleep(0.1)
    # Try-fail general exception catch.
    except:
        # Do not set or incriment errLvl value here.
        print("[CRIT] An exception or KeyboardInterrupt has occured!")
    # Check error level, cleanup, and exit.
    finally:
        if errLvl == 31: # Auth-mode-activated termination point.
            print("[ASB] Program halted on 'auth-mode-activated'.")
            # Output exit code over security light.
            blinkLight(3)
            sleep(0.4)
            blinkLight(1)
        elif errLvl == 33: # Standby-mode-activated termination point.
            print("[ASB] Program halted on 'standby-mode-activated'.")
            blinkLight(3)
            sleep(0.4)
            blinkLight(3)
        elif errLvl == 44: # Panic-mode termination point.
            print("[ASB] Program halted on 'system-panic'. Attempt limit reached, system locked out.")
            blinkLight(4)
            sleep(0.4)
            blinkLight(4)
        elif errLvl == 22: # Routine-timeout termination point.
            print("[ASB] Program halted on 'routine-timeout'. | Last recorded mode: " + str(cMode))
            print("No input detected during routine. No configuration changes were made.")
            blinkLight(2)
            sleep(0.4)
            blinkLight(2)
        else: # Unknown exception (catch-all) termination point.
            errLvl = 93 # Display error level 93 for all unknown exceptions.
            print("[CRIT] Program halted on 'exception-unknown'.")
            blinkLight(9)
            sleep(0.4)
            blinkLight(3)
        print("[ASB] Exited with code: " + str(errLvl))
        sleep(0.1)
        suspend(180)
# EOF
