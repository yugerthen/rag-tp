import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Clé API Groq manquante : vérifie ton fichier .env")

EMBEDDING_MODEL = "distiluse-base-multilingual-cased-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
CHROMA_DB_PATH = "./chroma_db"
CORPUS_CSV_PATH = "./data/corpus.csv"