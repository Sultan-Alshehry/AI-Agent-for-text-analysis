
from pathlib import Path
from ai_config import get_analysis_mode, setup_environment

if __name__ == "__main__":
    mode = setup_environment()
    print(f"Using {mode} mode")

    from ui.user_interface import AityApp
    app = AityApp()
    app.mainloop()
