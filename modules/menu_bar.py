import pystray
from PIL import Image

img = Image.open("assets/menu-bar-item.png")
img = img.convert("RGBA")

img = img.resize((64, 64), Image.Resampling.LANCZOS)

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