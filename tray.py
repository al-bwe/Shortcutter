import subprocess
import os
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image
import sys

APP_NAME = "Shortcutter"
runner_process = None  # Global variable to track the runner process
tray_icon = None  # Global variable for the tray icon

def get_icon_path(state: str) -> str:
    """
    Get the path to the icon based on the runner state.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if state == "on":
        return os.path.join(script_dir, "assets/runner_on.png")
    else:
        return os.path.join(script_dir, "assets/runner_off.png")

def update_tray_icon(state: str):
    """
    Update the tray icon based on the runner state.
    """
    global tray_icon
    icon_path = get_icon_path(state)
    image = Image.open(icon_path)

    # Stop the current tray icon and restart it with the new image
    tray_icon.icon = image
    tray_icon.visible = True

def start_gui(icon, item):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(script_dir, "main.py")
    subprocess.Popen([sys.executable, main_py, "--gui"])

def start_runner(icon, item):
    global runner_process
    if runner_process and runner_process.poll() is None:
        print("Runner is already running.")
        return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    runner_py = os.path.join(script_dir, "runner.py")
    runner_process = subprocess.Popen([sys.executable, runner_py])
    update_tray_icon("on")
    print("Runner started.")

def stop_runner(icon, item):
    global runner_process
    if runner_process and runner_process.poll() is None:  # Check if the process is running
        runner_process.terminate()
        runner_process = None
        update_tray_icon("off")
        print("Runner stopped.")
    else:
        print("No runner process is currently running.")

def quit_app(icon, item):
    stop_runner(icon, item)  # Ensure the runner is stopped before quitting
    icon.stop()
    sys.exit()

def setup_tray():
    global tray_icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = get_icon_path("off")  # Default to "runner off" icon
    image = Image.open(icon_path)

    menu = Menu(
        Item('Open Shortcut Creator', start_gui),
        Item('Start Runner', start_runner),
        Item('Stop Runner', stop_runner),
        Item('Exit', quit_app)
    )

    tray_icon = Icon(APP_NAME, image, menu=menu)
    tray_icon.run()
