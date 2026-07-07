# Directory Conventions

This document defines the canonical directory structure for the SRYSO Repertoire Project.

## Top-Level Layout

```
PDFs/
reference/
data/
scripts/
documents/
documentation/
logs/
```

Each directory has a single responsibility.

- `PDFs/` — canonical music library (Google Drive)
- `reference/` — normalization tables and controlled vocabularies
- `data/` — primary spreadsheet data
- `scripts/` — automation utilities
- `documents/` — architectural and design documentation
- `documentation/` — generated or user-facing documentation
- `logs/` — migration logs, surveys, and audit artifacts

---

## Composer Directory

Each composer receives a single canonical directory.

```
PDFs/
    Vivaldi/
    Mozart/
    Bach/
```

Composer directory names should be concise and human-readable.

---

## Work Directory

Each work receives a canonical directory beneath its composer.

```
PDFs/
    Vivaldi/
        Concerto-RV-522/
```

Work names should be stable.

Avoid embedding temporary information such as revisions or dates.

---

## CURRENT/

`CURRENT/` contains the canonical edition used by the orchestra.

```
CURRENT/
    SCORE.pdf
    VN-1.pdf
    VN-2.pdf
    VA.pdf
    VC.pdf
    Composer-Work.mscz
```

The spreadsheet always points to the work directory.

Users navigate into `CURRENT/` for the active performing materials.

---

## Versions/

Historical revisions belong here.

```
Versions/
    2026-09-14/
    2026-10-03/
```

These preserve previous editions without affecting the canonical version.

---

## Future Arrangements

Alternate realizations may eventually be stored separately.

For example:

```
Arrangements/
    Reduced-Orchestra/
    String-Orchestra/
```

This directory is reserved for musically distinct arrangements, not ordinary revisions.

---

## Part Naming

Part filenames use canonical abbreviations.

Examples:

```
SCORE.pdf
VN-1.pdf
VN-2.pdf
VA.pdf
VC.pdf
DB.pdf
PF.pdf
HP.pdf
```

Canonical abbreviations are defined in:

```
reference/PART-NORMALIZATION.csv
```

Scripts should never hard-code alternate spellings.

---

## Naming Philosophy

Prefer names that are:

- stable
- concise
- human-readable
- deterministic

Filesystem names are intended to remain stable over the lifetime of the repository.
