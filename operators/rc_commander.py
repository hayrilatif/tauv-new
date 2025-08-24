import sys

import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from lcm import LCM
from operators.mavreduction import RCChannels

class RCCommander:
    def __init__(self, channel= "udpm://239.255.76.67:7667?recv_addr=192.168.1.101&ttl=1"):
        self.lcm = LCM(channel)

    def send_rc(self, rc_channels: RCChannels):
        self.lcm.publish("RC_CHANNELS", self.rc_channels.to_bytes())

    def reset_rc(self):
        rc_channels = RCChannels()
        self.lcm.publish("RC_CHANNELS", rc_channels.to_bytes())
        print("RC channels reset to default values.")