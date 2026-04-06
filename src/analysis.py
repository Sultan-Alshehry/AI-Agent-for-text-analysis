
from pathlib import Path
import json
import summary_saver
import send_prompt_online
from ai_config import get_analysis_mode, validate_and_resolve_mode
from file_reader import read_file
import state


"""
Text Analysis Module
--------------------
Core analysis module that orchestrates the text analysis pipeline:
- Reads files (TXT, PDF)
- Selects and validates analysis mode (Gemini or BERTs)
- Executes analysis with fallback handling
- Saves results to JSON

This module bridges file input with AI processing and result storage.
"""


def get_analysis_result(filepath: str, mode: str = None):
    # Analyses the given file using the selected mode ('genai' or 'berts').
    # Returns the path to the saved JSON summary.
    
    print(filepath, mode)
    if mode is None:
        mode = get_analysis_mode()

    # Validate mode and apply fallback if needed
    mode = validate_and_resolve_mode(mode)

    # Read file content
    text = read_file(filepath)
    if not text.strip():
        raise ValueError("Input file is empty")

    # Analyze with selected mode
    try:
        analysis = send_prompt_online.analyze_text(text, mode=mode)
    except EnvironmentError as e:
        # Handle authentication errors with fallback
        error_msg = str(e).lower()
        if "invalid" in error_msg or "authentication" in error_msg:
            print(f"Authentication error: {e}")
            print("Attempting fallback mode...")
            fallback_mode = "berts" if mode == "genai" else "genai"
            try:
                fallback_mode = validate_and_resolve_mode(fallback_mode)
                analysis = send_prompt_online.analyze_text(text, mode=fallback_mode)
                mode = fallback_mode
            except Exception as fallback_error:
                raise EnvironmentError(
                    f"Analysis failed with {mode} and fallback also failed: {fallback_error}"
                ) from e
        else:
            raise

    # Prepare result payload
    result_payload = {
        "summary": analysis.get("summary", ""),
        "keywords": analysis.get("keywords", []),
        "topics": analysis.get("topics", []),
        "token_count": analysis.get("token_count"),
        "mode": mode,
        "source_file": str(Path(filepath).resolve()),
    }

    # Save JSON summary
    filename = Path(filepath).stem
    src_dir = Path(__file__).resolve().parent
    output_path = src_dir / "output" / "summary" / f"{filename}.json"
    saved_path = summary_saver.save_summary(result_payload, output_path)

    print(f"Success! Analysis mode={mode} saved to: {saved_path}")
    if mode == "genai":
        print(f"Number of tokens used: {result_payload.get('token_count')}")

    return saved_path


def json_to_text(file_path: str):
    # Parse JSON analysis result file and extract components.
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
        summary = data.get("summary", "")
        keywords = data.get("keywords", [])
        topics = data.get("topics", [])
        
        return summary, keywords, topics