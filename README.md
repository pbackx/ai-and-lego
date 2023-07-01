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