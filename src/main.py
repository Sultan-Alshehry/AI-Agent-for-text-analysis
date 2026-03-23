import os
from pathlib import Path

import send_prompt_online
import summary_saver

base_dir = Path(__file__).resolve().parent
bible_path = base_dir.parent / "python_test" / "bible.txt"
with open(bible_path, "r", encoding="utf-8") as file:
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
