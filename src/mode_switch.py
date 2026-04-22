from tkinter import simpledialog, messagebox
import state
from ai_config import get_mode_display_name, normalize_analysis_mode, set_gemini_api_key, set_analysis_mode


"""
Mode Switch Module
------------------
Handles switching between analysis modes (Gemini vs BERTs) in the UI.

Provides functions for mode switching with API key management
and dependency checks for BERTs mode.
"""


# -------------------------------------------------------------------
# Mode switching functions
# -------------------------------------------------------------------


def set_mode(mode: str):
    # Switches analysis mode between 'genai' (Gemini) and 'berts' (KeyBERT + BERTopic).
    # Handles API key prompt and BERTs mode availability check.
    mode = normalize_analysis_mode(mode)

    if mode == "genai":
        if not state.API_KEY:
            key = simpledialog.askstring(
                "Gemini API Key", 
                "Enter your GEMINI_API_KEY:\n\n(This will be saved for future sessions)"
            )
            if not key:
                messagebox.showwarning(
                    "Gemini required",
                    "Gemini API key required to use Gemini mode. Falling back to BERTs mode if available."
                )
                try:
                    import keybert
                    import bertopic
                    mode = "berts"
                except ImportError:
                    messagebox.showerror(
                        "No engine available",
                        "Neither Gemini nor BERTs mode dependencies are available."
                    )
                    return
            else:
                try:
                    set_gemini_api_key(key)
                    messagebox.showinfo(
                        "Success",
                        "API key saved! You won't need to enter it again."
                    )
                except ValueError as e:
                    messagebox.showerror("Invalid API Key", str(e))
                    return

    if mode == "berts":
        try:
            import keybert
            import bertopic
            state.KEYBERT_INSTALLED = True
        except ImportError:
            state.KEYBERT_INSTALLED = False
            messagebox.showwarning(
                "BERTs mode dependencies not available",
                "Please install required packages: pip install keybert sentence-transformers bertopic"
            )

    set_analysis_mode(mode)


def change_API_key():
    """Changes the API key for Gemini mode."""
    key = simpledialog.askstring(
                "Gemini API Key", 
                "Enter your GEMINI_API_KEY:\n\n(This will be saved for future sessions)"
            )
    try:
        set_gemini_api_key(key)
        messagebox.showinfo(
            "Success",
            "API key saved! You won't need to enter it again."
            )
    except ValueError as e:
        messagebox.showerror("Invalid API Key", str(e))
        return