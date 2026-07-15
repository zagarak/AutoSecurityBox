# AutoSecurityBox - Open Source Vehicle Security In A Box

## Table of Contents
1.) [About](#about)<br />
2.) [Precautions, Safety, & Disclaimers](#precautions-safety--disclaimers)<br />
3.) [Setup](#setup)<br />
4.) [Dependencies](#dependencies)<br />
5.) [Features & Operating Objective](#features--operating-objective)<br />
6.) [About Releases](#about-releases)<br />
7.) [Additional Notes](#additional-notes)

## About
> AutoSecurityBox is a project that aims to enhance the security of classic and antique vehicles that lack transponder keys or keyless ignitions by switching the starter solenoid coil wire with a logic-level relay immediately after the ignition switch inside the steering column. The controller emulates the function of a transponder key by preventing cranking of the vehicle until a valid nfc tag (or your choice of input) is detected.
    
> The driver presents a registered card to a hidden reader antenna, then ASB hashes the UID of the card and compares it to a stored hash. If they match the relay closes and the vehicle can then be started as normal. If the presented card does not match a valid record then the script will panic and lockout, preventing future attempts at starting the vehicle until you reset it.

## Precautions, Safety, & Disclaimers
- Do **not** wire in a way that prevents vehicle operation during emergencies.
- Follow automotive electrical safety standards: Disconnect the battery before installation/testing, fuse positive lines at source with correct values, and verify wiring before reconnecting the battery.
- This is **not tamper-proof** security; it simply dissuades potential thieves by increasing the complexity of the starter system.
- Freezing modules in ``/lib`` and ``keys.json`` hash as bytecode in firmware greatly increases **tamper resistance!**
- You are **solely responsible for your safety** and the functionality/warranty of your vehicle.
- For safety purposes I have programmed ASB with a built in "standby-mode".
- It is recommended to leave the vehicle in standby-mode during normal operation in case of engine stall so you can recover it without presenting a card.
- For this reason after a valid card is presented in auth-mode, by default the system automatically switches to standby-mode.

## Setup
To get started, follow ``schema.png`` to wire board and modules. You may also refer to [this page](https://github.com/wendlers/micropython-mfrc522/blob/master/README.md) for detailed reader setup instructions.

> After the board and external modules are assembled, choose an enclosure and mounting location. I chose to mount mine inside the steering column, positioning the reader in a manner so that cards could be read through the plastic column. Decide if you are using the Python modules as-is or if you are freezing them as bytecode in firmware. If you are using them as-is, place all modules in ``/lib``. Then place ``main.py`` in the ``/`` directory of the board using a USB cable and your choice of IDE. See [dependencies](#dependencies).
    
> On the initial run, ``keys.json`` will be generated in ``/`` automatically. Using Thonny or your preferred IDE, run ``main.py`` again and wait for the reader to initialize (~7-10 seconds) and then scan the card you wish to register. The debug console will print the UID of the card. Copy it or write it down and then stop ``main.py``. Then edit ``keys.json`` and replace the JSON data keys ``k0``, ``k1``, and ``k2`` with the SHA256 hash of the UID of the cards you wish to register. Then add the hash to ``asb_crypt`` variable ``kh``. Now run ``main.py`` one more time and verify that scanning the card results in an "Access Granted!" print statement.

## Dependencies
> ### <ins>**External:**</ins><br />
> [micropython/micropython](https://github.com/micropython/micropython)<br />
> [wendlers/micropython-mfrc522](https://github.com/wendlers/micropython-mfrc522/)<br />
> ### <ins>**Internal:**</ins><br />
> [lib/asb](https://github.com/zagarak/AutoSecurityBox/blob/main/lib/asb.py)<br />
> [lib/asb_auth](https://github.com/zagarak/AutoSecurityBox/blob/main/lib/asb_auth.py)<br />
> [lib/asb_crypt](https://github.com/zagarak/AutoSecurityBox/blob/main/lib/asb_crypt.py)<br />
> [lib/asb_fman](https://github.com/zagarak/AutoSecurityBox/blob/main/lib/asb_fman.py)<br />

## Features & Operating Objective
The goal of this project is to provide security for parked vehicles that lack native anti-theft systems. AutoSecurityBox implements a dual-mode approach to provide security when it is necessary and maintain simplicity and reliability when it is not, especially during active operation of the vehicle and while recovering from stalls.
- Standby Mode/Disarmed
- Auth Mode/Armed
 
### Operating objective
> By default ``config.json`` is generated with the mode (data key m0) set to standby (int 1010). When ``asb.py`` runs it checks this data key and if in standby mode, it closes the starter relay for a duration in seconds equal to the value of the data key ``disarm_sleep``. Then it opens the relay and initializes the reader for a duration of ``reader_sleep`` x ``ptickMax`` seconds to allow the user to arm the system. Finally it exits, and if a valid card was scanned, overwrites data key ``m0`` with the string ``"auth"``.

> When ``asb.py`` runs it checks this data key and if in auth/armed mode, initializes the reader for a duration equal to the value of the data key ``reader_sleep`` x ``ptickMax`` seconds. If a valid card is scanned during this time, the system will close the starter relay for ``arm_sleep`` seconds, disarm and exit on "system-disarmed" and on the next power cycle it will return to standby-mode operation. If no card is scanned, it will exit on "routine-timeout".

> For added security: If three read attempts are made with an invalid card, it overwrites the data key ``m0`` with the string ``"panic"`` and then resets the board. This puts the program into a tertiary mode that will refuse to initialize the reader or actuate the starter relay; Instead exiting on "system-panic" until ``m0`` is updated to either ``"auth"`` or ``"standby"``.

## About Releases
> AutoSecurityBox requires some setup before it will run properly. You must allow it to generate the files it expects and then configure them to match your needs (card uid hashes, config, mifare keys, etc.). Because of this releases are not ready-to-go packages per se, but represent tested, stable snapshots of the project.

> Do not write ``keys.json`` or ``config.json`` to the microcontroller's filesystem directly; Instead, allow ASB to generate its own object files to ensure they comply exactly with what the software expects. After generation you may modify their contents to conform to your needs.

> If you are freezing ``asb_crypt.py`` and/or other modules in firmware, modify ``asb_crypt.rtn_hw_hsh()`` and ``asb_crypt.cKey`` to their corresponding values before compiling Micropython.

## Additional Notes
**I've implemented SHA256 hashing of scanned card UIDs, stored UIDs, and the key file itsself. You will have to manually hash your UIDs before inputting them into keys.json. Then hash keys.json and input it into ``asb_crypt.py`` before freezing modules and compiling firmware.**

> The goal of this project is not government quality security. Instead, the hope is to increase the difficulty, time, and technical requirements for a potential thief to get away with the vehicle. In the future I plan to also control the fuel pump or ignition system. Though, this would require the board and relays to remain powered during operation of the vehicle.

> Mode values are arbitrary and may be changed by the end user so long as each corresponding reference in ``asb.py`` is also changed to match its partner. They exist solely to act as a magic number so that the Microcontroller can track state changes between power cycles without a backup battery.

> You may notice a diode on ``5v+_Vsys`` in ``schema.png``. I added it between the supply and the microcontroller to isolate the converter output from the debug cable's ``5v+`` to prevent backfeeding of the buck converter during programming.
