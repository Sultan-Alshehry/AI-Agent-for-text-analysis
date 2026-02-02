# Python Test

This is a test run for using program to interact with an LLM, in this case gemini-3-flash-preview.

The program summarizes text from a file and generates key words and topics.

In this directory there is an example text file called bible.txt which contains one page from the Holy Bible (King James Version) from openbible.com that you can use. There is also a generated_summary.txt file which contains one generated output from gemini using the program.

Before you run the program you will need an API key, you can get one by creating an account here: https://ai.google.dev/gemini-api/docs/api-key

You will need to set the api key in your environment variables:
    On Windows: ```set GEMINI_API_KEY=<your_key_here>
    On macOS/Linux: ```export GEMINI_API_KEY="<your_key_here>"

## To run the program

1. Enter it's directory in your terminal.

2. Create a python virtual environment:
    ```python -m venv venv```

3. Source the virtual environment:
    On Windows: ```venv\Scripts\activate```
    On macOS/Linux: ```source venv/bin/activate```

4. Install the dependencies:
    ```pip install -r dependencies.txt```

5. Run the program:
    ```python test.py```
