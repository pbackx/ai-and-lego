import asyncio
import os
import traceback

import cv2
import schedule


async def start_capture(host, port, folder: str, capture_interval=10):
    if not os.path.exists(folder) or not os.path.isdir(folder):
        os.makedirs(folder)

    print(f"Connecting to video stream at {host}:{port}.")
    cap = cv2.VideoCapture(f"udp://{host}:{port}")

    print("Starting capture.")

    # schedule.every(capture_interval).seconds.do(capture_frame, cap, folder)

    try:
        while True:
            # schedule.run_pending()
            capture_frame(cap, folder)
            await asyncio.sleep(capture_interval)
    finally:
        cap.release()


frame_count = 0


def capture_frame(cap, folder):
    try:
        global frame_count

        ret = False
        frame = None

        while not ret:
            # Keep trying to capture a frame until we succeed
            # TODO this should have a timeout
            ret, frame = cap.read()

        frame_count += 1
        image_filename = os.path.join(folder, f"frame_{frame_count}.png")

        cv2.imwrite(image_filename, frame)
        print(f"Saved {image_filename}")
    except Exception as e:
        print(f"Failed to capture frame: {e}")
        traceback.print_exc()
