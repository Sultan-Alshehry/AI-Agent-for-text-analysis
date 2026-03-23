import send_prompt_online
import json
import summary_saver

with open("../python_test/bible.txt", "r", encoding="utf-8") as file:
    text = file.read()

output = send_prompt_online.get_output(text)

text = json.loads(send_prompt_online.get_output_text(output))

print(text["summary"])
print(text["keywords"])
print(text["topics"])
tokens = output.usage_metadata.total_token_count
print(f"Number of tokens used: {tokens}")

saved_path = summary_saver.save_summary(text)
print(f"\nSuccess! Summary saved to: {saved_path}")
