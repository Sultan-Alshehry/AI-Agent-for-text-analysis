import os
from pathlib import Path
import json
import summary_saver
import send_prompt_online
from ai_config import get_analysis_mode, setup_environment
from file_reader import read_file
import state as t



def get_analysis_result(filepath: str, mode: str = None):
    print(filepath, mode)
    if mode is None:
        mode = get_analysis_mode()

    original_mode = mode
    if mode == "genai" and not t.API_KEY:
        # Try fallback to keybert
        try:
            import keybert
            print("Gemini API key not set. Falling back to KeyBERT.")
            mode = "keybert"
        except ImportError:
            raise EnvironmentError("Gemini mode requires GEMINI_API_KEY environment variable, and KeyBERT is not available as fallback.")
    elif mode == "keybert":
        try:
            import keybert
        except ImportError:
            # Try fallback to genai if key available
            if os.environ.get("GEMINI_API_KEY"):
                print("KeyBERT not installed. Falling back to Gemini.")
                mode = "genai"
            else:
                raise EnvironmentError("KeyBERT is not installed, and Gemini API key is not set.")

    text = read_file(filepath)
    if not text.strip():
        raise ValueError("Input file is empty")

    # Try analysis with selected mode
    try:
        analysis = send_prompt_online.analyze_text(text, mode=mode)
    except EnvironmentError as e:
        # Only fallback on explicit authentication failures
        error_msg = str(e).lower()
        if "invalid gemini api key" in error_msg or "authentication" in error_msg:
            print(f"Gemini API authentication error: {e}")
            print("Falling back to KeyBERT...")
            try:
                import keybert
                mode = "keybert"
                analysis = send_prompt_online.analyze_text(text, mode=mode)
            except ImportError:
                raise EnvironmentError("Gemini API key is invalid and KeyBERT is not installed as fallback.") from e
        else:
            # Re-raise other environment errors (not auth-related)
            raise

    result_payload = {
        "summary": analysis.get("summary", ""),
        "keywords": analysis.get("keywords", []),
        "topics": analysis.get("topics", []),
        "token_count": analysis.get("token_count"),
        "mode": mode,
        "source_file": str(Path(filepath).resolve()),
    }

    # Create unique output filename based on input file
    filename = Path(filepath).stem
    src_dir = Path(__file__).resolve().parent
    output_path = src_dir / "output" / "summary" / f"{filename}.json"
    
    saved_path = summary_saver.save_summary(result_payload, output_path)

    print(f"Success! Analysis mode={mode} saved to: {saved_path}")
    if mode == "genai":
        print(f"Number of tokens used: {result_payload.get('token_count')}")

    return saved_path