## File-Read-Write-JSON-Manipulation Module
# For AutoSecurityBox, Written by Zagarak.
import os
import gc
import ujson

## Basic File Manipulation.
# Create a new file.
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

# Initialize JSON conforming to machine setup requirements.
# Check main.py and ensure new additions are included there.
def setupJSON(fname, cardA, cardB, cardC, modeA, dUlSleep, aUlSleep, rsleep):
    try:
        data = {
            "ac0": cardA,
            "ac1": cardB,
            "ac2": cardC,
            "md0": modeA,
            "cs0": dUlSleep,
            "cs1": aUlSleep,
            "rs0": rsleep,
        }
        with open(str(fname), "w") as file:
            file.write(ujson.dumps(data))
    except OSError:
        print("[FRW/WARN] OSError in fileRW.setupJSON.")
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
    sFs = os.statvfs('/') # Test for 'os' module functionality. For an alternative, use 'uos'.
    bSize = sFs[0]
    bFree = sFs[3]
    fBytes = bSize * bFree
    kBytes = fBytes / 1000
    bOut = str(fBytes) + " bytes (" + str(kBytes) + ") KB free."
    return bOut
## EOF
