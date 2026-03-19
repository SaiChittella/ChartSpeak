# main.py
from Hotkeys import listener as HotkeysListener, set_exit_callback
from Menu import buildMenuApp

def main():
    def close():
        HotkeysListener.stop()

    tray_icon, shutdown = buildMenuApp(close)
    set_exit_callback(shutdown)

    HotkeysListener.start()
    tray_icon.run()


if __name__ == "__main__":
    main()