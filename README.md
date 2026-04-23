# AutoSecurityBox
Tested on: Micropython v1.23.0 | Raspberry Pi Pico 2020<br />
This repository does not provide releases. You may clone it and use it directly or fork the project.

## About
AutoSecurityBox is a Micropython based security project geared towards enhancing the security of older vehicles that lack transponder keys or keyless ignitions by switching the starter solenoid wire immediately after the ignition switch inside the steering column by placing a logic-level switched relay in the circuit. Thereby preventing potential thieves easily accessing the starter circuit under the dash and bypassing the ignition lock cylinder, increasing the time, skill, and foreknowledge required to steal the car. 

To do this I used a Raspberry Pi Pico 2020 board, LM2596 Buck Converter, Momentary Power Switch, RC522 Card Reader, a single 3V3 relay module, and an LED to display exit codes to the driver. Wiring is pretty straight forward. Refer to schema.png for wiring instructions. (PIN numbers listed may not correspond to actual physical location)

## Setup
To get started, follow ``schema.png`` to wire board and modules. You may also refer to [this page](https://github.com/wendlers/micropython-mfrc522/blob/master/README.md) for detailed reader setup instructions.

After the board and modules are assembled, choose an enclosure and mounting location. I chose to mount mine inside the steering column, positioning the reader in a manner so that cards could be read through the plastic column. Then place ``main.py`` in the ``/`` directory of the board using a USB cable and your choice of IDE. See [dependencies](#dependencies).

On the initial run, ``main.py`` will generate ``config.json`` in ``/``. Using Thonny or your preferred IDE, run ``main.py`` again and wait for the reader to initialize (~7-10 seconds) and then scan the card you wish to register. The debug console will print the UID of the card. Copy it or write it down and then stop ``main.py``. Then edit ``config.json`` and replace the JSON data keys ``c0``, ``c1``, and/or ``c2`` with the UID of your card(s). Now run ``main.py`` one more time and verify that scanning the card results in an "Access Granted!" print statement.

## Dependencies

This project depends on [micropython-mfrc522](https://github.com/wendlers/micropython-mfrc522/).<br />
After flashing firmware, place ``mfrc522.py`` and ``fileRW.py`` in the ``/lib`` directory of the board.

## Features & Operating Objective
The goal of this project is to provide security for parked vehicles that lack native anti-theft systems. AutoSecurityBox implements a dual-mode approach to provide security when it is necessary and maintain simplicity and reliability when it is not, especially during active operation of the vehicle and while recovering from stalls.
- Standby Mode/Disarmed
- Auth Mode/Armed
 
### Operating objective
By default ``config.json`` is generated with the mode (data key m0) set to standby (int 1010). When ``main.py`` runs it checks this data key and if in standby mode, it closes the starter relay for a duration in seconds equal to the value of the data key ``disarm_sleep``. Then it opens the relay and initializes the reader for a duration of ``reader_sleep`` x ``ptickMax`` seconds to allow the user to arm the system. Finally it exits, and if a valid card was scanned, overwrites data key ``m0`` with the value ``3040``.

When ``main.py`` runs it checks this data key and if in auth/armed mode, initializes the reader for a duration equal to the value of the data key ``reader_sleep`` x ``ptickMax`` seconds. If a valid card is scanned during this time, the system will close the starter relay for ``arm_sleep`` seconds, disarm and exit on "system-disarmed" and on the next power cycle it will return to standby-mode operation.

If no card is scanned, it will exit on "reader-timeout".

For added security: If three read attempts are made with an invalid card, it overwrites the data key ``m0`` with the value ``4003`` and then resets the board. This puts the program into a tertiary mode that will refuse to initialize the reader or actuate the starter relay; Instead exiting on "system-panic" until ``m0`` is updated to either ``3040`` or ``1010``.

## Additional Notes
Card UIDs are not encrypted or obscured in any way. The goal of this project is not government quality security. Instead, the hope is to increase the difficulty, time, and technical requirements for a potential thief to get away with the vehicle. In the future I plan to also control the fuel pump or ignition system. Though, this would require the board and relays to remain powered during operation of the vehicle.

You may notice a diode on ``5v+_Vsys`` in ``schema.png``. During the first few tests on vehicle power I noticed the power LED was no longer illuminating on the buck converter. Alternator voltage fluctuates slightly and is higher than nominal battery voltage. However, I tested the output voltage stability of the converter before connecting the microcontroller and I wasn't satisfied that was the issue. The relay module is opti-coupled and has a flyback diode but just to be sure I added another diode between the supply and the microcontroller to isolate the converter output and this resolved the issue. My prototype system has been deployed for six months now with no upsets or sporadic behavior observed. 

***This project could easily be adapted for electronic door lock cylinders and servo-actuated access panel latches.**
