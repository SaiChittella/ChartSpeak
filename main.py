from state import app
from Hotkeys import listener as HotkeysListener

def main():
    HotkeysListener.start()
    try:
        HotkeysListener.join()
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()