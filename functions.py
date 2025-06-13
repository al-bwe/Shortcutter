# functions.py
import os
import shutil
from typing import Optional

def copy_image_to_assets(src_path: str, dest_dir: str, new_filename: Optional[str] = None) -> str:
    """
    Copy an image file to the assets directory.
    Returns the new path of the copied file.
    If new_filename is None, uses the basename from src_path.
    """
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")

    os.makedirs(dest_dir, exist_ok=True)
    filename = new_filename if new_filename else os.path.basename(src_path)
    dest_path = os.path.join(dest_dir, filename)

    shutil.copy2(src_path, dest_path)
    return dest_path

def validate_image_file(filepath: str) -> bool:
    """
    Basic check if a file is a PNG image by extension and existence.
    """
    if not os.path.isfile(filepath):
        return False
    ext = os.path.splitext(filepath)[1].lower()
    return ext == ".png"

def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be a safe filename (remove/replace invalid chars).
    """
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name.strip()

def format_steps_for_display(steps: list) -> str:
    """
    Create a simple string summary of shortcut steps for display in the GUI.
    """
    lines = []
    for i, step in enumerate(steps, 1):
        action = step.get("action", "unknown")
        target = step.get("target", "")
        if action in ("left_click", "right_click"):
            lines.append(f"{i}. {action.replace('_', ' ').title()} on '{target}'")
        elif action == "delay":
            lines.append(f"{i}. Delay {step.get('duration', 0)} seconds")
        elif action == "wait_for_image":
            lines.append(f"{i}. Wait for image '{target}'")
        else:
            lines.append(f"{i}. {action}")
    return "\n".join(lines)
