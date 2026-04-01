
from typing import Literal
import json as j
from pathlib import Path
import state as t
import state

AnalysisMode = Literal["genai", "keybert"]


def get_analysis_mode() -> AnalysisMode:
    mode = state.ANALYSIS_MODE
    if mode in ("genai", "keybert"):
        return mode

    if t.API_KEY:
        return "genai"

    return "keybert"


def set_analysis_mode(mode: str) -> AnalysisMode:
    if mode not in ("genai", "keybert"):
        raise ValueError("mode must be 'genai' or 'keybert'")
    state.ANALYSIS_MODE = mode
    return mode


def set_gemini_api_key(api_key: str) -> None:
    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key cannot be empty")
    
    # Basic validation: Gemini keys are typically longer
    api_key = api_key.strip()
    if len(api_key) < 20:
        raise ValueError("Gemini API key seems too short. Please verify the key.")
    t.API_KEY = api_key
    #print(t.API_KEY)
    #os.environ["GEMINI_API_KEY"] = api_key
    
    


def setup_environment() -> AnalysisMode:
    # If user has already selected mode (or has key), use that.
    current_mode = get_analysis_mode()
    if current_mode == "genai" and t.API_KEY:
        return "genai"
    if current_mode == "keybert":
        return "keybert"

    # no mode set yet: prompt user
    print("Welcome to AITY! Select analysis mode:")
    print("1. Gemini API (online, needs GEMINI_API_KEY)")
    print("2. KeyBERT (local, no API key needed)")

    choice = input("Please choose an option (1 or 2): ").strip()

    if choice == "1":
        api_key = input("Enter your Gemini API key: ").strip()
        if not api_key:
            raise ValueError("Gemini API key cannot be empty")
        set_gemini_api_key(api_key)
        set_analysis_mode("genai")
        return "genai"

    if choice == "2":
        set_analysis_mode("keybert")
        return "keybert"

    raise ValueError("Invalid choice. Choose 1 or 2.")