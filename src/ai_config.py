import os
import json
import sys
import state


def validate_user_data():
    if not os.path.exists("user_data.json"):
        return False

    data_format = {"api key": str}


def setup_environment(choice):
    with open("user_data.json", "r") as file:
        user_data = json.load(file)

    state.API_KEY = user_data["api key"]

    try:
        import keybert
    except ImportError:
        state.KEYBERT_INSTALLED = False
    else:
        state.KEYBERT_INSTALLED = True
