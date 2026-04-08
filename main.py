## AutoSecurityBox by Zagarak
# Written for Micropython v1.23.0 on Raspberry Pi Pico 2020.
## Libraries and modules.
import os
import sys
import fileRW # Depends on fileRW Version 1.0.7.
import machine # Necessary for handling board reset.
from utime import sleep
from machine import Pin, PWM
from mfrc533 import MFRC522 # Known-good RC522 library, name change arbitrary.

## Version Handling.
# Version channel, number, and codename variables.
vchan = "stable"
vmajor = 1 # Incriment when major changes are made to code or vminor + 1 > 9.
vminor = 4 # Incriment when significant changes are made to functionality or vpatch + 1 > 9.
vpatch = 1 # Incriment when minor changes are made to syntax or readability.
vernum = "v" + str(vmajor) + "." + str(vminor) + "." + str(vpatch) + "-" + str(vchan)
codenam = "s3c0ndf4ct0r"

## Pin declarations.
relay0 = Pin(15, Pin.OUT) # Declare starter activation relay.
secLight = Pin(12, Pin.OUT) # Declare security light.
reader = MFRC522(spi_id=0,sck=18,miso=20,mosi=19,cs=2,rst=22) # Declare reader Antenna.

## Core functions.
# Starter unlock function.
def unlockStarter(sHold): # Unlock starter for the specified amount of time.
    print("[AUTH] Starter relay will unlock in 200ms!")
    sleep(0.2)
    relay0.value(1)
    print("[AUTH] Unlocked for " + str(float(sHold) * 1000) + "ms...")
    secLight.value(0) # Turn security light off while starter is unlocked.
    sleep(float(sHold)) # Sleep for sHold seconds as float.
    relay0.value(0)
    print("[AUTH] Locked! Security light will illuminate briefly")
    print("[AUTH] before exit-code flashes are displayed.")
    print("")
    sleep(0.1)
    secLight.value(1) # Once relocked, reactivate security light.

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
    print("[INFO] Software: AutoSecurityBox-" + str(vernum))
    print("[INFO] Codename: " + str(codenam))
    print("[INFO] Author: Zagarak")
    print("")

# Status light function.
def blinkLight(blinks): # Blinks security light to indicate exit or status code.
    for i in range(blinks): # Number of blinks as int.
        secLight.value(1) # Blink pattern is on, off.
        sleep(0.3)
        secLight.value(0)
        sleep(0.3)

# Config file setup function.
def setupConfig():
    global cMode
    global rSleep
    global sHangA
    global sHangB
    global accessCardA
    global accessCardB
    global accessCardC
    # Check that config.json exists.
    fExists = fileRW.readFile("config.json", True) # Tuple bool is lookup(if_exists).
    if fExists == True: # If exists, report exists and populate variables.
        cMode = fileRW.readJSON("config.json", "md0")
        rSleep = fileRW.readJSON("config.json", "rs0")
        sHangA = fileRW.readJSON("config.json", "cs0")
        sHangB = fileRW.readJSON("config.json", "cs1")
        accessCardA = fileRW.readJSON("config.json", "ac0")
        accessCardB = fileRW.readJSON("config.json", "ac1")
        accessCardC = fileRW.readJSON("config.json", "ac2")
        print("[MEM] Loaded config.")
    elif fExists == False: # If not exists, create and set to default: authMode(value).
        print("[MEM] Generating default config...")
        # JSON format is fname, cardA, cardB, mode0, disarmed-ul-timeout, armed-ul-timeout, reader-sleep.
        # Default setup values. Adjust in config.json after generation.
        # Generated default config mode set to standby-mode in v 1.4.1-testing.
        # This was done so that on first run, system can be used until a card is setup in config.
        fileRW.setupJSON("config.json", 12345678, 87654321, 98765432, 1010, 11, 7, 1.2)
    else:
        print("[MEM] An error occured while setting up config.")

# Initialize reader function.
def initReader():
    ptick = 0
    # Declare global variables card, errlvl, ptickMax.
    global card
    global errLvl
    global ptickMax
    # Error level, attempt, and wrong card tally variables as int.
    wctallyMax = 3
    wctally = 0
    errLvl = 0
    # Config mode checks.
    if cMode == 1010: # Standby-mode call unlockStarter() and then set reader cycle limit.
        ptickMax = 3 # Reduce reader cycle limit when in service mode.
        print("[MODE] Standby-mode active, system disarmed.")
        print("")
        print("[MODE] Relay will close for " + str(sHangB) + "s and then once reopened,")
        print("[MODE] you may scan a registered card within ~3s to switch the system to auth-mode.")
        print("[MODE] ")
        print("")
        unlockStarter(sHangB) # Initiate standby-mode unlock before reader initializes.
    elif cMode == 3040: # Auth-mode cycle limit set.
        ptickMax = 24 # Reader detection cycle limit in (seconds x reader_sleep(x)) as int.
        print("[MODE] Auth-mode active, system armed. ")
        print("")
        print("[MODE] Reader will initialize and you will have ~28s to scan a registered")
        print("[MODE] card. Once a valid card has been scanned, relay will close for " + str(sHangA) + "s")
        print("[MODE] and then once reopened, mode will be set to auth-mode in config and")
        print("[MODE] then system will exit.")
        print("")
    while True:
        if cMode == 4003: # Panic-mode check (inside while loop to leverage break).
            print("[MODE] System panicked.")
            errlvl = 44 # Set exit code to wrong card and skip reader.init().
            break
        reader.init()
        print("[ASB] Reader initialised succesfully.")
        print("")
        (stat, tag_type) = reader.request(reader.REQIDL)
        sleep(float(rSleep)) # Reader polling timeout now editable in config.json.
        if stat == reader.OK:
            print("[RDR] Card detected! Attempting read, please wait...")
            (stat, uid) = reader.SelectTagSN()
            if stat == reader.OK:
                print("[RDR] Card read successfully.")
                print("")
                print("[RDR] =======================")
                print("[RDR]   SCAN RESULTS")
                print("[RDR] -----------------------")
                # Convert card UID bytes to int.
                card = int.from_bytes(bytes(uid), "little", False)
                print("[RDR]   CARD UID: " + str(card))
                print("[RDR] =======================")
                print("")
                if cMode == 3040:
                    if card == accessCardA:
                        print("[AUTH] Access Granted! | Presented card matches a valid record.")
                        print("")
                        unlockStarter(sHangA)
                        fileRW.amendJSON("config.json", "md0", 1010)
                        errLvl = 33
                        break
                    elif card == accessCardB:
                        print("[AUTH] Access Granted! | Presented card matches a valid record.")
                        print("")
                        unlockStarter(sHangA)
                        fileRW.amendJSON("config.json", "md0", 1010)
                        errLvl = 33
                        break
                    elif card == accessCardC:
                        print("[AUTH] Access Granted! | Presented card matches a valid record.")
                        print("")
                        unlockStarter(sHangA)
                        fileRW.amendJSON("config.json", "md0", 1010)
                        errLvl = 33
                        break
                    else:
                        wctally += 1
                        print("[AUTH] Access Denied! | Presented card does not match any valid records.")
                        print("[AUTH] Attempt (" + str(wctally) + "/" + str(wctallyMax) + ")")
                        blinkLight(2) # Give two flashes for wrong-card-presented warning.
                        secLight.value(1) # Turn security light back on after warning flashes.
                        # Check wctally and break if exceeding attempt limit.
                        if wctally >= wctallyMax:
                            errLvl = 44 # Set exit to wrong card term point.
                            print("[AUTH] Maximum attempt limit reached! System will PANIC!")
                            # Set panic mode in config and reset board.
                            fileRW.amendJSON("config.json", "md0", 4003)
                            print("[BOARD] Board will reset. Power cycle required to continue.")
                            sleep(3)
                            machine.reset()
                            sleep(2)
                            break
                        else: # Reset cycle count to allow for another attempt.
                            ptick = 0
                            sleep(0.1)
                elif cMode == 1010: # If in standby-mode, change mode and break
                    if card == accessCardA:
                        print("[AUTH] Card Detected! | System switched to auth-mode.")
                        fileRW.amendJSON("config.json", "md0", 3040)
                        errLvl = 21
                        break
                    elif card == accessCardB:
                        print("[AUTH] Card Detected! | System switched to auth-mode.")
                        fileRW.amendJSON("config.json", "md0", 3040)
                        errLvl = 21
                        break
                    elif card == accessCardC:
                        print("[AUTH] Card Detected! | System switched to auth-mode.")
                        fileRW.amendJSON("config.json", "md0", 3040)
                        errLvl = 21
                        break
                    else: # If non-registered card is presented, warn prompt.
                        print("[AUTH] Invalid Card! | Presented card is not registered as a service card.")
            else: # Card unreadable or absent while resolving uid.
                print("[RDR] Error reading card. Please hold it close to the reader and keep it still...")
        else: # No card detected or no reader state change.
            if ptick < ptickMax:
                print("[RDR] No card detected! Place a card in front of the reader to begin. (Cycle: " + str(ptick) + "/" + str(ptickMax) + ")")
                ptick += 1
            elif ptick >= ptickMax:
                print("[RDR] Reader timed out. System will exit...")
                errLvl = 22
                break
            else:
                print("[WARN] Error! ptick(value) unparsable.")
                errLvl = 55
                break
    else: # True ≠ True in while?
        print("[CRIT] Error! Reader initialization failed.")
        print("")
        errLvl = 93 # Set errlvl to exit on exception-unknown.

## Setup.
# Setup config file with default settings or get existing config.
setupConfig()
# Print hardware and software info to debug console.
prInfo()
# Get and print the board's current memory info.
hRam = fileRW.getRAM()
fBlocks = fileRW.getNOR()
print("[MEM] Free Heap RAM: " + str(hRam) + " | Flash Memory: " + str(fBlocks))
print("")
# Ensure relay is in the correct starting state (open).
relay0.value(0)

## Main.
# Turn security light on, initialize reader and mode detection, catch exit code.
try:
    print("[ASB] Initializing...")
    print("")
    secLight.value(1)
    initReader()
    sleep(0.2)
# Try-fail general exception catch.
except:
    # Do not set or incriment errlvl value here.
    print("[CRIT] An exception or KeyboardInterrupt has occured!")
# Check error level, cleanup, and exit.
finally: 
    if errLvl == 21: # Authmode-access-granted termination point.
        print("[ASB] Program halted on 'auth-mode-active'.")
        # Output exit code over security light.
        secLight.value(0) # Reset security light to ensure exit code is readable.
        sleep(0.4)
        blinkLight(2)
        sleep(0.4)
        blinkLight(1)
    elif errLvl == 44: # Wrong card read attempt limit termination point.
        print("[ASB] Program halted on 'system-panic'. Attempt limit reached, system locked out.")
        secLight.value(0) # Reset security light to ensure exit code is readable.
        sleep(0.4)
        blinkLight(4)
        sleep(0.4)
        blinkLight(4)
    elif errLvl == 22: # 62 Reader cycle limit reached termination point.
        print("[ASB] Program halted on 'cycle-limit-reached'. Cycle request timeout.")
        secLight.value(0) # Reset security light to ensure exit code is readable.
        sleep(0.4)
        blinkLight(2)
        sleep(0.4)
        blinkLight(2)
    elif errLvl == 55: # Reader cycle count unparsable termination point.
        print("[WARN] Program halted on 'reader-bad-value'. Cycle count unparsable.")
        secLight.value(0) # Reset security light to ensure exit code is readable.
        sleep(0.4)
        blinkLight(5)
        sleep(0.4)
        blinkLight(5)
    elif errLvl == 33:# Standby-mode active termination point.
        print("[ASB] Program halted on 'standby-mode-active'.")
        secLight.value(0) # Reset security light to ensure exit code is readable.
        sleep(0.4)
        blinkLight(3)
        sleep(0.4)
        blinkLight(3)
    else: # Unknown exception (catch-all) termination point.
        errLvl = 93 # Display error level 93 for all unknown exceptions.
        print("[CRIT] Program halted on 'exception-unknown'.")
        secLight.value(0) # Reset security light to ensure exit code is readable.
        sleep(0.4)
        blinkLight(9)
        sleep(0.4)
        blinkLight(3)
    print("[ASB] Exited with code: " + str(errLvl))
    sleep(0.1)
    # Exit program.
    # Use sys module to exit cleanly and prevent restart before power is lost.
    sys.exit()
## EOF
