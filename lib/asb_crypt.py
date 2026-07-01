# asb_crypt.py
## SHA256 Hashing and Key Integrity Management Module for AutoSecurityBox.
# Written for Micropython.

__version__ = "0.0.4"

import machine
import hashlib
import binascii
from time import sleep

# SHA256 Hashing Functions.
# Convert a provided input to SHA256 hash lowercase hex.
def cnv_uid(vIn):
    try:
        hEnc = hashlib.sha256(str(vIn).encode())
        raw = hEnc.digest()
        hOut = binascii.hexlify(raw).decode()
    except OSError:
        print("[WARN] OSError in cnv_uid().")
    else:
        return str(hOut)

# Generate hash from file.
def rtn_f_hsh(path, chunk_size=512):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                h.update(data)
    except OSError:
        print("[WARN] OSError in rtn_f_hsh().")
    else:
        return ''.join('{:02x}'.format(b) for b in h.digest())

## Internal keys.json SHA256 hash (lowercase hex).
# ----------------------------------------------------------------
def rtn_hw_hsh():
    kh = "HASH3"
    return kh
# ----------------------------------------------------------------

## Firmware level key integrity check
# Run only when library is imported by another component.
if __name__ == "asb_crypt":
    try:
        file = open(str("/keys.json"), "r")
        data = file.read()
    except OSError: # If file doesn't exist.
        print("[CRYPT] No stored keys!")
    else:
        print("[CRYPT] Verifying key integrity...")
        if rtn_f_hsh("/keys.json") == rtn_hw_hsh():
            print("[CRIT] Passed integrity check!")
        else:
            print("[CRIT] Integrity check failed!")
            sleep(5)
            machine.reset()

if __name__ == "__main__":
    print("[ASB] asb_crypt.py should be frozen in firmware and imported by asb_auth.py!")
    sleep(3)
    machine.reset()
# EOF
