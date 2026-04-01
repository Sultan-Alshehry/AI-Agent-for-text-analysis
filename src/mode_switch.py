
from tkinter import simpledialog, messagebox
import state
from ai_config import set_gemini_api_key, set_analysis_mode

def set_mode(mode: str):
    # Switches analysis mode between 'genai' (Gemini) and 'keybert'.
    # Handles API key prompt and KeyBERT availability check.
    if mode == "genai":
        # If Gemini is not set up, prompt for API key
        if not state.API_KEY:
            key = simpledialog.askstring(
                "Gemini API Key", 
                "Enter your GEMINI_API_KEY:\n\n(This will be saved for future sessions)"
            )
            if not key:
                messagebox.showwarning(
                    "Gemini required",
                    "Gemini API key required to use Gemini mode. Falling back to KeyBERT if available."
                )
                # Try to switch to KeyBERT if Gemini key is not provided
                try:
                    import keybert
                    mode = "keybert"
                except ImportError:
                    messagebox.showerror(
                        "No engine available",
                        "Neither Gemini nor KeyBERT is available."
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

    if mode == "keybert":
        try:
            import keybert
            state.KEYBERT_INSTALLED = True
        except ImportError:
            state.KEYBERT_INSTALLED = False
            messagebox.showwarning(
                "KeyBERT not installed",
                "Please install KeyBERT: pip install keybert sentence-transformers"
            )

    # Update the mode in state
    set_analysis_mode(mode)
    print(f"Switched to mode: {mode}")