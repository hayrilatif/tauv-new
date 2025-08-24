import multiprocessing as mp
import time
import signal
import sys
from dataclasses import dataclass
from typing import Dict, Any
import yaml

class ConfigManager:
    def __init__(self):
        self.manager = mp.Manager()
        self.shared_config = self.manager.dict()
        self.stop_event = mp.Event()
        self.processes = []

    def initialize_config(self, config_file: str = 'orchestrator/config.yaml'):
        """Initialize shared configuration"""
        # load initial configuration from a YAML file
        with open(config_file, 'r') as file:
            config_data = yaml.safe_load(file)
        # update shared_config with the loaded configuration
        self.shared_config.update(config_data)
        print("Configuration initialized:", dict(self.shared_config))
        
    def update_config(self, key: str, value: Any):
        """Update configuration at runtime"""
        if key in self.shared_config:
            old_value = self.shared_config[key]
            self.shared_config[key] = value
            print(f"Config updated: {key} = {value} (was {old_value})")
        else:
            print(f"Warning: Unknown config key '{key}'")
            
    def get_config(self, key: str):
        """Get current configuration value"""
        return self.shared_config.get(key)
        
    def get_all_config(self):
        """Get all current configuration"""
        return dict(self.shared_config)
