import subprocess
import os
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image
import sys

APP_NAME = "Shortcutter"

def start_gui(icon, item):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(script_dir, "main.py")
    subprocess.Popen([sys.executable, main_py, "--gui"])

def start_runner(icon, item):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    runner_py = os.path.join(script_dir, "runner.py")
    subprocess.Popen([sys.executable, runner_py])

def quit_app(icon, item):
    icon.stop()
    sys.exit()

def setup_tray():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "assets", "icon.png")
    image = Image.open(icon_path)

    menu = Menu(
        Item('Open Shortcut Creator', start_gui),
        Item('Start Runner', start_runner),
        Item('Exit', quit_app)
    )

    tray_icon = Icon(APP_NAME, image, menu=menu)
    tray_icon.run()
