import sys

import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from lcm import LCM
import cv2
import numpy as np
import pickle
import lz4.frame
from origins.efficient_streamer import EfficientVideoStreamer



CHANNEL = "video_stream"
WIDTH = 640
HEIGHT = 480
CHANNEL_TYPE = 'BGR'  # OpenCV kullanıyor, BGR formatı

def video_callback(frame):
    # data = byte dizisi, yeniden numpy array yap
    cv2.imshow("Received Video", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        exit(0)

def main_loop():
    print("video_viewer")

    channel = sys.argv[1]

    if sys.argv[2]:
        lcm_url = sys.argv[2]
    else:
        lcm_url = "udpm://239.255.76.67:7667?recv_addr=192.168.1.101&ttl=1"

    streamer = EfficientVideoStreamer(lcm_url)
    streamer.subscribe(CHANNEL, video_callback)

    try:
        while True:
            streamer.handle()
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main_loop()