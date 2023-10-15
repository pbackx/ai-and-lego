import asyncio
import os
import queue
import threading

import cv2


# This thread reads all the frames from the video stream and discards them. There is no general way to skip frames.
class VideoCaptureThread:
    def __init__(self, host, port):
        print(f"Connecting to stream at {host}:{port}")
        self.cap = cv2.VideoCapture(f"udp://{host}:{port}")
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self._reader)
        self.thread.daemon = True
        self.thread.start()

    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()


async def start_capture(host, port, folder, capture_interval=1):
    if not os.path.exists(folder) or not os.path.isdir(folder):
        os.makedirs(folder)

    capture_thread = VideoCaptureThread(host, port)

    print("Starting capture")

    frame_count = 0
    try:
        while True:
            frame_count += 1
            image_filename = os.path.join(folder, f"frame_{frame_count}.png")
            frame = capture_thread.read()
            cv2.imwrite(image_filename, frame)
            print(f"Saved {image_filename}")
            await asyncio.sleep(capture_interval)
    finally:
        capture_thread.cap.release()
