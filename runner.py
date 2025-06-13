import keyboard
import pyautogui
import json
import os
from logic import load_all_shortcuts

def execute_steps(steps):
    """
    Execute the steps defined in the shortcut.
    """
    for step in steps:
        action = step.get("action")
        target = step.get("target")
        if action == "left_click":
            pyautogui.click()
        elif action == "right_click":
            pyautogui.rightClick()
        elif action == "move_to":
            x, y = target.split(",")
            pyautogui.moveTo(int(x), int(y))
        else:
            print(f"Unknown action: {action}")

def watch_shortcuts():
    """
    Watch for shortcut key presses and execute the corresponding actions.
    """
    shortcuts = load_all_shortcuts()
    shortcut_map = {sc["combo"]: sc["steps"] for sc in shortcuts}

    print("Watching for shortcuts...")
    for combo, steps in shortcut_map.items():
        keyboard.add_hotkey(combo, lambda: execute_steps(steps))

    # Keep the script running
    keyboard.wait()

if __name__ == "__main__":
    watch_shortcuts()