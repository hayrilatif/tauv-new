import sys

import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from operators.mavreduction import *
from pymavlink import mavutil
import time
from lcm import LCM
import pickle
import tqdm 
from operators.rc_commander import RCStreamer


def main_loop(shared_config):
    print("mavlink_orchestrator")

    lcm = LCM(shared_config["lcm_url"])
    
    rc_streamer = RCStreamer(shared_config["lcm_url"])
    rc_streamer.subscribe()

    print("Sensor akışı başlatılıyor...")

    
    master = connect_mavlink()

    arm(master)


    while master:
        try:
            raw_imu_data = get_raw_imu(master, hz=10)
            raw_imu_data = pickle.dumps(raw_imu_data)
            lcm.publish("RAW_IMU", raw_imu_data)

            scaled_imu_data = get_scaled_imu(master, hz=10)
            scaled_imu_data = pickle.dumps(scaled_imu_data)
            lcm.publish("SCALED_IMU", scaled_imu_data)


            attitude_data = get_attitude(master, hz=10)
            attitude_data = pickle.dumps(attitude_data)
            lcm.publish("ATTITUDE", attitude_data)
            
            #send this rc_channels.to_list()
            # pitch roll throttle yaw forward lateral
            send_rc_override(master, rc_streamer.rc_channels)
            print("rc sent")

            #print(get_scaled_imu(master, hz=10))

            # LCM mesajlarını işleme
            rc_streamer.handle()

            time.sleep(1/30)  # 100 ms bekleme
            #print("Sensor verisi alındı ve publish edildi.")

        except KeyboardInterrupt:
            print("Program sonlandırılıyor...")
            disarm(master)
            break
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            disarm(master)

    disarm(master)