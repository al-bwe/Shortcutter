# logic.py
import json
import os
import re
import time
from typing import List, Dict
import pyautogui
from assets import get_shortcut_path, ensure_directories
from constants import SHORTCUTS_DIR

# A list of common OS/system shortcut combos to block
COMMON_SHORTCUTS = {
    "ctrl+c", "ctrl+v", "ctrl+x", "alt+f4", "ctrl+z", "ctrl+y",
    "ctrl+a", "ctrl+s", "ctrl+p", "alt+tab", "win+d"
}

def normalize_shortcut(combo: str) -> str:
    """
    Normalize shortcut string to lowercase and sorted modifiers for consistency.
    E.g. "Alt+Ctrl+C" -> "alt+ctrl+c"
    """
    parts = combo.lower().split("+")
    parts = [p.strip() for p in parts if p.strip()]
    # Sort modifiers except the last key
    if len(parts) > 1:
        *mods, key = parts
        mods.sort()
        parts = mods + [key]
    return "+".join(parts)

def is_shortcut_valid(combo: str, existing_shortcuts: List[str]) -> bool:
    """
    Validate that the shortcut combo:
    - Is not empty
    - Is not a common system shortcut
    - Is not already used
    - Matches simple pattern of keys/modifiers
    """
    print(f"Validating shortcut: {combo}")  # Debugging line
    print(f"Existing shortcuts: {existing_shortcuts}")  # Debugging line

    if not combo:
        return False
    normalized = normalize_shortcut(combo)
    if normalized in COMMON_SHORTCUTS:
        print(f"Shortcut rejected as common: {normalized}")  # Debugging line
        return False
    if normalized in (normalize_shortcut(s) for s in existing_shortcuts):
        print(f"Shortcut rejected as already used: {normalized}")  # Debugging line
        return False
    # Simple pattern: modifiers + single key (letters, digits, f1-f12)
    pattern = re.compile(r"^(alt\+|ctrl\+|shift\+|win\+)*[a-z0-9f1-12]{1,3}$")
    if not pattern.match(normalized):
        print(f"Shortcut rejected by pattern: {normalized}")  # Debugging line
        return False
    return True

def load_all_shortcuts() -> List[Dict]:
    """
    Load all shortcut JSON files from SHORTCUTS_DIR
    """
    ensure_directories()
    shortcuts = []
    for filename in os.listdir(SHORTCUTS_DIR):
        if filename.endswith(".json"):
            path = os.path.join(SHORTCUTS_DIR, filename)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    shortcuts.append(data)
            except Exception as e:
                print(f"Error loading shortcut {filename}: {e}")
    return shortcuts

def save_shortcut(shortcut: Dict) -> None:
    ensure_directories()
    if "name" not in shortcut:
        raise ValueError("Shortcut dict must have a 'name' key")
    if "steps" in shortcut:
        if not isinstance(shortcut["steps"], list):
            raise ValueError("'steps' must be a list of shortcut strings")
    path = get_shortcut_path(shortcut["name"])
    with open(path, "w") as f:
        json.dump(shortcut, f, indent=4)

def execute_shortcut(shortcut: Dict) -> None:
    """
    Execute the shortcut actions, including sequences.
    """
    print(f"Executing shortcut: {shortcut.get('name')} with steps:")
    initial_position = pyautogui.position()  # Save the cursor's origin position

    for step in shortcut.get("steps", []):
        action = step.get("action")
        if action == "delay":
            duration = step.get("duration", 0)
            print(f"Delaying for {duration} seconds...")
            time.sleep(duration)
        elif action == "move_to_image":
            image_path = step.get("target")
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                continue
            location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
            if location:
                x, y = location
                print(f"Moving cursor to image at ({x}, {y})...")
                pyautogui.moveTo(x, y)
            else:
                print(f"Image not found on screen: {image_path}")
        elif action == "move_to_origin":
            print(f"Returning cursor to origin at {initial_position}...")
            pyautogui.moveTo(initial_position)
        elif action == "check_duplicates":
            image_path = step.get("target")
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                continue
            locations = list(pyautogui.locateAllOnScreen(image_path, confidence=0.8))
            if len(locations) > 1:
                print(f"Duplicate icons detected for {image_path}. Stopping execution.")
                return
        else:
            print(f"Unknown action: {action}")

    print("Shortcut execution completed.")

def is_sequence_valid(sequence: List[str], existing_shortcuts: List[str]) -> bool:
    """
    Validate that the sequence of shortcuts:
    - Each step is a valid shortcut
    - No step conflicts with existing shortcuts
    """
    for step in sequence:
        if not is_shortcut_valid(step, existing_shortcuts):
            print(f"Sequence step invalid: {step}")  # Debugging line
            return False
    return True

def create_sequence_shortcut(name: str, sequence: List[str], existing_shortcuts: List[str]) -> Dict:
    """
    Create a multi-step shortcut sequence.
    """
    if not is_sequence_valid(sequence, existing_shortcuts):
        raise ValueError("Invalid sequence")
    return {
        "name": name,
        "steps": sequence
    }

# Example shortcut definition
shortcut_example = {
    "name": "OpenDropdownMenu",
    "steps": [
        "ctrl+alt+d",
        "down",
        "enter"
    ]
}
