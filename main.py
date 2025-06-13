import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from gui import launch_gui
        launch_gui()
    else:
        from tray import setup_tray
        setup_tray()
