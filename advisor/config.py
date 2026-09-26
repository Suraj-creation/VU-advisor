"""Paths and Azure OpenAI settings. Everything configurable lives in .env (see .env.example)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

KB = ROOT / "knowledge_base"
CURATED = KB / "curated"
DB_PATH = KB / "advisor.sqlite"
CHUNKS_PATH = KB / "chunks.jsonl"
EMB_PATH = KB / "embeddings.npy"
EMB_CACHE = KB / "embedding_cache.json"

SOURCES = {
    "semester_spread": ROOT / "Semester_Spread_Structures_Sept_2026.xlsx",
    "minors": ROOT / "MinorCoursesforBTech_Students.xlsx",
    "handbook": ROOT / "4. Student Handbook Aug 2026.pdf",
    "sop": ROOT / "SOP STUDENT 17082026 - Final.pdf",
}

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "")
EMBED_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", "")
TRANSCRIBE_DEPLOYMENT = os.getenv("AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT", "")
# Some Azure resources expose transcription on a separate api-version.
TRANSCRIBE_API_VERSION = os.getenv("AZURE_OPENAI_TRANSCRIBE_API_VERSION", AZURE_API_VERSION)


EMB_MODEL_PATH = KB / "embeddings_model.txt"

# AWS Bedrock (embeddings only). boto3 reads AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY from the environment.
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
BEDROCK_EMBED_MODEL = os.getenv("BEDROCK_EMBED_MODEL", "")


def azure_ready(deployment: str) -> bool:
    return bool(AZURE_ENDPOINT and AZURE_API_KEY and deployment)


def bedrock_embed_ready() -> bool:
    return bool(BEDROCK_EMBED_MODEL and os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
