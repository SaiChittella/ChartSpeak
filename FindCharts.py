import os
import cv2
from ultralytics import YOLO
from PIL import ImageGrab

from state import app


def detect_crop_save(
    output_dir: str = "crops",
    conf_threshold: float = 0.5
):

    model_path = "./my_model/my_model.pt"

    snapshot = ImageGrab.grab()
    snapshot.save("image.png")

    image_path = "image.png"

    # Create output directory
    
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    os.makedirs(output_dir, exist_ok=True)


    # Load model
    model = YOLO(model_path)

    # Run inference
    results = model(image_path, conf=conf_threshold)

    # Read original image
    image = cv2.imread(image_path)

    saved_paths = []
    crop_count = 0

    for r in results:
        boxes = r.boxes.xyxy  # (x1, y1, x2, y2)
        scores = r.boxes.conf

        for box, score in zip(boxes, scores):
            x1, y1, x2, y2 = map(int, box.tolist())

            # Crop the image
            crop = image[y1:y2, x1:x2]

            # Skip empty crops (safety)
            if crop.size == 0:
                continue

            # Save crop
            filename = f"crop_{crop_count}.jpg"
            save_path = os.path.join(output_dir, filename)
            cv2.imwrite(save_path, crop)

            saved_paths.append(save_path)
            crop_count += 1

    app.cropped_image_paths = saved_paths
    print(saved_paths)