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


class RCStreamer:
    def __init__(self, lcm_url= "udpm://239.255.76.67:7667?recv_addr=192.168.1.101&ttl=1"):
        self.lcm = LCM(lcm_url)
        self.rc_channels = [65535] * 18

    def send_rc(self, rc: list, channel = "RC_CHANNEL"):
        rc_data = pickle.dumps(rc)
        self.lcm.publish(channel, rc_data)

    def subscribe(self, callback = None, channel = "RC_CHANNEL"):
        print("Subscribing to RC_CHANNEL")
        def rc_callback(channel, data):
            print("rc message received over lcm")
            rc_data = pickle.loads(data)
            self.rc_channels = rc_data
            if callback:
                callback(rc_data)

        self.lcm.subscribe(channel, rc_callback)
    
    def handle(self):
        self.lcm.handle_timeout(10)

    def unsubscribe(self, channel):
        self.lcm.unsubscribe(self.lcm.getSubscription(channel))

    def close(self, channel):
        self.lcm.unsubscribe(channel)
        self.lcm = None
    