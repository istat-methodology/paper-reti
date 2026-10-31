"""Riduce le immagini dei PDF in microdati/protocolli_pdf/ per restare sotto il limite di dimensione dell'endpoint.
Il testo nativo resta com'è; si riducono solo le immagini (scansioni). Gli originali sono in protocolli_pdf/_originali/.
Uso: python codice/pipeline_ai_v2/comprimi_pdf.py --codici 0902,0903,0908 [--dpi 110] [--qualita 60] [--prova]
Con --prova scrive in una cartella temporanea e non sostituisce i file."""
import argparse, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MICRODATI  # noqa: E402
try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    sys.exit("Manca PyMuPDF: pip install pymupdf")

ap = argparse.ArgumentParser()
ap.add_argument("--codici", required=True); ap.add_argument("--dpi", type=int, default=110)
ap.add_argument("--qualita", type=int, default=60); ap.add_argument("--prova", action="store_true")
o = ap.parse_args()
dest = Path(tempfile.mkdtemp()) if o.prova else None
for c in [x.strip() for x in o.codici.split(",")]:
    src = MICRODATI / "protocolli_pdf" / f"protocollo_{c}.pdf"
    doc = fitz.open(src)
    prima = src.stat().st_size / 1e6
    doc.rewrite_images(dpi_threshold=o.dpi + 20, dpi_target=o.dpi, quality=o.qualita)
    out = (dest or src.parent) / (f"protocollo_{c}.pdf" if o.prova else f"protocollo_{c}.tmp.pdf")
    doc.save(out, garbage=4, deflate=True, clean=True)
    doc.close()
    dopo = out.stat().st_size / 1e6
    if not o.prova:
        out.replace(src)
    print(f"{c}: {prima:.1f} MB -> {dopo:.1f} MB ({'prova in ' + str(dest) if o.prova else 'sostituito'})")
