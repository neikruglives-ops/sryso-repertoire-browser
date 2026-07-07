# Architecture

The canonical repository representation of the repertoire database is:

`data/SRYSO-Repertoire-Library.csv`

The same data also lives as a Google Sheet. The Google Sheet is the collaborative editing interface for humans and is periodically downloaded/exported as `data/SRYSO-Repertoire-Library.csv`.

The SRYSO repository consists of a few complementary components:

1. GitHub stores the repository metadata, scripts, normalization tables, and documentation.

2. Google Drive stores the PDF library itself.

3. Google Drive also hosts the human-facing and admin-editable SRYSO-Repertoire-Library spreadsheet.

# Components

The SRYSO repository consists of several complementary components:

1. **Git Repository (hosted on GitHub)**

   Stores the repository itself, including:

   - `data/`
   - `reference/`
   - `scripts/`
   - `documents/`
   - `documentation/`
   - `logs/`

   The GitHub repository preserves the project's architecture, metadata, normalization tables, scripts, documentation, and audit history.

2. **Google Drive PDF Library**

   Stores the canonical PDF repository:

   ```
   PDFs/
       Composer/
           Work/
               CURRENT/
               Versions/
               Arrangements/
   ```

   PDF files are intentionally excluded from Git.

3. **Google Sheets**

   Hosts the collaborative, human-editable
   `SRYSO-Repertoire-Library` spreadsheet.

   The spreadsheet is periodically exported and committed as

   `data/SRYSO-Repertoire-Library.csv`

   so that the repository always contains a canonical, version-controlled copy.

# Canonical directory layout

The canonical directory layout for a work is:

```
PDFs/
    Composer/
        Work/
            CURRENT/
                SCORE.pdf
                Composer-Work.mscz
                VN-1.pdf
                VN-2.pdf
                VA.pdf
                VC.pdf
                ...
```

Example:

```
PDFs/Vivaldi/Concerto-RV-522/
    CURRENT/
        SCORE.pdf
        Vivaldi-Concerto-RV-522.mscz
        VN-1.pdf
        VN-2.pdf
        VA.pdf
        VC.pdf
        DB.pdf
```

`CURRENT/` always represents the canonical active edition.

Future revisions belong under `Versions/`.

Normalization belongs in `reference/*.csv`, never hard-coded into Python.
