#!/usr/bin/env python3

from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

SURVEY = ROOT / "logs" / "sryso-parts-survey.csv"
NORMALIZATION = ROOT / "reference" / "PART-NORMALIZATION.csv"
OUT = ROOT / "logs" / "part-normalization-review.csv"

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    survey_rows = read_csv(SURVEY)
    norm_rows = read_csv(NORMALIZATION)

    known_patterns = {
        row["PATTERN"].strip().lower()
        for row in norm_rows
        if row.get("PATTERN", "").strip()
    }

    review_rows = []

    for row in survey_rows:
        candidate = row["CANDIDATE-NAME"].strip()
        likely = row.get("LIKELY-PART", "").strip()

        if not candidate:
            continue

        if candidate.lower() in known_patterns:
            continue

        review_rows.append({
            "PATTERN": candidate,
            "SUGGESTED-PART": likely,
            "COUNT": row.get("COUNT", ""),
            "EXAMPLES": row.get("EXAMPLES", ""),
            "PIECE-DIRS": row.get("PIECE-DIRS", ""),
            "COMMENTS": "",
        })

    fieldnames = [
        "PATTERN",
        "SUGGESTED-PART",
        "COUNT",
        "EXAMPLES",
        "PIECE-DIRS",
        "COMMENTS",
    ]

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"Wrote {OUT}")
    print(f"Rows needing review: {len(review_rows)}")

if __name__ == "__main__":
    main()
