<<<<<<< HEAD
import os
from pathlib import Path

import send_prompt_online
=======
import json
>>>>>>> 02c2ccca1685eadbc1e79cc9355e23a42d371087
import summary_saver
import ai_config

<<<<<<< HEAD
base_dir = Path(__file__).resolve().parent
bible_path = base_dir.parent / "python_test" / "bible.txt"
with open(bible_path, "r", encoding="utf-8") as file:
=======
# We run the setup logic first to ensure the user has configured their AI settings before the app runs.
ai_config.setup_environment()

# We import the AI module ONLY AFTER the setup is complete
import send_prompt_online

# Main Execution Logic
with open("../python_test/bible.txt", "r", encoding="utf-8") as file:
>>>>>>> 02c2ccca1685eadbc1e79cc9355e23a42d371087
    text = file.read()

# mode options: 'genai', 'keybert'
analysis = send_prompt_online.analyze_text(text, mode="keybert")

print("Summary:\n", analysis.get("summary", ""))
print("Topics:\n", analysis.get("topics", []))
print("Keywords (KeyBERT):", analysis.get("keybert_keywords", []))
print("Keywords (AI):", analysis.get("ai_keywords", []))
print("Keyword set used:", analysis.get("keywords", []))
print(f"Number of tokens used: {analysis.get('token_count')}")

saved_path = summary_saver.save_summary(analysis)
print(f"\nSuccess! Summary saved to: {saved_path}")
