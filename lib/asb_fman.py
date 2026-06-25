# asb_fman.py
## File Manipulation and Memory Reporting Module
# For AutoSecurityBox on Micropython.

__version__ = "2.0.3"

import os
import gc
import ujson

def touchFile(fName, content):
    try:
        file = open(str(fName), "w")
    except OSError:
        print("[FRW/CRIT] An error occured of type OSError in touchFile(open).")
    except TypeError:
        print("[FRW/WARN] An error occured of type TypeError in touchFile(str(fName)).")
    else: # Success block
        file.write(content)
        file.flush()
        print("[FRW] File '/" + str(fName) + "' created succesfully.")
    file.close()

# Overwrite an existing file.
def owriteFile(fName, content):
    try:
        file = open(str(fName), "r")
        data = file.read()
    except OSError: # if file does not exist
        print("[FRW/WARN] An error occured of type OSError in owriteFile(open).")
        print("[FRW/WARN] '/"+ str(fName) + "' | No such file or directory.")
    except TypeError: # if typeerror occurs
        print("[FRW/WARN] A TypeError exception occured in owriteFile(str(fName)).")
    else: # Success block. File exists
        os.remove(str(fName))
        file = open(str(fName), "w")
        file.write(content)
        file.flush()
        print("[FRW] File contents overwritten.")
    file.close()

# Remove an existing file.
def removeFile(fName):
    try:
        os.remove(str(fName))
    except TypeError: # if type doesnt match str
        print("[FRW/WARN] A TypeError exception occured in os.remove(str(fName)).")
    else: # Success block.
        # Removed file successfully.
        print("[FRW] Removed file '/" + str(fName) + "' successfully")

# Read an existing file.
def readFile(fName, lookup):
    try:
        file = open(str(fName), "r")
        data = file.read()
    except OSError: # if file doesnt exist.
        print("[FRW/WARN] readFile(" + str(fName) + ") operation failed.")
        print("[FRW/WARN] '/"+ str(fName) + "' | No such file or directory.")
        exists = False
        return exists
    else: # Success block.
        if lookup == True:
            exists = True
            return exists
        elif lookup == False:
            print("[FRW] File loaded.")
            return str(data)
        else:
            print("[FRW/WARN] Error in fileRW.readFile(lookup). Bad value or TypeError.")
    file.close()

## JSON File Manipulation.

# Create JSON conforming to machine setup requirements.
# Check main.py and ensure new additions are included there.
def setupCFG(fname, modeA, dUlSleep, aUlSleep, rsleep, rtimeout):
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
        print("[FRW/WARN] OSError in fileRW.setupJSON.")
    else: # Success block.
        print("[FRW] JSON created successfully.")

def setupKF(fname, keyA, keyB, keyC):
    try:
        data = {
            "k0": keyA,
            "k1": keyB,
            "k2": keyC,
        }
        with open(str(fname), "w") as file:
            file.write(ujson.dumps(data))
    except OSError:
        print("[FRW/WARN] OSError in fileRW.setupKF.")
    else: # Success block.
        print("[FRW] JSON created successfully.")

# Retrieve a single entry in JSON.
def readJSON(fname, reqVar):
    try:
        with open(str(fname), "r") as file:
            raw = file.read()
    except OSError:
        print("[FRW/WARN] OSError in fileRW.readJSON.")
    else: # Success block.
        data = ujson.loads(raw)
        retVar = data[reqVar]
        return retVar

# Edit a single entry in JSON.
def amendJSON(fname, reqVar, newValue):
    try:
        with open(str(fname), "r") as file:
            data = ujson.load(file)
    except OSError:
        print("[FRW/WARN] OSError in fileRW.amendJSON(read).")
    else: # Success block.
        data[reqVar] = newValue
    try:
        with open(str(fname), "w") as file:
            file.write(ujson.dumps(data)) 
    except OSError:
        print("[FRW/WARN] OSError in fileRW.amendJSON(write).")
    else: # Success block.
        print("[FRW] JSON amended.")

## Filesystem information requests.

# Output free memory stats to debug console.
def getRAM(): # Get heap free RAM.
    gc.collect() # Run a garbage collect.
    fMem = gc.mem_free() # Get available heap RAM in bytes as int(fMem).
    cMem = fMem / 1024 # Divide to get kilobytes.
    fOut = str(fMem) + " bytes (" + str(cMem) + ") KB free."
    return fOut
def getNOR(): # Get board free flash.
    sFs = os.statvfs('/')
    bSize = sFs[0]
    bFree = sFs[3]
    fBytes = bSize * bFree
    kBytes = fBytes / 1000
    bOut = str(fBytes) + " bytes (" + str(kBytes) + ") KB free."
    return bOut

## EOF
