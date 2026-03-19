import os

class App:
    def __init__(self):
        crops_dir = 'temp/crops'
        if not os.path.exists(crops_dir):
            os.makedirs(crops_dir)

        files = os.listdir(crops_dir)
        paths = []
        for file in files:
            paths.append(os.path.join(crops_dir, file))

        self.dev = False

        self.model_path = "./model/bar_chart_recognition.pt"
        self.screnshot_path = "temp/screenshot.png"
        self.cropped_image_paths = paths

        self.cache: dict[int, list[dict]] = {}

        self.high_note_freq = 880
        self.low_note_freq = 220
        self.duration = 0.5 if self.dev else 1

app = App()