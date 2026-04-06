
from pathlib import Path
from ai_config import get_mode_display_name, setup_environment

if __name__ == "__main__":
    mode = setup_environment()
    print(f"Using {get_mode_display_name(mode)} mode")

    from ui.user_interface import AityApp
    app = AityApp()
    app.mainloop()
