# Initial

First install Python 3.

Create and activate a virtual environment

    ```powershell
    python -m venv venv
    .\venv\Scripts\activate

Now install the requirements:

    ```powershell
    pip install -r requirements.txt

# Mindstorms Robot Inventor

The code consists of two parts:

* The `hub.py` program that needs to run on the hub.
* The `client.py` program that runs on your computer.

To get the hub program onto the hub, the easiest option is to use the PyBricks website.
It will demonstrate how to put the correct firmware on the hub and how to upload the program.
Just copy-and-paste the `hub.py` code into the PyBricks editor.

Once the hub program is on the hub, it is important to disconnect the hub from the PyBricks website.
To do this, simply press the Bluetooth button on the PyBricks editor. The little beams will 
disappear to indicate that the hub is no longer connected.

Now you can run the client program on your computer:

    ```powershell
    python client.py

When it has detected the hub, it will ask you to start the program by pressing the big button.

It is also possible to use pybricksdev, but this does not offer any advantages over the PyBricks website.
If you want to use this approach, check the next section.


# EV3

This is currently not very well developed, but the principal is exactly the same as for the Robot Inventor Hub.

Run the program

    ```powershell
    pybricksdev run ble .\technic.py

Or using the name that you gave the hub during the firmware installation:

    ```powershell
    pybricksdev run ble -n "Technic Hub" .\technic.py 


# Protocol

The protocol to the robot has two message types: a 'D' or drive message and the 'B' or bye message. 

## Drive message

Every 'D' message must contains exactly 7 characters.

Example:
+---+---+---+---+---+---+---+
| 0 | 1 | 2 | 3 | 4 | 5 | 6 |
+---+---+---+---+---+---+---+
| D | + | 2 | 0 | - | 3 | 0 |
+---+---+---+---+---+---+---+

This command will set the left motor to turn at 20% of its maximum speed and the right motor to turn at 30% of 
its maximum speed in reverse.

The first character must always be uppercase D, the next 6 characters are used to control the motors:

* All zeros (000000) will stop the motors.
* The first and 4th character are either a + or a - to indicate the direction of the motor.
* All other characters are digits between 0 and 9 to indicate the speed of the motor.

To parse a command, the following regex is used `^D([+-0])(\d\d)([+-0])(\d\d)$`. You can expeirment with it here:
https://regex101.com/r/vLf5D9/1

## Bye message

The bye message is a single character 'B' that indicates that the client is done sending commands and that the hub
can stop the program.