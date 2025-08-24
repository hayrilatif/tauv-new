import sys

import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from lcm import LCM
import cv2
import time
import cv2
import pickle
import lz4.frame
import yaml
from  origins.efficient_streamer import EfficientVideoStreamer

def main_loop(shared_config):
    print("camera_streamer")
    
    #read configuration

    CHANNEL = shared_config['camera_streamer']['channel']
    WIDTH = int(shared_config['camera_streamer']['width'])
    HEIGHT = int(shared_config['camera_streamer']['height'])
    FPS = int(shared_config['camera_streamer']['fps'])
    COMPRESSION = shared_config['camera_streamer']['compression']
    QUALITY = int(shared_config['camera_streamer']['quality'])
    VIDEO_SOURCE = int(shared_config['camera_streamer']['video_source'])
    DEBUG_VIDEO = shared_config['camera_streamer']['debug_video']
    LCM_URL = shared_config["lcm_url"]

    frame_time = 1 / FPS

    streamer = EfficientVideoStreamer(lcm_url=LCM_URL)

    cap = cv2.VideoCapture(VIDEO_SOURCE)  # Open the default camera
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    print("Autofocus command sent.")

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

    try:
        while True:
            start_time = time.time()
            ret, frame = cap.read()
            if not ret:
                print("Frame okunmadı, çıkılıyor...")
                break
            
            streamer.send_video_frame(CHANNEL, frame)
            
            # Display the frame (optional)
            if DEBUG_VIDEO:
                # Display the frame with masks
                cv2.imshow("Camera Stream", frame)

            if cv2.waitKey(1) & 0xFF == ord('q') & DEBUG_VIDEO:
                break
            
            elapsed = time.time() - start_time
            time.sleep(max(0, frame_time - elapsed))

    finally:
        cap.release()
        cv2.destroyAllWindows()
        streamer.close(CHANNEL)