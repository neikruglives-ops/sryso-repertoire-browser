# Migration Plan

This document describes the migration strategy used to build the SRYSO Repertoire Project.

The migration process is intended to be repeatable, deterministic, and auditable.

The original migration proceeded in several phases.

---

# Phase 1 — Survey

Before moving any files, survey the existing repository.

The goal is to understand the existing collection before attempting to reorganize it.

Scripts used:

- survey-tree
- survey-pieces
- survey-parts

Outputs:

- tree survey
- repertoire inventory
- part inventory

---

# Phase 2 — Normalize

Build canonical vocabularies.

Examples:

- PART-NORMALIZATION.csv
- COMPOSER-NORMALIZATION.csv
- WORK-NORMALIZATION.csv

Repository knowledge belongs in these tables rather than in code.

---

# Phase 3 — Build Migration Map

Construct a deterministic migration map.

Each source file receives one explicit destination.

The migration map is reviewed manually before any files are copied.

---

# Phase 4 — Dry Run

Generate a dry-run report.

No files are modified.

The dry run is used to identify:

- duplicate destinations
- unknown parts
- assumed scores
- normalization gaps
- unusual arrangements

Reference tables are updated until the dry run is satisfactory.

---

# Phase 5 — Execute Migration

Only after the dry run has been reviewed should the migration be executed.

The migration script copies files into the canonical repository structure.

The migration is intended to be idempotent.

---

# Phase 6 — Populate Repository

Populate the repertoire spreadsheet.

Verify:

- composer
- work
- folder links
- score sources
- metadata

---

# Future Migrations

Future migrations should follow the same philosophy.

Survey first.

Normalize second.

Copy last.

Never move files before understanding them.

Whenever possible:

- automate repetitive work
- review generated output
- preserve audit logs

Repository knowledge should be accumulated rather than rediscovered.

# Migration Philosophy

The purpose of the migration is not merely to copy files.

Its purpose is to transform an organically grown collection into a curated repository.

Whenever uncertainty exists, preserve information rather than discard it.

Repository quality is improved through repeated survey, normalization, and review rather than by attempting to solve every problem in a single pass.
