#!/usr/bin/env python3
"""
Run all sample activities through the full pipeline and save the results.

This is what produces the "three activities run end to end, each showing
the full set of seven outputs" submission requirement from the work order.

Usage (from the project root, with GROQ_API_KEY set):
    python scripts/generate_samples.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from proof_builder.pipeline import run_pipeline

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_PATH = os.path.join(ROOT, "data", "sample_activities.json")
OUTPUT_DIR = os.path.join(ROOT, "sample_outputs")


def slugify(title: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in title.lower()).strip("-")


def main():
    load_dotenv()

    if not os.environ.get("GROQ_API_KEY"):
        print(
            "GROQ_API_KEY is not set. Get a free key at console.groq.com "
            "(see Groq_API_Guide_Caarya_Interns.docx) and add it to a .env file first."
        )
        sys.exit(1)

    with open(SAMPLES_PATH, "r", encoding="utf-8") as f:
        samples = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, sample in enumerate(samples, start=1):
        title = sample["title"]
        print(f"[{i}/{len(samples)}] Running: {title}")
        result = run_pipeline(sample["activity_text"])

        slug = slugify(title)
        json_path = os.path.join(OUTPUT_DIR, f"{i:02d}_{slug}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"    saved -> {json_path}")

    print(f"\nDone. {len(samples)} activities run end to end. See {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
