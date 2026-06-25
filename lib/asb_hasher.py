# asb_hasher.py
## SHA256 Hashing and Key Integrity Management Module.
# For AutoSecurityBox.

__version__ = "0.0.1"

import machine
import hashlib
import binascii
from utime import sleep

def cnv_uid(vIn):
    hEnc = hashlib.sha256(str(vIn).encode())
    raw = hEnc.digest()
    hOut = binascii.hexlify(raw).decode()
    return str(hOut)

# Generate hash from file.
def rtn_f_hsh(path, chunk_size=512):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            h.update(data)
    return ''.join('{:02x}'.format(b) for b in h.digest())

# Your keys.json SHA256 hash goes here (lowercase hex).
# ----------------------------------------------------------------
def rtn_hw_hsh():
    kh = "HASH3"
    return kh
# ----------------------------------------------------------------

# Firmware level key integrity check
# Run only when library is imported by another component.

if __name__ == "asb_hasher":
    try:
        file = open(str("/keys.json"), "r")
        data = file.read()
    except OSError: # If file doesn't exist.
        print("[KMS] No stored keys!")
    else:
        print("[KMS] Verifying key integrity...")
        if rtn_f_hsh("/keys.json") == rtn_hw_hsh():
            print("[MEM/OK] System passed integrity check!")
        else:
            print("[MEM/CRIT] Integrity check failed!")
            sleep(5)
            machine.reset()
