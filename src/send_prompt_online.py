from key import key
from google import genai

#changed the AI model, because free version limit to gemini-3-flash was met during testing

#ai_model = "gemini-3-flash-preview"
ai_model = "gemini-2.5-flash-lite"

# initial values only, later will be assigned in a function based
# on the file word count
max_summary = 60
max_keywords = 5
max_topics = 3

json_format = {
    "summary": "summary here",
    "keywords": "keywords here",
    "topics": "topics here",
}


# send prompt to the AI
def get_output(message):
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=ai_model,
        contents="Your task is to create keywords, topics, "
        + "and a summary for the provided text. "
        + f"Maximum number of words in the summary is {max_summary}. "
        + f"Maximum number of keywords is {max_keywords}. "
        + f"Maximum number of topics is {max_topics}. "
        + f"Only respond with a json object of this format: {json_format}. "
        + f"Here are the contents that you need to read: {message}",
    )
    return response


# returns only the json fomrat requested
def get_output_text(output):
    return output.candidates[0].content.parts[0].text
