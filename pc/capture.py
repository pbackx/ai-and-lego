import cv2
import time


def capture(host, port, capture_interval=10, total_time=60):
    print(f"Capturing frames from {host}:{port}")
    cap = cv2.VideoCapture(f"udp://{host}:{port}")

    print("Starting timer")
    start_time = time.time()
    frame_count = 0

    # TODO it is probably much better to use the schedule library to capture frames at a regular interval
    # Instead of this busy loop
    # https://pypi.org/project/schedule/
    while frame_count < 5:
        try:
            ret, frame = cap.read()

            # Check if it's time to save a frame
            current_time = time.time()
            if ret and current_time - start_time >= capture_interval:
                frame_count += 1
                # TODO create folder if it doesn't exist otherwise writing will fail silently
                image_filename = f"capture/frame_{frame_count}.png"

                # Save the frame as an image
                cv2.imwrite(image_filename, frame)
                print(f"Saved {image_filename}")

                # Reset the timer
                start_time = current_time

        except Exception as e:
            print(f"Error: {e}")
            break

    cap.release()
