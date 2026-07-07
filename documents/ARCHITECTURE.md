# Architecture

The canonical repository representation of the repertoire database is:

`data/SRYSO-Repertoire-Library.csv`

The same data also lives as a Google Sheet. The Google Sheet is the collaborative editing interface for humans and is periodically downloaded/exported as `data/SRYSO-Repertoire-Library.csv`.

The SRYSO repository consists of a few complementary components:

1. GitHub stores the repository metadata, scripts, normalization tables, and documentation.

2. Google Drive stores the PDF library itself.

3. Google Drive also hosts the human-facing and admin-editable SRYSO-Repertoire-Library spreadsheet.

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
