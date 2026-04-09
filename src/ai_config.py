
from typing import Literal
import state
from data_manager import DataManager


"""
AI Configuration Module
-----------------------
Handles all AI-related configuration and setup, including:
- Analysis mode management (Gemini vs KeyBERT)
- Mode validation and fallback logic
- API key management
- Environment setup
"""


AnalysisMode = Literal["genai", "keybert"]


def is_keybert_available() -> bool:
    #Check if KeyBERT is installed and available.
    try:
        import keybert
        return True
    except ImportError:
        return False


def validate_and_resolve_mode(requested_mode: AnalysisMode) -> AnalysisMode:
    if requested_mode == "genai":
        if state.API_KEY:
            return "genai"
        # Fallback to KeyBERT if Gemini key is missing
        if is_keybert_available():
            print("Gemini API key not set. Falling back to KeyBERT.")
            return "keybert"
        raise EnvironmentError(
            "Gemini API key not set and KeyBERT is not available."
        )
    
    elif requested_mode == "keybert":
        if is_keybert_available():
            return "keybert"
        # Fallback to Gemini if KeyBERT is not installed
        if state.API_KEY:
            print("KeyBERT not installed. Falling back to Gemini.")
            return "genai"
        raise EnvironmentError(
            "KeyBERT not installed and Gemini API key not set."
        )
    
    else:
        raise ValueError(f"Invalid mode: {requested_mode}")


def get_analysis_mode() -> AnalysisMode:
    # Returns current analysis mode, defaulting based on API key availability.
    # Prefers saved mode if available.
    if state.ANALYSIS_MODE in ("genai", "keybert"):
        return state.ANALYSIS_MODE
    if state.API_KEY:
        state.ANALYSIS_MODE = "genai"
        return "genai"
    state.ANALYSIS_MODE = "keybert"
    return "keybert"


def set_analysis_mode(mode: str) -> AnalysisMode:
    # Set analysis mode to 'genai' or 'keybert'.
    if mode not in ("genai", "keybert"):
        raise ValueError("mode must be 'genai' or 'keybert'")
    state.ANALYSIS_MODE = mode
    return mode


def set_gemini_api_key(api_key: str) -> None:
    # Set the Gemini API key in state with basic validation.
    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key cannot be empty")
    
    # Basic validation: Gemini keys are typically longer
    api_key = api_key.strip()
    if len(api_key) < 20:
        raise ValueError("Gemini API key seems too short. Please verify the key.")
    state.API_KEY = api_key
    # Persist API key to user_data.json
    DataManager.set_api_key(api_key)

    
def setup_environment() -> AnalysisMode:
    # Initialize the AI environment and return the selected analysis mode.
    # Load saved API key from persistent storage
    saved_key = DataManager.get_api_key()
    if saved_key:
        state.API_KEY = saved_key
    
    mode = get_analysis_mode()
    if mode == "genai" and state.API_KEY:
        print("Using Gemini API for analysis.")
        return "genai"
    if mode == "keybert":
        print("Using KeyBERT for analysis.")
        return "keybert"
    
