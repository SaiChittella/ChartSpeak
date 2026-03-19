import pystray
from PIL import Image

# Open any image and convert it to a transparent PNG
img = Image.open("ChartSpeak.png")
img = img.convert("RGBA") # Ensures transparency support

# Resize to a standard high-res tray size
img = img.resize((64, 64), Image.Resampling.LANCZOS)

# Menu.py
def buildMenuApp(onExit):
    icon_ref = {"icon": None}

    def shutdown():
        icon = icon_ref["icon"]
        if icon is not None:
            icon.stop()
        onExit()

    def onExitWithIconClosure(icon, item):
        shutdown()

    menu = pystray.Menu(
        pystray.MenuItem("Exit", onExitWithIconClosure)
    )

    icon = pystray.Icon(
        "chartspeak_icon",
        icon=img,
        title="Chartspeak",
        menu=menu
    )
    icon_ref["icon"] = icon
    return icon, shutdown