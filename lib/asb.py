# asb.py
## AutoSecurityBox Initialization, Termination, and Error Handling Module.
# Written for Micropython on RP2040/Pico 2020/Arduino, by Zagarak.

__version__ = "1.8.0"

import sys
import asb_auth # Depends on v0.0.2
from time import sleep

if __name__ == "asb":
    asb_auth.check_config()
    try:
        print("[ASB] AutoSecurityBox-v" + str(__version__) + "is starting...")
        print("")
        asb_auth.start_auth_proto()
        sleep(0.1)
    except:
        print("[CRIT] An exception or KeyboardInterrupt has occured!")
    finally:
        if asb_auth.errLvl == 31: # Auth-mode-activated termination point.
            print("[ASB] Program halted on 'auth-mode-activated'.")
            asb_auth.blink_sec_led(3)
            sleep(0.4)
            asb_auth.blink_sec_led(1)
        elif asb_auth.errLvl == 33: # Standby-mode-activated termination point.
            print("[ASB] Program halted on 'standby-mode-activated'.")
            asb_auth.blink_sec_led(3)
            sleep(0.4)
            asb_auth.blink_sec_led(3)
        elif asb_auth.errLvl == 44: # Panic-mode termination point.
            print("[ASB] Program halted on 'system-panic'. Attempt limit reached, system locked out.")
            asb_auth.blink_sec_led(4)
            sleep(0.4)
            asb_auth.blink_sec_led(4)
        elif asb_auth.errLvl == 22: # Polling-timeout termination point.
            print("[ASB] Program halted on 'polling-timeout'. | Last recorded mode: " + str(asb_auth.mode))
            print("No input detected during routine. No configuration changes were made.")
            asb_auth.blink_sec_led(2)
            sleep(0.4)
            asb_auth.blink_sec_led(2)
        else: # Unknown exception termination point.
            print("[CRIT] Program halted on 'exception-unknown'.")
            asb_auth.blink_sec_led(9)
            sleep(0.4)
            asb_auth.blink_sec_led(3)
        print("[ASB] Exited with code: " + str(asb_auth.errLvl))
        sleep(0.1)
        asb_auth.suspend_exec(True)
        sys.exit()
        
if __name__ == "__main__":
    print("[ASB] asb.py should be frozen in firmware and imported by main.py!")
    sleep(3)
    sys.exit()
# EOF
