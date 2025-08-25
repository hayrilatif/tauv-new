CMDS = {
    'MAV_CMD_SET_MESSAGE_INTERVAL': 511,
    'MAV_CMD_COMPONENT_ARM_DISARM': 400
}

MSGS = {
    'GLOBAL_POSITION_INT': 33,
    'SCALED_PRESSURE': 29,
    'SCALED_IMU': 26,
    'RAW_IMU': 27,
    'SCALED_PRESSURE2': 137,
    'ATTITUDE': 30,
    'RC_CHANNELS_RAW': 35,
    'RC_CHANNELS': 65
}

_MODES = {
    "STABILIZE": 0,
    "POSHOLD": 16,
    "MANUAL": 19,
    "DEPTH_HOLD": 2
}

MODES = [
    "STABILIZE",
    "POSHOLD",
    "MANUAL",
    "DEPTH_HOLD"
]

MIN_PWM = 1400
MAX_PWM = 1600

"""
1	Pitch
2	Roll
3	Throttle
4	Yaw
5	Forward
6	Lateral
"""

RC_CHANNELS = {
    "PITCH": 1,
    "ROLL": 2,
    "UP": 3,
    "DOWN": 3,
    "YAW": 4,
    "FORWARD": 5,
    "BACKWARD": 5,
    "LEFT": 6,
    "RIGHT": 6,
}

import sys

import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from dataclasses import dataclass
from pymavlink import mavutil
import time
from lcm import LCM
import pickle
import numpy as np


def get_rc_channel(channel):
    return RC_CHANNELS[channel] - 1


def _send_long_command(master, command, conf=0, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0):
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        command,
        conf, param1, param2, param3, param4, param5, param6, param7
    )

def recv_match(master, type, condition=None, blocking=False, timeout=None) -> dict:
    if not master:
        print("MAVLink bağlantısı yok, RC override atlanıyor.")
        return {}

    m = None
    while not m:
        m = master.recv_match(condition=condition, type=type, blocking=blocking, timeout=timeout)
    return m

def get_raw_imu(master, hz=10):
    # Request RAW_IMU at hz Hz
    _send_long_command(
        master,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        param1=mavutil.mavlink.MAVLINK_MSG_ID_RAW_IMU,
        param2=int(1e6 / hz)
    )

    while True:
        msg = master.recv_match(type='RAW_IMU', blocking=True, timeout=5)
        if msg:
            return msg.to_dict()
        
def get_attitude(master, hz=10) -> dict:
    # Request ATTITUDE at the specified frequency (hz)
    _send_long_command(
        master,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        param1=mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE,
        param2=int(1e6 / hz)  # Interval in microseconds
    )

    # Loop until an ATTITUDE message is received
    while True:
        msg = master.recv_match(type='ATTITUDE', blocking=True, timeout=5)
        if msg:
            # The ATTITUDE message provides angles in radians.
            # Convert them to degrees for the return value.
            return {
                'roll': np.rad2deg(msg.roll),
                'pitch': np.rad2deg(msg.pitch),
                'yaw': np.rad2deg(msg.yaw)
            }

def get_scaled_imu(master, hz=10) -> dict:
    # Request SCALED_IMU at the specified frequency (hz)
    _send_long_command(
        master,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        param1=mavutil.mavlink.MAVLINK_MSG_ID_SCALED_IMU,
        param2=int(1e6 / hz)  # Interval in microseconds
    )

    # Loop until a SCALED_IMU message is received
    while True:
        msg = master.recv_match(type='SCALED_IMU', blocking=True, timeout=5)
        if msg:
            return msg.to_dict()

def arm(master): 
        print("Armlıyor...")
        _send_long_command(master, CMDS['MAV_CMD_COMPONENT_ARM_DISARM'], param1=1) # param2=21196

def disarm(master):  
        print("Disarmlıyor...")
        _send_long_command(master, CMDS['MAV_CMD_COMPONENT_ARM_DISARM'], param1=0) # param2=21196

def set_mode(mode):
    if mode not in MODES:
        raise ValueError(f"Geçersiz mod: {mode}. Geçerli modlar: {MODES}")

    mode_id = _MODES[mode]
    print(f"{mode} moduna geçiliyor...")
    _send_long_command(
        mavutil.mavlink.MAV_CMD_DO_SET_MODE,
        param1=0,  # param2=21196
        param2=mode_id
    )

def send_rc_override(master, rc_channels = [65535] * 18):
    try:
        if not master:
            return

        # Send RC_CHANNELS_OVERRIDE
        master.mav.rc_channels_override_send(
            master.target_system,
            master.target_component,
            *rc_channels
        )
        print("rc_messages_applied: ", rc_channels)

    except Exception as e:
        print(f"RC kanal gönderiminde problem: {str(e)}")

def connect_mavlink(source="/dev/ttyACM0", baud=115200, heartbeat_timeout=10):
    try:
        master = mavutil.mavlink_connection(source, baud=baud)
        if not master:
            print(f"MAVLink bağlantı sorunu. Serial: {source}.")
            return None
        # Wait for heartbeat with timeout
        if not master.wait_heartbeat(timeout=heartbeat_timeout):
            print(f"{source}' den {heartbeat_timeout} saniye boyunca heartbeat alınamadı. Pixhawk bozuk olabilir.")
            return None
        print("Pixhawk yaşıyor.")
        return master
    except Exception as e:
        print(f"Tanımlanamayan MAVLink hatası: {e}")
        return None
