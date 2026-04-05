
from typing import Literal
import state
from data_manager import DataManager


"""
AI Configuration Module
-----------------------
Handles all AI-related configuration and setup, including:
- Analysis mode management (Gemini vs Hybrid)
- Mode validation and fallback logic
- API key management
- Environment setup
"""


AnalysisMode = Literal["genai", "hybrid"]


def is_keybert_available() -> bool:
    #Check if KeyBERT is installed and available.
    try:
        import keybert
        return True
    except ImportError:
        return False


def is_bertopic_available() -> bool:
    #Check if BERTopic is installed and available.
    try:
        import bertopic
        return True
    except ImportError:
        return False


def validate_and_resolve_mode(requested_mode: AnalysisMode) -> AnalysisMode:
    if requested_mode == "genai":
        if state.API_KEY:
            return "genai"
        # Fallback to hybrid if Gemini key is missing and hybrid dependencies are available
        if is_keybert_available() and is_bertopic_available():
            print("Gemini API key not set. Falling back to hybrid mode.")
            return "hybrid"
        raise EnvironmentError(
            "Gemini API key not set and hybrid mode dependencies (KeyBERT + BERTopic) are not available."
        )
    
    elif requested_mode == "hybrid":
        if is_keybert_available() and is_bertopic_available():
            return "hybrid"
        # Fallback to genai if hybrid dependencies are not available
        if state.API_KEY:
            print("Hybrid mode dependencies not available. Falling back to Gemini.")
            return "genai"
        raise EnvironmentError(
            "Hybrid mode requires KeyBERT and BERTopic, and neither is available. Gemini API key also not set."
        )
    
    else:
        raise ValueError(f"Invalid mode: {requested_mode}")


def get_analysis_mode() -> AnalysisMode:
    # Returns current analysis mode, defaulting based on API key availability.
    # Prefers saved mode if available.
    if state.ANALYSIS_MODE in ("genai", "hybrid"):
        return state.ANALYSIS_MODE
    # Prefer hybrid mode if both KeyBERT and BERTopic are available
    if is_keybert_available() and is_bertopic_available():
        state.ANALYSIS_MODE = "hybrid"
        return "hybrid"
    # Otherwise use genai if API key is available
    if state.API_KEY:
        state.ANALYSIS_MODE = "genai"
        return "genai"
    # Final fallback to hybrid even if dependencies might not be available
    # (will be caught by validate_and_resolve_mode)
    state.ANALYSIS_MODE = "hybrid"
    return "hybrid"


def set_analysis_mode(mode: str) -> AnalysisMode:
    # Set analysis mode to 'genai' or 'hybrid'.
    if mode not in ("genai", "hybrid"):
        raise ValueError("mode must be 'genai' or 'hybrid'")
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
    if mode == "hybrid":
        print("Using Hybrid (KeyBERT + BERTopic) for analysis.")
        return "hybrid"
    
