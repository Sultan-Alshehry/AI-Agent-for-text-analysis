import summary_saver
import file_reader
import ai_config
from pathlib import Path
import state

# We run the setup logic first to ensure the user has configured their AI settings before the app runs.
ai_config.setup_environment()

# We import the AI module ONLY AFTER the setup is complete
import send_prompt_online

# Main Execution Logic
text = file_reader.read_file("../python_test/bible.txt")

# Ask user to choose analysis mode
print("\nChoose analysis mode:")
print("1. AI (Gemini) - provides summary, keywords, and topics")
print("2. KeyBERT - extracts keywords only (no API key needed)")
choice = input("\nEnter your choice (1 or 2): ").strip()

mode = "genai" if choice == "1" else "keybert" if choice == "2" else "genai"

# Analyze the text
analysis = send_prompt_online.analyze_text(text, mode=mode)

# Display results based on mode
if mode == "genai":
    print("\n=== AI Analysis Results ===")
    print("Summary:\n", analysis.get("summary", ""))
    print("\nTopics:\n", analysis.get("topics", []))
    print("Keywords (AI):", analysis.get("ai_keywords", []))
    print(f"Number of tokens used: {analysis.get('token_count')}")
else:
    print("\n=== KeyBERT Analysis Results ===")
    print("Keywords (KeyBERT):", analysis.get("keybert_keywords", []))

saved_path = summary_saver.save_summary(analysis)
print(f"\nSuccess! Summary saved to: {saved_path}")
