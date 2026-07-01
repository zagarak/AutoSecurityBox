# manifest.py - /micropython/ports/rp2/manifest.py
# Place manifest.py in ports/rp2 of your micropython repo.
# Then add asb modules to ports/rp2/module and build with manifest.
# If you don't include _boot, _boot_fat, and rp2 you will not have filesystem access!
# Freeze board libraries and asb modules.
module("_boot.py")
module("_boot_fat.py")
module("rp2.py")
module("mfrc522.py")
module("asb.py")
module("asb_fman.py")
module("asb_crypt.py")
module("asb_auth.py")
