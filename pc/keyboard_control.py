import keyboard

def main():
    print("Press 'q' to quit.")

    # Register a callback for keypress events
    keyboard.on_press(callback)

    # Keep the program running until 'q' is pressed
    keyboard.wait("q")

    # Unregister the callback and exit
    keyboard.unhook_all()

def callback(event):
    print(f"You pressed key: {event.name}")

if __name__ == "__main__":
    main()
