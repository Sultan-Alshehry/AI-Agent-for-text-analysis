import send_prompt_online

with open("../python_test/bible.txt", "r", encoding="utf-8") as file:
    text = file.read()

output = send_prompt_online.get_output(text)

print(output)
