#!/usr/bin/env python3

from pathlib import Path
import csv
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]

DRY_RUN = ROOT / "logs" / "sryso-migration-dry-run.csv"
LOG_OUT = ROOT / "logs" / "sryso-migration-executed.csv"

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    if not DRY_RUN.exists():
        print(f"ERROR: missing {DRY_RUN}")
        print("Run ./scripts/dry-run-migration.py first.")
        sys.exit(1)

    rows = read_csv(DRY_RUN)

    copy_rows = [r for r in rows if r["ACTION"] == "COPY"]

    print(f"Dry-run file: {DRY_RUN}")
    print(f"Copy rows to execute: {len(copy_rows)}")
    print()
    print("This will copy files into:")
    print(f"  {ROOT / 'PDFs'}")
    print()
    confirm = input("Proceed? Type YES to continue: ")

    if confirm != "YES":
        print("Aborted.")
        sys.exit(0)

    executed_rows = []

    for row in rows:
        action = row["ACTION"]

        if action != "COPY":
            row["EXECUTED"] = "NO"
            row["EXECUTION-NOTES"] = "not a COPY row"
            executed_rows.append(row)
            continue

        source = ROOT / row["SOURCE-FILE"]
        dest = ROOT / row["DEST-FILE"]

        if not source.exists():
            row["EXECUTED"] = "NO"
            row["EXECUTION-NOTES"] = "source file missing"
            executed_rows.append(row)
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists():
            row["EXECUTED"] = "NO"
            row["EXECUTION-NOTES"] = "destination already exists; skipped to avoid overwrite"
            executed_rows.append(row)
            continue

        shutil.copy2(source, dest)

        row["EXECUTED"] = "YES"
        row["EXECUTION-NOTES"] = "copied"
        executed_rows.append(row)

    fieldnames = list(rows[0].keys()) + ["EXECUTED", "EXECUTION-NOTES"]

    with LOG_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(executed_rows)

    copied = sum(1 for r in executed_rows if r["EXECUTED"] == "YES")
    skipped = sum(1 for r in executed_rows if r["EXECUTED"] != "YES")

    print()
    print(f"Wrote {LOG_OUT}")
    print(f"Copied: {copied}")
    print(f"Skipped/not copied: {skipped}")

if __name__ == "__main__":
    main()
