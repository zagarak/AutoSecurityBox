# AutoSecurityBox
#### Tested on: Micropython v1.23.0
### 
### AutoSecurityBox is a Micropython based security project geared towards enhancing the security of older vehicles that lack transponder keys or keyless ignitions by electrically breaking the starter solenoid wire after the ignition switch but before the solenoid, and placing a relay in the circuit so that it may be switched by a microcontroller. Doing this also prevents hotwiring by accessing the starter circuit under the dash; Thereby increasing the time it would take  to steal the car. 
### To do this I used a Raspberry Pi Pico 2020 board, RC522 Card Reader, a single 3V3 relay module, and an LED to display exit codes to the driver. Wiring is pretty straight forward. Refer to schema.png for wiring instructions. (PIN numbers listed may not correspond to actual physical location)
### On first run, let main.py generate its own 'config.json'. If you try to create your own, the debug console may spit variable or type errors.
### Note: This project does not encrypt or obscure card UIDs. UIDs are stored locally on the board in 'config.json'. The goal here is not government level security, but to increase the difficulty in stealing or starting the vehicle without permission.
