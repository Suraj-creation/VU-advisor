"""FastAPI app: chat + voice transcription + synthetic profiles + static UI.

    uvicorn advisor.server:app --reload        # then open http://127.0.0.1:8000
"""
import json
import time
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config

app = FastAPI(title="VU AI Academic Advisor")
STATIC = config.ROOT / "advisor" / "static"
PROFILES = {p["id"]: p for p in json.loads((config.ROOT / "eval" / "profiles.json").read_text(encoding="utf-8"))}
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # Azure OpenAI transcription limit


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    thread_id: str | None = None
    profile_id: str | None = None


@app.on_event("startup")
def warm_up():
    """Load the search index, graph and Azure clients before the first question (avoids a slow first answer)."""
    from .retrieval import embed_query, index
    if index()[2] is not None:
        embed_query("warm up")  # opens the Bedrock connection
    if config.azure_ready(config.CHAT_DEPLOYMENT):
        from . import graph
        graph._GRAPH = graph.build()
        graph.llm(True)
        graph.llm(False).invoke("Reply OK")  # opens the Azure connection (TLS) so the first student question is fast


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    return {"chat": config.azure_ready(config.CHAT_DEPLOYMENT), "embeddings": config.EMB_PATH.exists(),
            "transcription": config.azure_ready(config.TRANSCRIBE_DEPLOYMENT), "knowledge_base": config.DB_PATH.exists()}


@app.get("/api/profiles")
def profiles():
    return [{"id": p["id"], "label": p["label"], "batch": p["batch"], "current_semester": p["current_semester"],
             "cgpa": p["cgpa"], "minor": p["minor"], "notes": p["notes"],
             "credits_earned": p.get("credits_earned"), "failed_courses": p.get("failed_courses") or []} for p in PROFILES.values()]


@app.post("/api/chat")
def chat(body: ChatIn):
    if body.profile_id and body.profile_id not in PROFILES:
        raise HTTPException(400, "Unknown profile")
    thread = body.thread_id or uuid.uuid4().hex
    profile = PROFILES.get(body.profile_id)
    if not config.azure_ready(config.CHAT_DEPLOYMENT):
        return {**preview(body.message), "thread_id": thread}
    from .graph import ask
    # A profile switch starts a fresh conversation so one student's record never leaks into another's thread.
    out = ask(body.message, thread_id=f"{thread}:{body.profile_id or 'none'}", profile=profile)
    return {**out, "thread_id": thread}


def preview(message):
    """No LLM configured yet: show the retrieved evidence so the pipeline can still be checked end to end."""
    from .retrieval import search
    t0 = time.perf_counter()
    hits = search(message, k=4)
    sources = [{"id": f"S{i}", "citation": h["citation"], "tool": "search_documents", "snippet": h["text"][:600]} for i, h in enumerate(hits, 1)]
    answer = ("**Preview mode** – Azure OpenAI chat is not configured yet (fill in `.env`), so no answer is generated. "
              "These are the passages the advisor would ground its answer in:\n\n" + "\n".join(f"- [{s['id']}] {s['citation']}" for s in sources))
    return {"answer": answer, "sources": sources, "latency_ms": round((time.perf_counter() - t0) * 1000),
            "flags": {"tools": ["search_documents"], "cited": [s["id"] for s in sources], "preview": True}}


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    if not config.azure_ready(config.TRANSCRIBE_DEPLOYMENT):
        raise HTTPException(503, "Voice input needs AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT in .env")
    data = await audio.read()
    if not data or len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(400, "Audio must be between 1 byte and 25 MB")
    from openai import AzureOpenAI
    client = AzureOpenAI(azure_endpoint=config.AZURE_ENDPOINT, api_key=config.AZURE_API_KEY, api_version=config.TRANSCRIBE_API_VERSION)
    r = client.audio.transcriptions.create(model=config.TRANSCRIBE_DEPLOYMENT, file=(audio.filename or "speech.webm", data, audio.content_type or "audio/webm"),
                                           prompt="Vidyashilp University academic advising. Course codes like DATA301, COMP201, MATH203; CGPA, L-T-P, semester, minor.")
    return {"text": r.text}


app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/assets", StaticFiles(directory=config.ROOT / "assets"), name="assets")  # official logo + campus photo
