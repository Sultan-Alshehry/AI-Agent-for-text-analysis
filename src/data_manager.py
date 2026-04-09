
import json
from pathlib import Path
from typing import Optional, Dict, Any

"""
Data Manager Module
-------------------
Handles persistent storage of user data (API keys, settings, etc.)
in JSON format.

Responsibilities:
- Load/save API keys from user_data.json
- Load/save application settings
- Ensure data persistence across sessions
"""


class DataManager:
    #Manages persistent user configuration data.
    
    DATA_FILE = Path(__file__).parent / "user_data.json"
    
    # Default structure for user_data.json
    DEFAULT_CONFIG = {
        "api_key": "",
        "analysis_mode": "genai",
        "settings": {}
    }
    
    @classmethod
    def _ensure_file_exists(cls) -> None:
        #Create user_data.json with default structure if it doesn't exist.
        if not cls.DATA_FILE.exists():
            cls.DATA_FILE.write_text(json.dumps(cls.DEFAULT_CONFIG, indent=4))
    
    @classmethod
    def _load_data(cls) -> Dict[str, Any]:
        #Load data from user_data.json.
        cls._ensure_file_exists()
        try:
            with open(cls.DATA_FILE, 'r') as f:
                data = json.load(f)
            # Ensure all required keys exist
            for key in cls.DEFAULT_CONFIG:
                if key not in data:
                    data[key] = cls.DEFAULT_CONFIG[key]
            return data
        except (json.JSONDecodeError, IOError):
            return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def _save_data(cls, data: Dict[str, Any]) -> None:
        # Save data to user_data.json.
        cls._ensure_file_exists()
        with open(cls.DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    
    @classmethod
    def get_api_key(cls) -> str:
        # Get saved API key from user_data.json.
        data = cls._load_data()
        return data.get("api_key", "").strip()
    
    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        # Save API key to user_data.json.
        data = cls._load_data()
        data["api_key"] = api_key.strip()
        cls._save_data(data)
    
    @classmethod
    def get_analysis_mode(cls) -> str:
        # Get saved analysis mode from user_data.json.
        data = cls._load_data()
        mode = data.get("analysis_mode", "genai")
        if mode == "hybrid":
            mode = "berts"
            data["analysis_mode"] = mode
            cls._save_data(data)
        return mode
    
    @classmethod
    def set_analysis_mode(cls, mode: str) -> None:
        # Save analysis mode to user_data.json.
        if mode == "hybrid":
            mode = "berts"
        data = cls._load_data()
        data["analysis_mode"] = mode
        cls._save_data(data)
    
    @classmethod
    def get_setting(cls, key: str, default: Any = None) -> Any:
        # Get a specific setting from user_data.json.
        data = cls._load_data()
        return data.get("settings", {}).get(key, default)
    
    @classmethod
    def set_setting(cls, key: str, value: Any) -> None:
        # Save a specific setting to user_data.json.
        data = cls._load_data()
        if "settings" not in data:
            data["settings"] = {}
        data["settings"][key] = value
        cls._save_data(data)
    
    @classmethod
    def clear_api_key(cls) -> None:
        # Clear saved API key (for security or re-entry).
        cls.set_api_key("")
