import json
import summary_saver
import file_reader
import ai_config

# We run the setup logic first to ensure the user has configured their AI settings before the app runs.
ai_config.setup_environment()

# We import the AI module ONLY AFTER the setup is complete
import send_prompt_online

# Main Execution Logic
text = file_reader.read_file("../python_test/bible.txt")

output = send_prompt_online.get_output(text)

text = json.loads(send_prompt_online.get_output_text(output))

print(text["summary"])
print(text["keywords"])
print(text["topics"])
tokens = output.usage_metadata.total_token_count
print(f"Number of tokens used: {tokens}")

saved_path = summary_saver.save_summary(text)
print(f"\nSuccess! Summary saved to: {saved_path}")
