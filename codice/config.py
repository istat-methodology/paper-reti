"""Percorsi del progetto. I microdati non sono nel repository (vedi microdati/README.md).
Per usare una copia dei microdati in un'altra cartella: export RETI_MICRODATI=/percorso/microdati"""
import os
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
MICRODATI = Path(os.environ.get("RETI_MICRODATI", REPO / "microdati"))
RIFERIMENTI = REPO / "riferimenti"
RISULTATI = REPO / "risultati"
DOCS = REPO / "docs"
