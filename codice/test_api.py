"""Prova di connessione al modello (Azure Foundry). Legge chiave, endpoint e deployment da .env nella radice del repo.
Prova alcune varianti dell'URL e stampa quella che funziona. La chiave non viene mai stampata.
Richiede: pip install openai python-dotenv   (python-dotenv è facoltativo)
Uso: python codice/test_api.py"""
import os
import sys
from config import REPO

try:
    from openai import OpenAI
except ImportError:
    sys.exit("Manca openai: pip install openai python-dotenv")

env = REPO / ".env"
if not env.exists():
    sys.exit(f"Manca {env}: copia .env.example in .env e inserisci i valori")
for riga in env.read_text(encoding="utf-8").splitlines():
    if "=" in riga and not riga.strip().startswith("#"):
        k, v = riga.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

chiave = os.environ.get("AZURE_OPENAI_API_KEY", "")
ep = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
dep = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
if not (chiave and ep and dep):
    sys.exit("Nel .env mancano AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT o AZURE_OPENAI_DEPLOYMENT")

host = ep.split("/api/projects")[0]
varianti = [ep, ep + "/openai/v1", host + "/openai/v1", host.replace(".services.ai.", ".openai.") + "/openai/v1"]
trovata = False
for base in dict.fromkeys(varianti):
    try:
        c = OpenAI(base_url=base, api_key=chiave, timeout=60)
        r = c.responses.create(model=dep, input="Rispondi solo con la parola: ok")
        print("OK  ", base, "| risposta:", (r.output_text or "")[:40], "| modello:", getattr(r, "model", "?"))
        trovata = True
        break
    except Exception as e:
        msg = str(e).replace(chiave, "***")[:200].replace("\n", " ")
        print("ERR ", base, "|", type(e).__name__, "|", msg)
print("\nURL da usare come AZURE_OPENAI_ENDPOINT:" if trovata else "\nNessuna variante ha funzionato.", base if trovata else "")
