
from typing import Literal
import state
from data_manager import DataManager


"""
AI Configuration Module
-----------------------
Handles all AI-related configuration and setup, including:
- Analysis mode management (Gemini vs BERTs)
- Mode validation and fallback logic
- API key management
- Environment setup
"""


AnalysisMode = Literal["genai", "berts"]
LEGACY_MODE_ALIASES = {"hybrid": "berts"}


def normalize_analysis_mode(mode: str) -> AnalysisMode:
    normalized_mode = LEGACY_MODE_ALIASES.get(mode, mode)
    if normalized_mode not in ("genai", "berts"):
        raise ValueError("mode must be 'genai' or 'berts'")
    return normalized_mode


def get_mode_display_name(mode: str) -> str:
    return "Gemini" if normalize_analysis_mode(mode) == "genai" else "BERTs"


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


def validate_and_resolve_mode(requested_mode: str) -> AnalysisMode:
    requested_mode = normalize_analysis_mode(requested_mode)

    if requested_mode == "genai":
        if state.API_KEY:
            return "genai"
        # Fallback to BERTs if Gemini key is missing and BERTs dependencies are available
        if is_keybert_available() and is_bertopic_available():
            print("Gemini API key not set. Falling back to BERTs mode.")
            return "berts"
        raise EnvironmentError(
            "Gemini API key not set and BERTs mode dependencies (KeyBERT + BERTopic) are not available."
        )
    
    elif requested_mode == "berts":
        if is_keybert_available() and is_bertopic_available():
            return "berts"
        # Fallback to genai if BERTs dependencies are not available
        if state.API_KEY:
            print("BERTs mode dependencies not available. Falling back to Gemini.")
            return "genai"
        raise EnvironmentError(
            "BERTs mode requires KeyBERT and BERTopic, and neither is available. Gemini API key also not set."
        )
    
    else:
        raise ValueError(f"Invalid mode: {requested_mode}")


def get_analysis_mode() -> AnalysisMode:
    # Returns current analysis mode, defaulting based on API key availability.
    # Prefers saved mode if available.
    if state.ANALYSIS_MODE in ("genai", "berts", "hybrid"):
        state.ANALYSIS_MODE = normalize_analysis_mode(state.ANALYSIS_MODE)
        return state.ANALYSIS_MODE

    saved_mode = DataManager.get_analysis_mode()
    if saved_mode in ("genai", "berts"):
        state.ANALYSIS_MODE = saved_mode
        return saved_mode

    # Prefer BERTs mode if both KeyBERT and BERTopic are available
    if is_keybert_available() and is_bertopic_available():
        state.ANALYSIS_MODE = "berts"
        return "berts"
    # Otherwise use genai if API key is available
    if state.API_KEY:
        state.ANALYSIS_MODE = "genai"
        return "genai"
    # Final fallback to BERTs even if dependencies might not be available
    # (will be caught by validate_and_resolve_mode)
    state.ANALYSIS_MODE = "berts"
    return "berts"


def set_analysis_mode(mode: str) -> AnalysisMode:
    # Set analysis mode to 'genai' or 'berts'.
    mode = normalize_analysis_mode(mode)
    state.ANALYSIS_MODE = mode
    DataManager.set_analysis_mode(mode)
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
    state.ANALYSIS_MODE = mode

    if mode == "genai":
        return "genai"

    return "berts"
    
