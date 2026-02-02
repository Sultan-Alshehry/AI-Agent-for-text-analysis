from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# API key can be obtained from https://aistudio.google.com/api-keys
client = genai.Client()

file_name = input("Add the full path to the file you want to be summarized:\n")
with open(file_name, "r", encoding="utf-8") as file:
    file_contents = file.read()
input = f"Shortly list the key words and topics in the following text:\n{file_contents}"
file.close()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=input
)

print(response.text)
