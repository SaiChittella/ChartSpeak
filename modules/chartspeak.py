import os
from threading import Thread
from cv2 import imread, imwrite
from ultralytics import YOLO
from PIL import ImageGrab

from state import app


def detect_crop_save(
    output_dir: str = "temp/crops",
    conf_threshold: float = 0.5
):
    t1 = Thread(target=os.system, args=('say "Detecting bar charts on screen"',), daemon=True)
    t1.start()

    model_path = app.model_path

    snapshot = ImageGrab.grab()
    image_path = app.screnshot_path
    snapshot.save(image_path)


    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    os.makedirs(output_dir, exist_ok=True)


    model = YOLO(model_path)

    results = model(image_path, conf=conf_threshold)

    image = imread(image_path)

    saved_paths = []
    crop_count = 0

    for r in results:
        boxes = r.boxes.xyxy  # (x1, y1, x2, y2)
        scores = r.boxes.conf

        for box, score in zip(boxes, scores):
            x1, y1, x2, y2 = map(int, box.tolist())

            crop = image[y1:y2, x1:x2]

            if crop.size == 0:
                continue

            filename = f"crop_{crop_count}.jpg"
            save_path = os.path.join(output_dir, filename)
            imwrite(save_path, crop)

            saved_paths.append(save_path)
            crop_count += 1
    app.cropped_image_paths = saved_paths