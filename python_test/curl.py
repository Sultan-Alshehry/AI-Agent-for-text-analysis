import os
import requests

API_KEY = os.environ.get("GEMINI_API_KEY") 

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

headers = {
    "x-goog-api-key": API_KEY,
    "Content-Type": "application/json",
}


payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Explain how AI works in a few words"
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()
text_output = data['candidates'][0]['content']['parts'][0]['text']
print(text_output)
