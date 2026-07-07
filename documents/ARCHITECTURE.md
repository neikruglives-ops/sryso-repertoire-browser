# Architecture

The SRYSO repository consists of two complementary components.

1. GitHub stores the repository metadata, scripts, normalization tables, and documentation.

2. Google Drive stores the PDF library itself.

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
