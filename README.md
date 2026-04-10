# AutoSecurityBox
Tested on: Micropython v1.23.0 | Raspberry Pi Pico 2020

## Setup
To get started, follow ``schema.png`` to wire board and modules. You may also refer to [this](https://github.com/wendlers/micropython-mfrc522/blob/master/README.md) for detailed reader setup instructions.

After the board and modules are assembled, choose an enclosure and mounting location. I chose to mount mine inside the steering column, positioning the reader in a manner so that cards could be read through the plastic column. Then place ``main.py`` in the ``/`` directory of the board using a USB cable and your choice of IDE. See [dependencies](#dependencies). Run a test of ``main.py`` and it will generate ``config.json``. After it exits edit the configuration file to include your card UIDs modify the starter hang-time or reader polling timeout to tune them to your needs.

## About
AutoSecurityBox is a Micropython based security project geared towards enhancing the security of older vehicles that lack transponder keys or keyless ignitions by electrically breaking the starter solenoid wire after the ignition switch but before the solenoid, and placing a relay in the circuit so that it may be switched by a microcontroller. Doing this also prevents hotwiring by accessing the starter circuit under the dash; Thereby increasing the time it would take  to steal the car. 

To do this I used a Raspberry Pi Pico 2020 board, RC522 Card Reader, a single 3V3 relay module, and an LED to display exit codes to the driver. Wiring is pretty straight forward. Refer to schema.png for wiring instructions. (PIN numbers listed may not correspond to actual physical location)

## Dependencies

This project depends on [micropython-mfrc522](https://github.com/wendlers/micropython-mfrc522/).

After flashing firmware, place ``mfrc522.py`` and ``fileRW.py`` in the ``/lib`` directory of the board.

## Notes
On first run, let ``main.py`` generate its own ``config.json``. If you try to create your own, the debug console may spit variable or type errors.

This project does not encrypt or obscure card UIDs. UIDs are stored locally on the board in ``config.json``. The goal here is not government level security, but to increase the difficulty in stealing or starting the vehicle without permission. Version handling is tracked within main.py and dependency versions within accompanying modules.
