# asb_fman.py
## File Manipulation and Memory Reporting Module for AutoSecurityBox.
# Written for Micropython.

__version__ = "2.0.7"

import os
import gc
import ujson
import machine

## Basic File Manipulation.
# Create a new file.
def touch_file(fName, content):
    try:
        file = open(str(fName), "w")
    except OSError:
        print("[CRIT] An error occured of type OSError in touch_file(open).")
    except TypeError:
        print("[WARN] An error occured of type TypeError in touch_file(open).")
    else: # Success block.
        file.write(content)
        file.flush()
        print("[FMAN] File '/" + str(fName) + "' created succesfully.")
    file.close()

# Overwrite an existing file.
def o_write_file(fName, content):
    try:
        file = open(str(fName), "r")
        data = file.read()
    except OSError: # If file does not exist.
        print("[WARN] An error occured of type OSError in o_write_file(open).")
        print("[WARN] '/"+ str(fName) + "' | No such file or directory.")
    except TypeError:
        print("[WARN] An error occured of type TypeError in o_write_file(open).")
    else:
        os.remove(str(fName))
        file = open(str(fName), "w")
        file.write(content)
        file.flush()
        print("[FMAN] File contents overwritten.")
    file.close()

# Remove an existing file.
def rm_file(fName):
    try:
        os.remove(str(fName))
    except TypeError: # If type doesnt match str.
        print("[WARN] An error occured of type TypeError in rm_file().")
    else:
        print("[FMAN] Removed file '/" + str(fName) + "' successfully")

# Read the contents of an existing file.
def read_file(fName, lookup):
    try:
        file = open(str(fName), "r")
        data = file.read()
    except OSError: # if file doesnt exist.
        print("[WARN] An error occured of type OSError in read_file(open).")
        print("[WARN] '/"+ str(fName) + "' | No such file or directory.")
        exists = False
        return exists
    else:
        if lookup == True:
            exists = True
            return exists
        elif lookup == False:
            print("[FMAN] File loaded.")
            return str(data)
        else:
            print("[WARN] An error occured of type TypeError in read_file().")
    file.close()

## JSON File Manipulation.
# Create JSON conforming to ASB setup requirements.
def gen_config(fname, modeA, dUlSleep, aUlSleep, rsleep, rtimeout):
    try:
        data = {
            "m0": modeA,
            "disarm_sleep": dUlSleep,
            "arm_sleep": aUlSleep,
            "reader_sleep": rsleep,
            "reader_timeout": rtimeout,
        }
        with open(str(fname), "w") as file:
            file.write(ujson.dumps(data))
    except OSError:
        print("[WARN] An error occured of type OSError in gen_config().")
    else:
        print("[FMAN] CONFIG generated successfully.")

def gen_keys(fname, keyA, keyB, keyC):
    try:
        data = {
            "k0": keyA,
            "k1": keyB,
            "k2": keyC,
        }
        with open(str(fname), "w") as file:
            file.write(ujson.dumps(data))
    except OSError:
        print("[WARN] An error occured of type OSError in gen_keys().")
    else:
        print("[FMAN] KEYS generated successfully.")

# Retrieve a single entry in JSON.
def load_json_obj(fname, reqVar):
    try:
        with open(str(fname), "r") as file:
            raw = file.read()
    except OSError:
        print("[WARN] An error occured of type OSError in load_json_obj().")
    else:
        data = ujson.loads(raw)
        retVar = data[reqVar]
        return retVar

# Edit a single entry in JSON.
def amend_json_obj(fname, reqVar, newValue):
    try:
        with open(str(fname), "r") as file:
            data = ujson.load(file)
    except OSError:
        print("[WARN] An error occured of type OSError in amend_json_obj(load).")
    else:
        data[reqVar] = newValue
    try:
        with open(str(fname), "w") as file:
            file.write(ujson.dumps(data)) 
    except OSError:
        print("[WARN] An error occured of type OSError in amend_json_obj(load).")
    else:
        print("[FMAN] JSON amended.")

## Memory Reporting.
# Get heap free ram.
def get_heap_fram():
    try:
        gc.collect()
        fMem = gc.mem_free()
        cMem = fMem / 1024
        fOut = str(fMem) + " bytes (" + str(cMem) + ") KB free."
    except OSError:
        print("[WARN] An error occured of type OSError in get_heap_fram().")
    except TypeError:
        print("[WARN] An error occured of type TypeError in get_heap_fram().")
    except MemoryError:
        print("[WARN] An error occured of type MemoryError in get_heap_fram().")
    else:
        return fOut

# Get NOR free bytes.
def get_nor_fbytes():
    try:
        sFs = os.statvfs('/')
        bSize = sFs[0]
        bFree = sFs[3]
        fBytes = bSize * bFree
        kBytes = fBytes / 1000
        bOut = str(fBytes) + " bytes (" + str(kBytes) + ") KB free."
    except OSError:
        print("[WARN] An error occured of type OSError in get_nor_fbytes().")
    except TypeError:
        print("[WARN] An error occured of type TypeError in get_heap_fram().")
    except MemoryError:
        print("[WARN] An error occured of type MemoryError in get_nor_fbytes().")
    else:
        return bOut

## Power Management
# Suspend execution and reduce power
def suspend_exec(deepT):
    if deepT == True:
        print("[FMAN] Deep sleep active. Power cycle required to continue.")
        machine.deepsleep() # Deep sleep indefinitely.
    elif deepT == False:
        print("[FMAN] Light sleep active. Power cycle required to continue.")
        machine.lightsleep() # Lightsleep indefinitely.
        machine.reset() # Reset if lightsleep fails or on interrupt.
    else: # Catch exception.
        print("[WARN] An error occured in suspend().")

def reboot(dfu):
    if dfu == False:
        print("[FMAN] Rebooting, please wait...")
        machine.reset()
    elif dfu == True: # If requesting dfu, reboot to bootloader.
        print("[FMAN] Entering DFU mode, please wait...")
        machine.bootloader()
    else:
        print("[WARN] Invalid argument for reboot().")

if __name__ == "__main__":
    print("[ASB] asb_fman.py should be frozen in firmware and imported by asb_auth.py!")
## EOF
