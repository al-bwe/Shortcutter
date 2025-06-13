# logic.py
import json
import os
import re
from typing import List, Dict
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
    path = get_shortcut_path(shortcut["name"])
    with open(path, "w") as f:
        json.dump(shortcut, f, indent=4)

def execute_shortcut(shortcut: Dict) -> None:
    """
    Execute the shortcut actions.
    (Placeholder for now)
    """
    print(f"Executing shortcut: {shortcut.get('name')} with steps:")
    for step in shortcut.get("steps", []):
        print(f" - {step}")
    # TODO: Implement actual PyAutoGUI mouse/key logic here
