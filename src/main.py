
import os
from pathlib import Path
import json
import summary_saver
import send_prompt_online
from ai_config import get_analysis_mode, setup_environment
from file_reader import read_file
import state as t


if __name__ == "__main__":
    mode = setup_environment()
    print(f"Using {mode} mode")

    from user_interface import AityApp
    app = AityApp()
    app.mainloop()
