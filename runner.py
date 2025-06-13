import keyboard
import pyautogui
import json
import os
from logic import load_all_shortcuts
from constants import ASSETS_DIR

def execute_steps(steps):
    """
    Execute the steps defined in the shortcut.
    """
    # Remember the initial cursor position
    initial_position = pyautogui.position()

    for step in steps:
        action = step.get("action")
        target = step.get("target")
        if not target:
            print("No target specified for step.")
            continue

        # Locate the image on the screen
        image_path = os.path.join(ASSETS_DIR, target)
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            continue

        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
            if location:
                x, y = location
                if action == "left_click":
                    pyautogui.click(x, y)
                elif action == "right_click":
                    pyautogui.rightClick(x, y)
                else:
                    print(f"Unknown action: {action}")
            else:
                print(f"Image not found on screen: {image_path}")
        except Exception as e:
            print(f"Error locating image: {e}")

    # Return the cursor to the initial position
    pyautogui.moveTo(initial_position)

def watch_shortcuts():
    """
    Watch for shortcut key presses and execute the corresponding actions.
    """
    shortcuts = load_all_shortcuts()
    shortcut_map = {sc["combo"]: sc["steps"] for sc in shortcuts}

    print("Watching for shortcuts...")
    for combo, steps in shortcut_map.items():
        keyboard.add_hotkey(combo, lambda steps=steps: execute_steps(steps))

    # Keep the script running
    keyboard.wait()

if __name__ == "__main__":
    watch_shortcuts()