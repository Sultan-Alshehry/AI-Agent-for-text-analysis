import os
import sys

def setup_environment():
    # Prompt the user to configure their AI setting before the app runs.
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Welcome to AITY! You need an AI model to analyze your documents.")
        print("1. Use Gemini online (Requires API Key)")
        print("2. Use KeyBERT locally (No API key needed)")
        choice = input("\nPlease choose an option (1 or 2): ")

        if choice == "1":
            key_input = input("Please paste your Gemini API Key: ")
            os.environ["GEMINI_API_KEY"] = key_input
            print("API Key set for this session!\n")

        elif choice == "2":
            try:
                import keybert
                print("\nKeyBERT is installed! (Note: Local analysis logic is still in development).")
                sys.exit(0)
            except ImportError:
                print("\n[Error] KeyBERT is not installed on your system.")
                print("To use local analysis without an API key, please install it by running:")
                print("pip install keybert")
                sys.exit(1)
        else:
            sys.exit("Invalid choice. Existing application.")
            