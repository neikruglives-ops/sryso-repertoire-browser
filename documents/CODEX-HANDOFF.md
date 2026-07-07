# Codex Handoff: SRYSO Repertoire Project

This repository supports the SRYSO Repertoire Library.

Primary goals:
- Maintain a canonical repertoire spreadsheet.
- Maintain normalized reference tables.
- Generate/maintain a searchable browser interface.
- Keep PDFs out of Git; PDFs live in Google Drive.

Important directories:
- `data/` — main CSV data
- `reference/` — controlled vocabularies and normalization tables
- `scripts/` — migration/survey/build tools
- `logs/` — migration artifacts and audit trail
- `documents/` — architecture and conventions
- `sryso-repertoire-browser/` — future browser output

Core principles:
- Normalize vocabulary in CSV tables, not hard-coded Python.
- Scripts should be boring and data-driven.
- PDFs are operational assets, not Git-tracked source.
- `CURRENT/` is the canonical active edition.
- `Versions/` preserves revision history.
- `Arrangements/` contains alternate realizations/instrumentations.
