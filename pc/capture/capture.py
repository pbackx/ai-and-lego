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


def find_next_frame_index(folder: str) -> int:
    try:
        # List all files in the given directory
        files = os.listdir(folder)

        # Filter files that match the naming pattern (e.g., "frame_1.png", "frame_2.png")
        matching_files = [file for file in files if file.startswith("frame_") and file.endswith(".png")]

        if not matching_files:
            print("No matching files found.")
            return 0

        # Extract the indices from the filenames and find the highest index
        indices = [int(file.split("_")[1].split(".")[0]) for file in matching_files]
        highest_index = max(indices) + 1

        return highest_index

    except FileNotFoundError:
        print(f"Directory '{folder}' not found.")
        return 0


class CaptureTask:
    def __init__(self, host, port, folder, capture_interval=1):
        self.host = host
        self.port = port
        self.folder = folder
        self.capture_interval = capture_interval
        self.capture_thread = None

    async def start(self):
        if not os.path.exists(self.folder) or not os.path.isdir(self.folder):
            os.makedirs(self.folder)

        self.capture_thread = VideoCaptureThread(self.host, self.port)

        print("Starting capture")

        frame_count = find_next_frame_index(self.folder)
        try:
            while True:
                frame_count += 1
                image_filename = os.path.join(self.folder, f"frame_{frame_count}.png")
                frame = self.capture_thread.read()
                cv2.imwrite(image_filename, frame)
                print(f"Saved {image_filename}")
                await asyncio.sleep(self.capture_interval)
        finally:
            self.capture_thread.cap.release()

    async def stop(self):
        self.capture_thread.cap.release()
        self.capture_thread.thread.join()
        self.capture_thread = None
