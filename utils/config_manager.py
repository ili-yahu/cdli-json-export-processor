import json
import os

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "database_path": None,
    "logging_enabled": False,
    "breadcrumb_enabled": True, 
    "default_table": "identification"
}

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")
