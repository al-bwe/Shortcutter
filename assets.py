# assets.py
import os
from constants import ASSETS_DIR, SHORTCUTS_DIR

def ensure_directories():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(SHORTCUTS_DIR, exist_ok=True)

def get_icon_path(filename: str) -> str:
    return os.path.join(ASSETS_DIR, filename)

def get_shortcut_path(shortcut_name: str) -> str:
    return os.path.join(SHORTCUTS_DIR, f"{shortcut_name}.json")
