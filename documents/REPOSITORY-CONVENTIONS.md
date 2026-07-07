# Repository Conventions

This document describes the conventions used throughout the SRYSO Repertoire Project.

The repository is intended to remain internally consistent over many years of use. When new repertoire is added, these conventions should be followed whenever practical.

---

# Guiding Principles

## Prefer convention over special cases.

When multiple reasonable naming choices exist, prefer the one most consistent with the existing repository.

Consistency is generally more valuable than perfect musicological precision.

---

## Canonical names are stable.

Directory names should not change merely because a better source or edition is discovered.

Instead:

- update the contents
- preserve the directory name

Stable names produce stable links.

---

## Normalize vocabulary.

Many historical spellings refer to the same musical concept.

Examples include:

```
Violin I
Violin 1
VIOLIN-1
Violins_1
```

These should all normalize to

```
VN-1
```

Normalization rules belong in

```
reference/*.csv
```

—not inside Python scripts.

---

# Filesystem Names

Filesystem names should be

- concise
- deterministic
- human-readable

Use hyphens instead of spaces.

Example:

```
Brandenburg-3-Mvt-1
```

rather than

```
Brandenburg Concerto No. 3 Movement 1
```

---

# Spreadsheet Values

The spreadsheet is intended for human readers.

Filesystem names are intended for stable directory names.

For this reason, the same work may appear slightly differently in the spreadsheet and the filesystem.

Example:

Spreadsheet

    COMPOSER
    Joseph Haydn

    WORK
    Emperor Quartet

Filesystem

    PDFs/
        Haydn/
            Emperor-Quartet/

Human-readable metadata belongs in the spreadsheet.

Stable, concise names belong in the filesystem.

---

# Canonical Filesystem Names

Filesystem names should be concise while remaining recognizable.

Examples:

Joseph Haydn
    → Haydn

Wolfgang Amadeus Mozart
    → Mozart

Antonio Vivaldi
    → Vivaldi

Franz Xaver Richter
    → Franz-Xaver-Richter

Johann Christian Bach
    → Johann-Christian-Bach

---

# Reference Tables

The repository's controlled vocabulary lives under

```
reference/
```

Examples include

```
PART-NORMALIZATION.csv
COMPOSER-NORMALIZATION.csv
WORK-NORMALIZATION.csv
READINESS-STATES.csv
```

Whenever possible, repository behavior should be controlled by these tables rather than hard-coded logic.

---

# Scripts

Scripts should be

- deterministic
- idempotent
- data-driven

Scripts should read repository conventions from the reference tables rather than embedding repository knowledge in code.

---

# Repository Knowledge

Whenever practical, knowledge belongs in the repository rather than in software.

For example:

- normalization rules belong in CSV tables
- naming conventions belong in documentation
- scripts consume repository knowledge

This approach minimizes code complexity while allowing the repository to evolve through data rather than program logic.

---

# Repository Evolution

The repository is expected to grow.

Reference tables are expected to expand as new repertoire is encountered.

Growth should occur by extending existing conventions rather than introducing competing conventions.

---

# Design Philosophy

The repository is intended to function as institutional memory.

It should preserve not only musical materials, but also the naming conventions, organizational structure, and accumulated experience of the organization.

Whenever possible, future improvements should simplify the repository rather than increasing its complexity.

The repository should remain understandable by a human reader with no prior knowledge beyond these documents.
