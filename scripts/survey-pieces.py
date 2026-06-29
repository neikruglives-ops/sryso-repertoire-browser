#!/usr/bin/env python3

from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "SRYSO-Student-Folders"
LOG_DIR = ROOT / "logs"
OUT = LOG_DIR / "sryso-piece-inventory.csv"

IGNORE_DIR_RE = re.compile(
    r"(seating|recording|master-docs|^old|ignore|do[-_ ]?not[-_ ]?use|^sryso-scales$)",
    re.IGNORECASE,
)

CONTAINER_RE = re.compile(r"^(ALPHA_|OMEGA_|PRE-ORCHESTRA)", re.IGNORECASE)

def is_ignored(name: str) -> bool:
    return bool(IGNORE_DIR_RE.search(name))

def is_container(name: str) -> bool:
    return bool(CONTAINER_RE.search(name))

def group_name(name: str) -> str:
    if re.match(r"^ALPHA_", name, re.I):
        return "ALPHA"
    if re.match(r"^OMEGA_", name, re.I):
        return "OMEGA"
    if re.match(r"^PRE-ORCHESTRA", name, re.I):
        return "PRE-ORCHESTRA"
    return ""

def immediate_dirs(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Source path does not exist: {path}")
    return sorted([p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")], key=lambda p: p.name.lower())

def inspect_piece_dir(piece_path: Path):
    pdfs = []
    mscz = []
    subdirs = set()
    flags = set()

    for p in piece_path.rglob("*"):
        if p.name.startswith("."):
            continue

        if p.is_dir():
            subdirs.add(p.name)

            if re.search(r"^old|ignore|do[-_ ]?not[-_ ]?use", p.name, re.I):
                flags.add(f"HAS-SKIP-DIR:{p.name}")
                continue

            if re.search(r"source", p.name, re.I):
                flags.add(f"HAS-SOURCE-DIR:{p.name}")

            if re.search(r"violin.*2.*b|2.*b.*part", p.name, re.I):
                flags.add(f"HAS-VN-2B-DIR:{p.name}")

        elif p.is_file():
            # Skip files if they live anywhere inside ignored/skip dirs.
            rel_parts = p.relative_to(piece_path).parts[:-1]
            if any(is_ignored(part) for part in rel_parts):
                continue

            suffix = p.suffix.lower()
            if suffix == ".pdf":
                pdfs.append(p.name)
            elif suffix == ".mscz":
                mscz.append(p.name)

    samples = (pdfs + mscz)[:8]

    return {
        "pdf_count": len(pdfs),
        "mscz_count": len(mscz),
        "subdirs": sorted(subdirs, key=str.lower),
        "samples": samples,
        "flags": sorted(flags, key=str.lower),
    }

def piece_dirs_for_semester(semester_path: Path):
    for entry in immediate_dirs(semester_path):
        if is_ignored(entry.name):
            continue

        if is_container(entry.name):
            group = group_name(entry.name)
            for piece in immediate_dirs(entry):
                if is_ignored(piece.name):
                    continue
                yield group, piece
        else:
            yield "", entry

def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    for semester in immediate_dirs(SOURCE_ROOT):
        if is_ignored(semester.name):
            continue

        for group, piece_path in piece_dirs_for_semester(semester):
            info = inspect_piece_dir(piece_path)

            if info["pdf_count"] == 0 and info["mscz_count"] == 0:
                continue

            rows.append({
                "SEMESTER": semester.name,
                "ENSEMBLE-GROUP": group,
                "PIECE-DIR": piece_path.name,
                "REL-PATH": str(piece_path.relative_to(SOURCE_ROOT)),
                "PDF-COUNT": info["pdf_count"],
                "MSCZ-COUNT": info["mscz_count"],
                "SUBDIR-COUNT": len(info["subdirs"]),
                "SUBDIRS": " | ".join(info["subdirs"]),
                "SAMPLE-FILES": " | ".join(info["samples"]),
                "FLAGS": " | ".join(info["flags"]),
            })

    fieldnames = [
        "SEMESTER",
        "ENSEMBLE-GROUP",
        "PIECE-DIR",
        "REL-PATH",
        "PDF-COUNT",
        "MSCZ-COUNT",
        "SUBDIR-COUNT",
        "SUBDIRS",
        "SAMPLE-FILES",
        "FLAGS",
    ]

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUT}")
    print(f"Rows: {len(rows)}")

if __name__ == "__main__":
    main()
