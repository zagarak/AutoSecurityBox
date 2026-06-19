# AutoSecurityBox
This repository does not provide releases. You may clone it and use it directly or fork it for your own project.

## About
> AutoSecurityBox is a project that aims to enhance the security of classic and antique vehicles that lack transponder keys or keyless ignitions by switching the starter solenoid wire with a logic-level relay immediately after the ignition switch inside the steering column. The controller then emulates the function of a transponder key by adding an access layer in between the driver and the vehicle.
    
> The driver presents a registered card to a hidden reader antenna, then ASB hashes the UID of the card and compares it to a stored hash. If they match the relay closes and the vehicle can then be started as normal. If the presented card does not match a valid record then the script will panic and lockout, preventing future attempts at starting the vehicle until you reset it.

## Precautions, Safety, & Disclaimers
- Do **not** wire in a way that prevents vehicle operation during emergencies.
- Follow automotive electrical safety standards: Disconnect the battery before installation/testing, fuse positive lines at source with correct values, and verify wiring before reconnecting the battery.
- This is **not tamper-proof** security; it simply dissuades potential thieves by increasing the complexity of the starter system.
- You are **solely responsible for your safety** and the functionality/warranty of your vehicle.
- For safety purposes I have programmed ASB with a built in "standby-mode".
- It is recommended to leave the vehicle in standby-mode during normal operation in case of engine stall so you can recover it without presenting a card.
- For this reason after a valid card is presented in auth-mode, by default the system automatically switches to standby-mode.

## Setup
To get started, follow ``schema.png`` to wire board and modules. You may also refer to [this page](https://github.com/wendlers/micropython-mfrc522/blob/master/README.md) for detailed reader setup instructions.

> After the board and modules are assembled, choose an enclosure and mounting location. I chose to mount mine inside the steering column, positioning the reader in a manner so that cards could be read through the plastic column. Then place ``main.py`` in the ``/`` directory of the board using a USB cable and your choice of IDE. See [dependencies](#dependencies).
    
> On the initial run, ``main.py`` will generate ``config.json`` in ``/``. Using Thonny or your preferred IDE, run ``main.py`` again and wait for the reader to initialize (~7-10 seconds) and then scan the card you wish to register. The debug console will print the UID of the card. Copy it or write it down and then stop ``main.py``. Then edit ``config.json`` and replace the JSON data keys ``c0``, ``c1``, and/or ``c2`` with the SHA256 hash of the UID of your card(s). Now run ``main.py`` one more time and verify that scanning the card results in an "Access Granted!" print statement.

## Dependencies

This project depends on [micropython-mfrc522](https://github.com/wendlers/micropython-mfrc522/).<br />
After flashing firmware, place ``mfrc522.py`` and ``fileRW.py`` in the ``/lib`` directory of the board.<br />
For instructions on flashing MicroPython to Pico or for other information, see its [documentation](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
<br />
| Firmware Version     | Board            | Status          |
| -------------------- | ---------------- | --------------- |
| MicroPython v1.23.0  | RP2040/Pico 2020 | Tested, Working |
| MicroPython v1.28.0  | RP2040/Pico 2020 | Testing         |

## Features & Operating Objective
The goal of this project is to provide security for parked vehicles that lack native anti-theft systems. AutoSecurityBox implements a dual-mode approach to provide security when it is necessary and maintain simplicity and reliability when it is not, especially during active operation of the vehicle and while recovering from stalls.
- Standby Mode/Disarmed
- Auth Mode/Armed
 
### Operating objective
> By default ``config.json`` is generated with the mode (data key m0) set to standby (int 1010). When ``main.py`` runs it checks this data key and if in standby mode, it closes the starter relay for a duration in seconds equal to the value of the data key ``disarm_sleep``. Then it opens the relay and initializes the reader for a duration of ``reader_sleep`` x ``ptickMax`` seconds to allow the user to arm the system. Finally it exits, and if a valid card was scanned, overwrites data key ``m0`` with the value ``3040``.

> When ``main.py`` runs it checks this data key and if in auth/armed mode, initializes the reader for a duration equal to the value of the data key ``reader_sleep`` x ``ptickMax`` seconds. If a valid card is scanned during this time, the system will close the starter relay for ``arm_sleep`` seconds, disarm and exit on "system-disarmed" and on the next power cycle it will return to standby-mode operation. If no card is scanned, it will exit on "routine-timeout".

> For added security: If three read attempts are made with an invalid card, it overwrites the data key ``m0`` with the value ``4003`` and then resets the board. This puts the program into a tertiary mode that will refuse to initialize the reader or actuate the starter relay; Instead exiting on "system-panic" until ``m0`` is updated to either ``3040`` or ``1010``.

## Additional Notes
~~Card UIDs are not encrypted or obscured in any way.~~

**I have implemented rudimentary support for SHA256 hashing of scanned card UIDs and comparison of stored UID hashes. You will have to manually hash your UIDs before inputting them into config.json.**

> The goal of this project is not government quality security. Instead, the hope is to increase the difficulty, time, and technical requirements for a potential thief to get away with the vehicle. In the future I plan to also control the fuel pump or ignition system. Though, this would require the board and relays to remain powered during operation of the vehicle.

> Mode values are arbitrary and may be changed by the end user so long as each corresponding reference in ``main.py`` is also changed to match its partner. They exist solely to act as a magic number so that the Microcontroller can track state changes between power cycles without a backup battery.

> You may notice a diode on ``5v+_Vsys`` in ``schema.png``. I added it between the supply and the microcontroller to isolate the converter output from the debug cable's ``5v+`` to prevent backfeeding of the buck converter during programming.

***This project could easily be adapted for electronic door lock cylinders and servo-actuated access panel latches.**
