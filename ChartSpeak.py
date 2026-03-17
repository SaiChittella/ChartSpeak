# -*- coding: utf-8 -*-
"""
Bar Chart Analyzer — Local Version
====================================
Downloads bar chart dataset from Kaggle, sends each image to Gemini,
and returns normalized [0, 1] values per bar.

Setup:
    pip install kagglehub google-genai python-dotenv pillow matplotlib opencv-python numpy

    Create a .env file in the same directory with:
        GEMINI_API_KEY=your_key_here

    Make sure your Kaggle credentials are configured:
        Either via ~/.kaggle/kaggle.json
        Or via KAGGLE_USERNAME and KAGGLE_KEY environment variables in .env

Usage:
    python bar_chart_analyzer.py
"""

import os
import glob
import json
import re
import time
import math
import random
from pathlib import Path

import kagglehub
import PIL.Image
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import cv2
from dotenv import load_dotenv
from google import genai

# ─────────────────────────────────────────────
#  Load environment variables from .env
# ─────────────────────────────────────────────

load_dotenv()

GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY")
KAGGLE_USERNAME  = os.getenv("KAGGLE_USERNAME")   # optional — only needed if
KAGGLE_KEY       = os.getenv("KAGGLE_KEY")         # kaggle.json isn't present

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Make sure it's set in your .env file.")

# If kaggle.json doesn't exist, set credentials from .env
if KAGGLE_USERNAME and KAGGLE_KEY:
    os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
    os.environ["KAGGLE_KEY"]      = KAGGLE_KEY


# ─────────────────────────────────────────────
#  Cell 2 — Download Dataset & Find Images
# ─────────────────────────────────────────────

def download_dataset() -> list[str]:
    """
    Download the Kaggle dataset using kagglehub.
    Locally, kagglehub caches to ~/.cache/kagglehub/ instead of /kaggle/input/.
    Returns a sorted list of bar chart image paths.
    """
    print("Downloading dataset from Kaggle...")
    path = kagglehub.dataset_download("sunedition/graphs-dataset")
    print(f"Downloaded to: {path}")

    # Locally kagglehub returns the actual cache path directly —
    # we don't need to hardcode /kaggle/input/ like in Colab
    download_dir = path

    image_paths = sorted([
        p for p in (
            glob.glob(f"{download_dir}/graphs/*.png") +
            glob.glob(f"{download_dir}/graphs/*.jpg") +
            glob.glob(f"{download_dir}/graphs/*.jpeg")
        )
        if Path(p).name.startswith("bar_chart")
    ])

    print(f"✅ Found {len(image_paths)} bar chart images")
    for p in image_paths[:10]:
        print(" ", Path(p).name)

    return image_paths


# ─────────────────────────────────────────────
#  Cell 3 — Gemini Client Setup
# ─────────────────────────────────────────────

def setup_gemini() -> genai.Client:
    """Initialize and test the Gemini client."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with just: OK"
    )
    print("Gemini connection test:", response.text.strip())
    print("✅ Gemini ready")
    return client


# ─────────────────────────────────────────────
#  Cell 4 — Extraction & Normalization Functions
# ─────────────────────────────────────────────

EXTRACTION_PROMPT = """
You are a data extraction tool analyzing a bar chart image.

Extract all bars visible in the chart and return a JSON object in EXACTLY this format:

{
  "chart_title": "...",
  "x_axis_label": "...",
  "y_axis_label": "...",
  "y_axis_min": 0,
  "y_axis_max": 100,
  "bars": [
    {"label": "Category A", "raw_value": 45.2},
    {"label": "Category B", "raw_value": 82.1}
  ]
}

Rules:
- List bars left to right as they appear in the chart
- Read raw_value directly from the axis scale or gridlines — do not guess
- If a bar's exact value is unlabeled, estimate carefully from the nearest gridline
- y_axis_min and y_axis_max are the bottom and top values shown on the y-axis
- If the chart title or axis labels are missing, use null
- Return ONLY the JSON object — no explanation, no markdown, no code fences
"""


def extract_bar_data(image_path: str, client: genai.Client, max_retries: int = 3) -> dict | None:
    """Send a chart image to Gemini and return structured bar data."""
    img = PIL.Image.open(image_path)

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[EXTRACTION_PROMPT, img]
            )
            raw_text = response.text.strip()

            # Strip markdown fences if Gemini adds them despite instructions
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"^```\s*",     "", raw_text)
            raw_text = re.sub(r"\s*```$",     "", raw_text)

            data = json.loads(raw_text)

            assert "bars"       in data, "Missing 'bars' key"
            assert "y_axis_min" in data, "Missing 'y_axis_min'"
            assert "y_axis_max" in data, "Missing 'y_axis_max'"
            assert isinstance(data["bars"], list), "'bars' must be a list"
            assert len(data["bars"]) > 0, "Empty bars list"

            return data

        except json.JSONDecodeError as e:
            print(f"  [Attempt {attempt+1}] JSON parse error: {e}")
        except AssertionError as e:
            print(f"  [Attempt {attempt+1}] Validation error: {e}")
        except Exception as e:
            print(f"  [Attempt {attempt+1}] Unexpected error: {e}")

        if attempt < max_retries - 1:
            time.sleep(2)

    return None


def normalize_bars(data: dict) -> list[dict]:
    """Normalize each bar's raw value to [0, 1] using the axis scale."""
    y_min = data["y_axis_min"]
    y_max = data["y_axis_max"]

    if y_max == y_min:
        return [{"bar_index": i, "label": b.get("label", str(i)),
                 "raw_value": b["raw_value"], "normalized_value": 0.5}
                for i, b in enumerate(data["bars"])]

    normalized = []
    for i, bar in enumerate(data["bars"]):
        raw  = bar["raw_value"]
        norm = (raw - y_min) / (y_max - y_min)
        norm = max(0.0, min(1.0, norm))
        normalized.append({
            "bar_index":        i,
            "label":            bar.get("label", str(i)),
            "raw_value":        round(raw,  4),
            "normalized_value": round(norm, 4)
        })

    return normalized


# ─────────────────────────────────────────────
#  Cell 5 — Single Image Test
# ─────────────────────────────────────────────

def test_single_image(image_path: str, client: genai.Client):
    """Run the full pipeline on one image and display results."""
    print(f"\nTesting on: {Path(image_path).name}")

    # Preview the image
    img_preview = plt.imread(image_path)
    plt.figure(figsize=(8, 5))
    plt.imshow(img_preview)
    plt.title("Input Chart")
    plt.axis('off')
    plt.show()

    # Run extraction
    raw_data = extract_bar_data(image_path, client)

    if raw_data:
        print("\n── Gemini Raw Output ────────────────────────")
        print(json.dumps(raw_data, indent=2))

        normalized = normalize_bars(raw_data)
        print("\n── Normalized Values ────────────────────────")
        print(f"{'Bar':<6} {'Label':<20} {'Raw':<10} {'Normalized (0–1)'}")
        print("─" * 50)
        for r in normalized:
            print(f"{r['bar_index']:<6} {str(r['label']):<20} {r['raw_value']:<10} {r['normalized_value']}")

        # Plot normalized values
        labels = [str(r["label"]) for r in normalized]
        values = [r["normalized_value"] for r in normalized]
        colors = cm.viridis(values)

        plt.figure(figsize=(8, 4))
        bars_plot = plt.bar(labels, values, color=colors, edgecolor='black')
        plt.ylim(0, 1.1)
        plt.ylabel("Normalized Value (0–1)")
        plt.title(f"Extracted: {raw_data.get('chart_title', 'Unknown Title')}")
        for bar, val in zip(bars_plot, values):
            plt.text(bar.get_x() + bar.get_width() / 2, val + 0.02,
                     f"{val:.2f}", ha='center', fontsize=9, fontweight='bold')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.show()

    else:
        print("❌ Extraction failed — check the error messages above")


# ─────────────────────────────────────────────
#  Cell 6 — Batch Run
# ─────────────────────────────────────────────
# 
# def run_batch(image_paths: list[str], client: genai.Client,
            #   sample_size: int = 50) -> tuple[list, list]:
    # """
    # Run extraction across multiple images.
    # Respects Gemini free tier rate limit (~12 requests/min).
    # """
    # from tqdm import tqdm
# 
    # REQUESTS_PER_MINUTE = 12
    # DELAY = 60 / REQUESTS_PER_MINUTE
# 
    # results_log = []
    # errors_log  = []
    # sample      = image_paths[:sample_size]
# 
    # print(f"Running on {len(sample)} images (~{len(sample) * DELAY / 60:.1f} mins at free tier rate)...")
# 
    # for image_path in tqdm(sample):
        # filename = Path(image_path).name
        # raw_data = extract_bar_data(image_path, client)
# 
        # if raw_data:
            # normalized = normalize_bars(raw_data)
            # results_log.append({
                # "filename":    filename,
                # "chart_title": raw_data.get("chart_title"),
                # "y_axis_min":  raw_data["y_axis_min"],
                # "y_axis_max":  raw_data["y_axis_max"],
                # "num_bars":    len(normalized),
                # "values":      normalized,
            # })
        # else:
            # errors_log.append({"filename": filename})
# 
        # time.sleep(DELAY)
# 
    # print(f"\n✅ Success: {len(results_log)} / {len(sample)}")
    # print(f"❌ Failed:  {len(errors_log)} / {len(sample)}")
    # return results_log, errors_log
# 
# 
# ─────────────────────────────────────────────
#  Cell 7 — Save Results
# ─────────────────────────────────────────────

def save_results(results_log: list, output_path: str = "chartdata_normalized.json"):
    """Save all results to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(results_log, f, indent=2)
    print(f"💾 Results saved to {output_path}")


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1: Download dataset and find images
    image_paths = download_dataset()

    if not image_paths:
        raise RuntimeError("No bar chart images found. Check the dataset path.")

    # Step 2: Set up Gemini
    client = setup_gemini()

    # Step 3: Test on a single image first
    test_single_image(image_paths[0], client)

    # Step 4: Run batch (set sample_size=len(image_paths) for full run)
    results_log, errors_log = run_batch(image_paths, client, sample_size=50)

    # Step 5: Save results
    save_results(results_log)
