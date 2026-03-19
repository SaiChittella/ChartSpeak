import os
from threading import Thread

from modules.hotkeys import listener as HotkeysListener, set_exit_callback
from modules.menu_bar import buildMenuApp

def main():
    def close():
        HotkeysListener.stop()

    tray_icon, shutdown = buildMenuApp(close)
    set_exit_callback(shutdown)

    HotkeysListener.start()
    t1 = Thread(target=os.system, args=('say "Hit command plus option plus control plus H to find list of shortcuts."',), daemon=True)
    t1.start()
    tray_icon.run()


if __name__ == "__main__":
    main()