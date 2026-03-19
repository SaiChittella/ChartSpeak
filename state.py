class App:
    def __init__(self):
        self.model_path = "./my_model/my_model.pt"
        self.test_image_path = "./test.png"
        self.cropped_image_paths = []
        self.cache: dict[int, list[dict]] = {}


app = App()