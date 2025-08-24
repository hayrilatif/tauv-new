import sys

import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from ultralytics import YOLO
from PIL import Image
import requests
from io import BytesIO
import yaml
import numpy as np
from lcm import LCM
import cv2
import pickle
import lz4.frame
from origins.efficient_streamer import EfficientVideoStreamer
import time

CONFIDENCE_THRESHOLD = 0.4
IOU_THRESHOLD = 0.45
AG_NMS = False
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
DEBUG_VIDEO = True

empty_image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH), dtype=np.uint8)

def video_callback(streamer, model, frame):
    # data = byte dizisi, yeniden numpy array yap

    results = model(frame, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD, agnostic_nms=AG_NMS, verbose=False)

    # logic or all results vectorized
    results = results[0]
    if results.masks is not None:
        masks = results.masks.data.cpu().numpy()
        masks = masks[masks.sum(axis=(1, 2)) > 50]
        masks = masks.sum(axis=0) > 0.5  # Thresholding masks
        masks = masks.astype(np.uint8) * 255  # Convert to binary mask

    else:
        masks = empty_image

    # send masks over LCM
    streamer.send_video_frame("segmentation_stream", masks)

    if DEBUG_VIDEO:
        # Display the frame with masks
        cv2.imshow("Received Video", masks)
    
    if cv2.waitKey(1) & 0xFF == ord('q') & DEBUG_VIDEO:
        cv2.destroyAllWindows()
        exit(0)

def main_loop(shared_config):
    print("yolo_segmentation")
    
    model = YOLO('derivators/weights/yolo/best.pt')
    streamer = EfficientVideoStreamer(shared_config["lcm_url"])
    
    streamer.subscribe("video_stream", lambda frame: video_callback(streamer, model, frame))

    try:
        while True:
            streamer.handle()
    except KeyboardInterrupt:
        print("Program terminated by user.")
        cv2.destroyAllWindows()