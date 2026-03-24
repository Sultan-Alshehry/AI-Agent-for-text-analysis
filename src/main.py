
import send_prompt_online
import json
import summary_saver
import re

def get_analysis_result(filepath):


    

    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()
    
    
    if not text:
        print("nothing inside given file")
        return

    output = send_prompt_online.get_output(text)
    output2 = output.candidates[0].content.parts[0].text
    text = parse_gemini_json(output2)

    tokens = output.usage_metadata.total_token_count
    print(f"Number of tokens used: {tokens}")

    saved_path = summary_saver.save_summary(text)
    print(f"\nSuccess! Summary saved to: {saved_path}")
    
    return saved_path
    
def get_dummy_results(filepath):
    return r"C:\BAC\AI-Agent-for-text-analysis\src\output\summary\summary.json"

def parse_gemini_json(text):
    cleaned = re.sub(r"^```json\s*|```$", "", text.strip(), 0, re.MULTILINE)
    return json.loads(cleaned)

