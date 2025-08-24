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
import numpy as np


class EfficientVideoStreamer:
    def __init__(self, lcm_url= "udpm://239.255.76.67:7667?recv_addr=192.168.1.101&ttl=1"):
        self.lcm = LCM(lcm_url)

    def send_video_frame(self, channel, frame):
        _, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])

        frame_payload = {
            'shape': frame.shape,
            'dtype': str(frame.dtype),
            'data': lz4.frame.compress(jpeg.tobytes())
        }

        payload_bytes = pickle.dumps(frame_payload)
        
        self.lcm.publish(channel, payload_bytes)

    def subscribe(self, channel, callback):
        def video_callback(channel, data):
            frame_payload = pickle.loads(data)
            
            shape = frame_payload['shape']
            dtype = frame_payload['dtype']
            data = frame_payload['data']

            frame = lz4.frame.decompress(data)
            frame = cv2.imdecode(np.frombuffer(frame, dtype), cv2.IMREAD_COLOR)
            
            frame = frame.reshape(shape[:2] + (3,))

            if len(shape) == 2:
                frame = frame[:,:,0] # If grayscale, keep only one channel

            callback(frame)

        self.lcm.subscribe(channel, video_callback)
    
    def handle(self):
        self.lcm.handle()

    def unsubscribe(self, channel):
        self.lcm.unsubscribe(self.lcm.getSubscription(channel))

    def close(self, channel):
        self.lcm.unsubscribe(channel)
        self.lcm = None
    