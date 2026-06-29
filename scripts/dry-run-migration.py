#!/usr/bin/env python3

from pathlib import Path
import csv
import re
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

SOURCE_ROOT = ROOT / "SRYSO-Student-Folders"
DEST_ROOT = ROOT / "PDFs"

MIGRATION_MAP = ROOT / "logs" / "sryso-migration-map.csv"
PART_NORMALIZATION = ROOT / "reference" / "PART-NORMALIZATION.csv"
OUT = ROOT / "logs" / "sryso-migration-dry-run.csv"

SKIP_DIR_RE = re.compile(
    r"(seating|recording|master-docs|^old|ignore|do[-_ ]?not[-_ ]?use|^sryso-scales$|orig[-_ ]?parts|xml[-_ ]?files)",
    re.IGNORECASE,
)

REV_RE = re.compile(r"(?:ver|version|rev)[-_ \[\]]*(\d+)", re.I)
FULL_DATE_RE = re.compile(r"\b(20\d{2})[-_ ](\d{2})[-_ ](\d{2})\b")
PARTIAL_DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[-_](\d{1,2})(?!\d)")

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_part_normalization():
    table = {}
    for row in read_csv(PART_NORMALIZATION):
        pattern = row["PATTERN"].strip()
        part = row["PART"].strip()
        if pattern and part:
            table[pattern.lower()] = part
    return table

def should_skip_path(path: Path) -> bool:
    return any(SKIP_DIR_RE.search(part) for part in path.parts)

def strip_ext(name: str) -> str:
    return re.sub(r"\.(pdf|mscz)$", "", name, flags=re.I)

def explicit_rev_number(name: str) -> int:
    m = REV_RE.search(name)
    return int(m.group(1)) if m else 0

def version_key(path: Path):
    name = path.name
    lower = name.lower()

    rev = explicit_rev_number(name)

    full_date = 0
    m = FULL_DATE_RE.search(name)
    if m:
        yyyy, mm, dd = map(int, m.groups())
        full_date = yyyy * 10000 + mm * 100 + dd

    partial_date = 0
    for m in PARTIAL_DATE_RE.finditer(name):
        mm, dd = map(int, m.groups())
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            partial_date = mm * 100 + dd

    copy_penalty = -1 if lower.startswith("copy of ") else 0
    source_penalty = -1 if re.search(r"orig|source|xml", str(path), re.I) else 0

    return (rev, full_date, partial_date, copy_penalty, source_penalty, str(path))

def version_label(path: Path):
    rev, full_date, partial_date, *_ = version_key(path)
    bits = []
    if rev:
        bits.append(f"REV:{rev}")
    if full_date:
        bits.append(f"DATE:{full_date}")
    elif partial_date:
        bits.append(f"DATE-MMDD:{partial_date:04d}")
    return ";".join(bits) if bits else "NO-VERSION"

def semester_key_from_source(source_file: str) -> int:
    m = re.search(r"SRYSO-Student-Folders/(\d{4})-(\d)-", source_file)
    if not m:
        return 0
    return int(m.group(1)) * 10 + int(m.group(2))

def candidate_part_labels(filename: str):
    stem = strip_ext(filename)

    variants = {
        stem,
        stem.replace("_", "-"),
        stem.replace("_", " "),
        stem.replace("-", " "),
    }

    pieces = set()

    for v in variants:
        v = v.strip()
        if not v:
            continue

        pieces.add(v)
        tokens = [t for t in re.split(r"[-_ ]+", v) if t]

        for n in range(1, min(6, len(tokens)) + 1):
            pieces.add(" ".join(tokens[-n:]))
            pieces.add("-".join(tokens[-n:]))
            pieces.add("_".join(tokens[-n:]))
            pieces.add(" ".join(tokens[:n]))
            pieces.add("-".join(tokens[:n]))
            pieces.add("_".join(tokens[:n]))

    return sorted(pieces, key=len, reverse=True)

def infer_part(filename: str, norm):
    stem = strip_ext(filename)

    variants = {
        stem,
        stem.replace("_", "-"),
        stem.replace("_", " "),
        stem.replace("-", " "),
    }

    for candidate in candidate_part_labels(filename):
        key = candidate.strip().lower()
        if key in norm:
            return norm[key], candidate, "explicit"

    patterns = sorted(norm.keys(), key=len, reverse=True)

    for variant in variants:
        variant_lc = variant.lower()

        for pattern in patterns:
            pat = re.escape(pattern)
            pat = pat.replace(r"\ ", r"[-_ ]+")
            pat = pat.replace(r"\-", r"[-_ ]+")
            pat = pat.replace(r"_", r"[-_ ]+")

            if re.search(rf"(^|[-_ \[\]()]){pat}($|[-_ \[\]()])", variant_lc, re.I):
                return norm[pattern], pattern, "explicit-anywhere"

    return "SCORE", "", "assumed-score"

def mscz_dest_name(dest_composer, dest_work, path):
    rev = explicit_rev_number(path.name)
    if rev:
        return f"{dest_composer}-{dest_work}-REV-{rev}.mscz"
    return f"{dest_composer}-{dest_work}.mscz"

def add_row(rows, action, source_file, dest_file, part, matched, confidence, notes):
    rows.append({
        "ACTION": action,
        "SOURCE-FILE": str(source_file),
        "DEST-FILE": str(dest_file),
        "PART": part,
        "MATCHED-PATTERN": matched,
        "CONFIDENCE": confidence,
        "NOTES": notes,
    })

def choose_best(items):
    """
    Best means:
      1. later semester
      2. higher explicit REV/VER/date key
      3. deterministic path tie-break
    """
    return max(
        items,
        key=lambda item: (
            semester_key_from_source(str(item["path"])),
            item["version_key"],
            str(item["path"]),
        )
    )

def main():
    norm = load_part_normalization()
    migration_rows = read_csv(MIGRATION_MAP)

    all_pdf_candidates = []
    all_mscz_candidates = []
    dry_rows = []

    for row in migration_rows:
        notes = row.get("NOTES", "").strip()
        if notes.upper().startswith("EXCLUDE"):
            continue

        source_rel = row["SOURCE-REL-PATH"].strip()
        dest_composer = row["DEST-COMPOSER"].strip()
        dest_work = row["DEST-WORK"].strip()

        if not source_rel or not dest_composer or not dest_work:
            add_row(dry_rows, "ERROR", source_rel, "", "", "", "error",
                    "missing source/composer/work in migration map")
            continue

        source_dir = SOURCE_ROOT / source_rel
        if not source_dir.exists():
            add_row(dry_rows, "ERROR", source_dir, "", "", "", "error",
                    "source directory does not exist")
            continue

        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue

            rel_to_source = path.relative_to(source_dir)
            if should_skip_path(rel_to_source):
                continue

            suffix = path.suffix.lower()

            if suffix == ".pdf":
                part, matched, confidence = infer_part(path.name, norm)
                dest_file = DEST_ROOT / dest_composer / dest_work / "CURRENT" / f"{part}.pdf"

                all_pdf_candidates.append({
                    "path": path,
                    "dest_file": dest_file,
                    "part": part,
                    "matched": matched,
                    "confidence": confidence,
                    "version_key": version_key(path),
                    "version_label": version_label(path),
                })

            elif suffix == ".mscz":
                logical_dest = DEST_ROOT / dest_composer / dest_work / "CURRENT" / "__MSCZ__"

                all_mscz_candidates.append({
                    "path": path,
                    "logical_dest": logical_dest,
                    "dest_composer": dest_composer,
                    "dest_work": dest_work,
                    "version_key": version_key(path),
                    "version_label": version_label(path),
                })

    # PDFs: dedupe globally by actual destination file.
    pdf_by_dest = defaultdict(list)
    for item in all_pdf_candidates:
        pdf_by_dest[str(item["dest_file"].relative_to(ROOT))].append(item)

    for dest_key, items in pdf_by_dest.items():
        chosen = choose_best(items)

        for item in items:
            action = "COPY" if item is chosen else "SKIP"

            note_bits = []

            if item is chosen:
                if item["version_label"] != "NO-VERSION":
                    note_bits.append(f"KEPT-LATEST:{item['version_label']}")
                if len(items) > 1:
                    note_bits.append("SELECTED-BEST-CANDIDATE")
            else:
                note_bits.append(
                    f"SKIPPED-OLDER-SEMESTER-OR-VERSION:{item['version_label']}; "
                    f"kept {chosen['version_label']}"
                )

            add_row(
                dry_rows,
                action,
                item["path"].relative_to(ROOT),
                item["dest_file"].relative_to(ROOT),
                item["part"],
                item["matched"],
                item["confidence"],
                " | ".join(note_bits),
            )

    # MSCZ: dedupe globally by logical work/current slot, then assign final dest filename.
    mscz_by_logical_dest = defaultdict(list)
    for item in all_mscz_candidates:
        mscz_by_logical_dest[str(item["logical_dest"].relative_to(ROOT))].append(item)

    for logical_dest, items in mscz_by_logical_dest.items():
        chosen = choose_best(items)

        for item in items:
            final_dest = (
                DEST_ROOT
                / item["dest_composer"]
                / item["dest_work"]
                / "CURRENT"
                / mscz_dest_name(item["dest_composer"], item["dest_work"], item["path"])
            )

            action = "COPY" if item is chosen else "SKIP"

            note_bits = []

            if item is chosen:
                if item["version_label"] != "NO-VERSION":
                    note_bits.append(f"KEPT-LATEST:{item['version_label']}")
                if len(items) > 1:
                    note_bits.append("SELECTED-BEST-CANDIDATE")
            else:
                note_bits.append(
                    f"SKIPPED-OLDER-SEMESTER-OR-VERSION:{item['version_label']}; "
                    f"kept {chosen['version_label']}"
                )

            add_row(
                dry_rows,
                action,
                item["path"].relative_to(ROOT),
                final_dest.relative_to(ROOT),
                "MSCZ",
                "",
                "mscz",
                " | ".join(note_bits),
            )

    fieldnames = [
        "ACTION",
        "SOURCE-FILE",
        "DEST-FILE",
        "PART",
        "MATCHED-PATTERN",
        "CONFIDENCE",
        "NOTES",
    ]

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dry_rows)

    print(f"Wrote {OUT}")
    print(f"Rows: {len(dry_rows)}")
    print(f"Copy rows: {sum(1 for r in dry_rows if r['ACTION'] == 'COPY')}")
    print(f"Skipped rows: {sum(1 for r in dry_rows if r['ACTION'] == 'SKIP')}")
    print(f"Assumed scores copied: {sum(1 for r in dry_rows if r['CONFIDENCE'] == 'assumed-score' and r['ACTION'] == 'COPY')}")

if __name__ == "__main__":
    main()
