#!/usr/bin/env python3

from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]

INVENTORY = ROOT / "logs" / "sryso-piece-inventory.csv"
OUT = ROOT / "logs" / "sryso-migration-map.csv"

KNOWN_COMPOSERS = [
    "Bach", "Bartok", "Bizet", "Corelli", "Djawadi", "Dvorak", "Ffrench",
    "Holst", "Hurwitz", "Mozart", "Offenbach", "Rachmaninoff", "Rossini",
    "Saint-Saens", "Sibelius", "Tchaikovsky", "Vivaldi", "Williams", "Zimmer",
]

COMPOSER_ALIASES = {
    "Brandenburg": "Bach",
    "Air-on-the-G-String": "Bach",
    "Air-G-String": "Bach",
    "Habanera": "Bizet",
    "Xmas-Cto": "Corelli",
    "Game-Thrones": "Djawadi",
    "William-Tell": "Rossini",
    "Finlandia": "Sibelius",
    "1812": "Tchaikovsky",
    "Swan-Lake": "Tchaikovsky",
    "Andante": "Tchaikovsky",
    "Jurassic": "Williams",
    "Star-Wars": "Williams",
    "Interstellar": "Zimmer",
    "Howls-Moving-Castle": "Hisaishi",
    "Kikis-Delivery-Service": "Hisaishi",
    "Mia": "Hurwitz",
    "Sebastian": "Hurwitz",
    "Up-Theme": "Giacchino",
    "Married-Life": "Giacchino",
    "Jupiter": "Holst",
    "Holberg": "Grieg",
    "Eroica": "Beethoven",
    "Jingle": "Traditional",
    "Musette": "Bach",
    "Judas-Maccabaeus": "Handel",
    "Naruto": "Toshio-Masuda",
    "The-Crown": "Balfe",
    "Queen-of-Night": "Mozart",
    "Eine-Kleine": "Mozart",
    "Mozart-40": "Mozart",
    "Wishing": "Ffrench",
    "Bartok": "Bartok",
    "Rachmaninoff": "Rachmaninoff",
    "Saint-Saens": "Saint-Saens",
    "Vivaldi": "Vivaldi",
    "Dvorak": "Dvorak",
}

def slug(s: str) -> str:
    s = s.strip()
    s = s.replace("&", "and")
    s = s.replace("'", "")
    s = s.replace("’", "")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")

def guess_composer(piece_dir: str) -> str:
    text = slug(piece_dir)

    parts = text.split("-")

    for composer in KNOWN_COMPOSERS:
        if composer.lower() in [p.lower() for p in parts]:
            return composer

    for key, composer in COMPOSER_ALIASES.items():
        if key.lower() in text.lower():
            return composer

    return ""

def remove_composer_tokens(work_slug: str, composer: str) -> str:
    if not composer:
        return work_slug

    tokens = work_slug.split("-")
    tokens = [t for t in tokens if t.lower() != composer.lower()]
    return "-".join(tokens)

def canonical_work(piece_dir: str, composer: str) -> str:
    s = slug(piece_dir)

    # Handful of known canonical cleanups.
    replacements = {
        "1812-Overture": "1812-Overture",
        "Mia-and-Sebastian-s-Theme": "Mia-and-Sebastian-Theme",
        "Mia-and-Sebastian-s-Theme": "Mia-and-Sebastians-Theme",
        "Mia-and-Sebastian-s-Theme": "Mia-and-Sebastian-Theme",
        "Brandenburg-3-Bach": "Brandenburg-3-Mvt-1",
        "Brandenburg-3-Mvt-3": "Brandenburg-3-Mvt-3",
        "Bach-Air-on-the-G-String": "Air-on-the-G-String",
        "Mozart-Eine-Kleine-Nachtmusik": "Eine-Kleine-Nachtmusik",
        "Mozart-40": "Symphony-40",
        "Corelli-xmas-cto": "Christmas-Concerto",
        "Up-Theme-Married-Life": "Married-Life",
        "Djawadi-Game-Thrones": "Game-of-Thrones",
        "Rossini-William-Tell": "William-Tell",
        "Saint-Saens-Symph-3-Mvt-2": "Symphony-3-Mvt-2",
        "Vivaldi-Cto-RV-565-Chamber-Group-ONLY": "Concerto-RV-565",
        "Vivaldi-Cto-RV-522-Chamber-Group-ONLY": "Concerto-RV-522",
        "Queen-of-Night-Mozart": "Queen-of-the-Night",
        "Swan-Lake-Tchaikovsky": "Swan-Lake",
        "Jupiter-Hymn-Holst": "Jupiter",
        "Rachmaninoff-Prelude": "Prelude",
        "Bartok-Romanian-Dances": "Romanian-Dances",
        "Howls-Moving-Castle": "Howls-Moving-Castle",
        "Kikis-Delivery-Service": "Kikis-Delivery-Service",
        "Tchaikovsky-Andante": "Andante-Cantabile",
        "Dvorak-Serenade-Waltz": "Serenade-Waltz",
        "Holberg-Suite-Prelude": "Holberg-Suite-Prelude",
        "Judas-Maccabaeus": "Judas-Maccabaeus",
    }

    if s in replacements:
        return replacements[s]

    s = remove_composer_tokens(s, composer)
    return s

def main():
    with INVENTORY.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out_rows = []

    seen = set()

    for row in rows:
        rel = row["REL-PATH"]
        piece = row["PIECE-DIR"]

        if rel in seen:
            continue
        seen.add(rel)

        composer = guess_composer(piece)
        work = piece
        dest_composer = composer
        dest_work = canonical_work(piece, composer)

        notes = ""
        if not composer:
            notes = "REVIEW: composer not guessed"

        out_rows.append({
            "SOURCE-REL-PATH": rel,
            "COMPOSER": composer,
            "WORK": work,
            "DEST-COMPOSER": dest_composer,
            "DEST-WORK": dest_work,
            "NOTES": notes,
        })

    fieldnames = [
        "SOURCE-REL-PATH",
        "COMPOSER",
        "WORK",
        "DEST-COMPOSER",
        "DEST-WORK",
        "NOTES",
    ]

    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {OUT}")
    print(f"Rows: {len(out_rows)}")

if __name__ == "__main__":
    main()
