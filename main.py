# ASB Loader
# Eventually asb, asb_fman, and asb_hasher modules will move to firmwareland.
# This loader will be the entry point into asb to protect keys.json stored hash from
# accidental exposure. I am currently having trouble building Micropython with frozen 
# modules and FS support is not currently working. However, everything works as normal
# for now with modules in /lib on prebuilt Micropython.

def load_asb():
    print("Loading AutoSecurityBox...")
    import asb

if __name__ == "__main__":
    load_asb()
