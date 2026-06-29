#!/usr/bin/env python3

from pathlib import Path
import csv
import re
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "SRYSO-Student-Folders"
LOG_DIR = ROOT / "logs"
PIECE_INVENTORY = LOG_DIR / "sryso-piece-inventory.csv"
OUT = LOG_DIR / "sryso-parts-survey.csv"

SKIP_DIR_RE = re.compile(
    r"(seating|recording|master-docs|^old|ignore|do[-_ ]?not[-_ ]?use|^sryso-scales$)",
    re.IGNORECASE,
)

# Ordered from most specific to most general.
PART_LABEL_PATTERNS = [
    (re.compile(r"(Violin\s*I\s*Ripieno)$", re.I), "Violin I Ripieno"),
    (re.compile(r"(Violin\s*II\s*Ripieno)$", re.I), "Violin II Ripieno"),
    (re.compile(r"(Violin\s*III\s*Ripieno)$", re.I), "Violin III Ripieno"),

    (re.compile(r"(Violin\s*I\s*Solo)$", re.I), "Violin I Solo"),
    (re.compile(r"(Violin\s*II\s*Solo)$", re.I), "Violin II Solo"),
    (re.compile(r"(Violin\s*III\s*Solo)$", re.I), "Violin III Solo"),

    (re.compile(r"(VIOLIN[-_\s]*SOLO)$", re.I), "VIOLIN-SOLO"),
    (re.compile(r"(Violin[-_\s]*Solo)$", re.I), "Violin Solo"),
    (re.compile(r"(Cello[-_\s]*Solo)$", re.I), "Cello Solo"),

    (re.compile(r"(Violins[-_\s]*2[-_\s]*4)$", re.I), "Violins 2-4"),
    (re.compile(r"(Violins[-_\s]*1)$", re.I), "Violins_1"),
    (re.compile(r"(Violins[-_\s]*2)$", re.I), "Violins_2"),

    (re.compile(r"(3rd[-_\s]*Violin(?:\s*\([^)]*\))?)$", re.I), "3rd Violin"),
    (re.compile(r"(2nd[-_\s]*Violin)$", re.I), "2nd Violin"),

    (re.compile(r"(Vln[-_\s]*1)$", re.I), "Vln-1"),
    (re.compile(r"(Vln[-_\s]*2)$", re.I), "Vln-2"),
    (re.compile(r"(Vln[-_\s]*3)$", re.I), "Vln-3"),

    (re.compile(r"(VN[-_\s]*1)$", re.I), "VN-1"),
    (re.compile(r"(VN[-_\s]*2)$", re.I), "VN-2"),
    (re.compile(r"(VN[-_\s]*3)$", re.I), "VN-3"),

    (re.compile(r"(VIOLIN[-_\s]*(?:1|I))$", re.I), "VIOLIN-1"),
    (re.compile(r"(VIOLIN[-_\s]*(?:2|II))$", re.I), "VIOLIN-2"),
    (re.compile(r"(VIOLIN[-_\s]*(?:3|III))$", re.I), "VIOLIN-3"),

    (re.compile(r"(Violin[-_\s]*(?:1|I))$", re.I), "Violin 1"),
    (re.compile(r"(Violin[-_\s]*(?:2|II))$", re.I), "Violin 2"),
    (re.compile(r"(Violin[-_\s]*(?:3|III))$", re.I), "Violin 3"),

    (re.compile(r"(Violin[-_\s]*2B)$", re.I), "Violin-2B"),

    (re.compile(r"(Violoncello[-_\s]*1)$", re.I), "Violoncello-1"),
    (re.compile(r"(Violoncello[-_\s]*2)$", re.I), "Violoncello-2"),
    (re.compile(r"(Cello[-_\s]*1)$", re.I), "Cello-1"),
    (re.compile(r"(Cello[-_\s]*2)$", re.I), "Cello-2"),

    (re.compile(r"(Violas)$", re.I), "Violas"),
    (re.compile(r"(Viola)$", re.I), "Viola"),
    (re.compile(r"(Vla)$", re.I), "Vla"),

    (re.compile(r"(Cellos)$", re.I), "Cellos"),
    (re.compile(r"(Cello)$", re.I), "Cello"),
    (re.compile(r"(Basso)$", re.I), "Basso"),
    (re.compile(r"(Bass)$", re.I), "Bass"),

    (re.compile(r"(Vibraphone[-_\s]*1)$", re.I), "Vibraphone-1"),
    (re.compile(r"(Vibraphone[-_\s]*2)$", re.I), "Vibraphone-2"),
    (re.compile(r"(Piano)$", re.I), "Piano"),

    (re.compile(r"(Score)$", re.I), "SCORE"),
    (re.compile(r"(Full[-_\s]*Score)$", re.I), "SCORE"),
]

def should_skip_path(path: Path) -> bool:
    return any(SKIP_DIR_RE.search(part) for part in path.parts)

def strip_extension(filename: str) -> str:
    return re.sub(r"\.(pdf|mscz)$", "", filename, flags=re.IGNORECASE)

def normalized_stem(filename: str) -> str:
    stem = strip_extension(filename)
    stem = stem.replace("_", "-")
    stem = re.sub(r"\s+", "-", stem)
    stem = re.sub(r"-+", "-", stem)
    return stem.strip(" -_.")

def extract_part_label(filename: str) -> tuple[str, str]:
    """
    Returns (part_label, confidence).

    If no part label is found, default to SCORE because exported MuseScore
    scores often do not include the word SCORE in the filename.
    """
    stem = strip_extension(filename)
    stem_norm = normalized_stem(filename)

    candidates = [
        stem,
        stem_norm,
        stem.replace("-", " "),
        stem.replace("_", " "),
    ]

    for text in candidates:
        for regex, label in PART_LABEL_PATTERNS:
            if regex.search(text):
                return label, "explicit"

    return "SCORE", "assumed-score"

def load_piece_roots():
    piece_roots = []

    with PIECE_INVENTORY.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel = row["REL-PATH"]
            piece_roots.append(SOURCE_ROOT / rel)

    return piece_roots

def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if not PIECE_INVENTORY.exists():
        raise FileNotFoundError(
            f"Missing {PIECE_INVENTORY}. Run scripts/survey-pieces.py first."
        )

    rows_by_label = defaultdict(lambda: {
        "COUNT": 0,
        "CONFIDENCE": set(),
        "EXAMPLES": set(),
        "PIECE-DIRS": set(),
    })

    for piece_root in load_piece_roots():
        if not piece_root.exists():
            continue

        for path in piece_root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() != ".pdf":
                continue

            rel_to_piece = path.relative_to(piece_root)

            if should_skip_path(rel_to_piece):
                continue

            label, confidence = extract_part_label(path.name)

            entry = rows_by_label[label]
            entry["COUNT"] += 1
            entry["CONFIDENCE"].add(confidence)

            if len(entry["EXAMPLES"]) < 8:
                entry["EXAMPLES"].add(str(path.relative_to(SOURCE_ROOT)))

            if len(entry["PIECE-DIRS"]) < 8:
                entry["PIECE-DIRS"].add(str(piece_root.relative_to(SOURCE_ROOT)))

    fieldnames = [
        "PART-LABEL",
        "COUNT",
        "CONFIDENCE",
        "EXAMPLES",
        "PIECE-DIRS",
    ]

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for label in sorted(rows_by_label, key=str.lower):
            info = rows_by_label[label]
            writer.writerow({
                "PART-LABEL": label,
                "COUNT": info["COUNT"],
                "CONFIDENCE": " | ".join(sorted(info["CONFIDENCE"])),
                "EXAMPLES": " | ".join(sorted(info["EXAMPLES"])),
                "PIECE-DIRS": " | ".join(sorted(info["PIECE-DIRS"])),
            })

    print(f"Wrote {OUT}")
    print(f"Rows: {len(rows_by_label)}")

if __name__ == "__main__":
    main()
