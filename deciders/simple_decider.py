import sys

import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
from lcm import LCM
import cv2
import time
import cv2
import pickle
import lz4.frame
import yaml
from  origins.efficient_streamer import EfficientVideoStreamer
from operators.rc_commander import RCCommander

class Simple():
  """
  pca componenet bul, line fit et, egimini bul. egimini motor komutu icin kullan
  Format: HW
  """

  def __init__(self, shape):
    self.pca = PCA(n_components=2)
    self.center_point = np.array(shape) / 2
    self.shape = shape

  def __calculate_point_cloud(self, segmap):
    segmap = segmap.squeeze()
    y_coords, x_coords = np.where(segmap > 0)
    y_coords = segmap.shape[0] - y_coords

    coordinates = np.vstack((x_coords, y_coords)).T   

    return (x_coords, y_coords), coordinates

  def __pca_fit(self, coordinates):
    self.pca.fit(coordinates)
    first_component = self.pca.components_[0]
    return (self.pca.mean_, first_component)

  def __calculate_things(self, mean_point, first_component):
    steer_angle = (np.arctan(first_component[0]/first_component[1])) * 180 / np.pi
    horizontal_error = mean_point[0] - self.center_point[0]

    return horizontal_error, steer_angle

  def evaluate(self, segmap):
    point_cloud = self.__calculate_point_cloud(segmap)
    mean_point, first_component = self.__pca_fit(point_cloud[1])
    return {key:value for key, value in zip(["horizontal_error", "steer_angle", "mean_point"], self.__calculate_things(mean_point, first_component) + (mean_point,))}


def simple_decider_callback(streamer, frame, commander: RCCommander, simple: Simple):
    # predict with simple decider    
    results = simple.evaluate(frame)

    horizontal_error = results["horizontal_error"]
    steer_angle = results["steer_angle"]

    if abs(steer_angle) > 12:
      if horizontal_error <0:
        yaw = "<-"
        #drone_commands.append((DroneCommand.COMMAND_YAW, MAX_RC, 0.0, 0.0, 1.0))
        # send drone command to turn left
        #commander.send_command(DroneCommand.COMMAND_YAW, MAX_RC, 0.0, 0.0, 1.0)
      else:
        yaw = "->"
        #drone_commands.append((DroneCommand.COMMAND_YAW, -MAX_RC, 0.0, 0.0, 1.0))
    else:
      yaw = "."
      #drone_commands.append((DroneCommand.COMMAND_YAW, 0.0, 0.0, 0.0, 1.0))

    if abs(horizontal_error) > 50:
      if horizontal_error < 0:
        strafe = "<-"
        #drone_commands.append((DroneCommand.COMMAND_STRAFE, -MAX_RC, 0.0, 0.0, 1.0))
      else:
        strafe = "->"
        #drone_commands.append((DroneCommand.COMMAND_STRAFE, MAX_RC, 0.0, 0.0, 1.0))
    else:
      strafe = "."
      #drone_commands.append((DroneCommand.COMMAND_STRAFE, 0.0, 0.0, 0.0, 1.0))

    if abs(horizontal_error) < 50 and abs(steer_angle) < 12:
      throttle = "/\\"
      #drone_commands.append((DroneCommand.COMMAND_FORWARD, MAX_RC, 0.0, 0.0, 1.0))
    else:
      throttle = "."
      #drone_commands.append((DroneCommand.COMMAND_FORWARD, 0.0, 0.0, 0.0, 1.0))

    print(f"""
        ------------------------------------------------
           horizontal_error: {horizontal_error}
                steer_angle: {steer_angle}
              
                        yaw: {yaw}
                     strafe: {strafe}
                   throttle: {throttle}
        ------------------------------------------------
    """)


    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Convert to BGR for visualization
    frame = frame.astype(np.uint8)


    print(f"Horizontal Error: {results['horizontal_error']}, Steer Angle: {results['steer_angle']}")

    #draw mean point
    results["mean_point"] = results["mean_point"].astype(int).tolist()
    results["mean_point"][1] = frame.shape[0] - results["mean_point"][1]  # Adjust y-coordinate for OpenCV
    frame = cv2.circle(frame, list(results["mean_point"]), radius=10, color=(0, 255, 0), thickness=-1)

    #draw first component
    first_component_end = (results["mean_point"] + results["steer_angle"] * np.array([np.sin(np.deg2rad(-results["steer_angle"])), np.cos(np.deg2rad(-results["steer_angle"]))]) * 100).astype(int)
    frame = cv2.line(frame, tuple(results["mean_point"]), tuple(first_component_end), color=(0, 0, 255), thickness=3)

    #draw center point
    center_point = (320, 240)  # Assuming the center point is at (320, 240)
    frame = cv2.circle(frame, center_point, radius=10, color=(255, 0, 0), thickness=-1)

    # vertical center line
    frame = cv2.line(frame, (320, 0), (320, 480), color=(255, 255, 0), thickness=1)

    # draw horizontal error line
    horizontal_error_end = (320 + int(results["horizontal_error"]), 240)
    frame = cv2.line(frame, (320, 240), horizontal_error_end, color=(255, 0, 255), thickness=1)

    cv2.imshow("Received Video", frame)


    streamer.send_video_frame("simple_decider", frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
      cv2.destroyAllWindows()
      exit(0)

def main_loop(shared_config):
  print("simple_decider")

  simple = Simple((640, 480))
  commander = RCCommander()
  streamer = EfficientVideoStreamer()

  streamer.subscribe("segmentation_stream", lambda frame: simple_decider_callback(streamer, frame, commander, simple))

  while True:
      try:
          streamer.handle()
      except KeyboardInterrupt:
          print("Program sonlandırılıyor...")
          break
      except Exception as e:
          print(f"Hata oluştu: {str(e)}")


def main_loop():
  print("simple_decider")

  simple = Simple((640, 480))
  commander = RCCommander()
  streamer = EfficientVideoStreamer()

  streamer.subscribe("segmentation_stream", lambda frame: simple_decider_callback(streamer, frame, commander, simple))

  while True:
      try:
          streamer.handle()
      except KeyboardInterrupt:
          print("Program sonlandırılıyor...")
          break
      except Exception as e:
          print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    main_loop()