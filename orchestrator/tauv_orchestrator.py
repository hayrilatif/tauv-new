import sys
import os
# This line gets the absolute path of the directory the script is in ('.../orchestrator')
# then gets the parent directory ('.../tauv') and adds it to the path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from config import ConfigManager

from colorama import Fore, Style, init

init()

# Define colors to make it easier
BLUE = Fore.BLUE
CYAN = Fore.CYAN
YELLOW = Fore.YELLOW
RESET = Style.RESET_ALL
RED = Fore.RED

print(f"{YELLOW}Starting TAUV Orchestrator...{RESET}")

import multiprocessing
import os
import sys
import time
from deciders.simple_decider import main_loop as simple_decider_main
from derivators.yolo_segmentation import main_loop as yolo_segmentation_main
from operators.mavlink_orchestrator import main_loop as mavlink_orchestrator_main
from origins.camera_streamer import main_loop as camera_streamer_main

def main():
    print(f"""{CYAN}                                                     __
                                     _.-~  )    {YELLOW}    TAUV Orchestrator{RED} - {CYAN}Happy Dolphin
                          _..--~~~~,'   ,-/     _
                       .-'. . . .'   ,-','    ,' )
                     ,'. . . _   ,--~,-'__..-'  ,'
                   ,'. . .  (@)' ---~~~~      ,'
                  /. . . . '~~             ,-'
                 /. . . . .             ,-'
                ; . . . .  - .        ,'
               : . . . .       _     /
              . . . . .          `-.:
             . . . ./  - .          )
            .  . . |  _____..---.._/ 
{BLUE}      ~---~~~~----~~~~             ~~{RESET}""")
    print("\n")
    print(f"{CYAN}Welcome to the TAUV Orchestrator!{RESET}")
    print("")

    # Initialize shared configuration
    config_manager = ConfigManager()
    config_manager.initialize_config()

    # Start camera streamer in a separate process
    camera_streamer_process = multiprocessing.Process(target=camera_streamer_main, args=(config_manager.shared_config,))
    camera_streamer_process.start()
    print("Camera Streamer started.")

    

    # Start the YOLO segmentation in a separate process
    yolo_process = multiprocessing.Process(target=yolo_segmentation_main, args=(config_manager.shared_config,))
    yolo_process.start()
    print("YOLO Segmentation started.")

    # Start the Mavlink orchestrator in a separate process
    mavlink_process = multiprocessing.Process(target=mavlink_orchestrator_main, args=(config_manager.shared_config,))
    mavlink_process.start()
    print("Mavlink Orchestrator started.")

    # Start the simple decider in a separate process
    decider_process = multiprocessing.Process(target=simple_decider_main, args=(config_manager.shared_config,))
    decider_process.start()
    print("Simple Decider started.")

    try:
        while True:
            time.sleep(1)  # Keep the main process alive
    except KeyboardInterrupt:
        print("Shutting down TAUV Orchestrator...")
        camera_streamer_process.terminate()
        camera_streamer_process.join()

        yolo_process.terminate()
        yolo_process.join()

        mavlink_process.terminate()
        mavlink_process.join()

        decider_process.terminate()
        decider_process.join()
        print("Orchestrator stopped.")

if __name__ == "__main__":
    main()