import re
import time
from dotenv import load_dotenv
import os
from google import genai
import PIL
import json

from state import app

# ─────────────────────────────────────────────
#  Load environment variables from .env
# ─────────────────────────────────────────────

load_dotenv()

GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Make sure it's set in your .env file.")

def setup_gemini() -> genai.Client:
    """Initialize and test the Gemini client."""
    if app.dev:
        print("✅ Gemini ready")
        return None
    else:
        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Reply with just: OK"
        )
        print("Gemini connection test:", response.text.strip())
        print("✅ Gemini ready")
        return client


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

    if app.dev:
        return DUMMY_DATA
    else:
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

                print(data)
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

DUMMY_DATA = {'chart_title': None, 'x_axis_label': None, 'y_axis_label': 'Hits@10', 'y_axis_min': 0, 'y_axis_max': 70, 'bars': [{'label': 'FB15k-237 (PPR)', 'raw_value': 2.0}, {'label': 'FB15k-237 (SOTA)', 'raw_value': 68.0}, {'label': 'WN18RR (PPR)', 'raw_value': 46.0}, {'label': 'WN18RR (SOTA)', 'raw_value': 60.0}, {'label': 'CoDEx-S (PPR)', 'raw_value': 8.0}, {'label': 'CoDEx-S (SOTA)', 'raw_value': 68.0}, {'label': 'CoDEx-M (PPR)', 'raw_value': 8.0}, {'label': 'CoDEx-M (SOTA)', 'raw_value': 49.0}, {'label': 'CoDEx-L (PPR)', 'raw_value': 9.0}, {'label': 'CoDEx-L (SOTA)', 'raw_value': 47.0}, {'label': 'Hetionet (PPR)', 'raw_value': 18.0}, {'label': 'Hetionet (SOTA)', 'raw_value': 42.0}, {'label': 'DBPedia100k (PPR)', 'raw_value': 30.0}, {'label': 'DBPedia100k (SOTA)', 'raw_value': 42.0}]}