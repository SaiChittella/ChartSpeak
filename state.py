import os
class App:
    def __init__(self):

        files = os.listdir('crops')
        paths = []
        for file in files:
            paths.append(os.path.join("crops", file))


        self.model_path = "./my_model/my_model.pt"
        self.test_image_path = "./test.png"
        self.cropped_image_paths = paths
        self.cache: dict[int, list[dict]] = {}
        self.high_note_freq = 880
        self.low_note_freq = 220
        self.dev = True
        self.duration = 0.5 if self.dev else 1

        print(self.cropped_image_paths)


app = App()