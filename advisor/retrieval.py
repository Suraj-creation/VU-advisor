"""Hybrid retrieval: BM25 (exact terms, course codes) + dense embeddings (paraphrases), fused with RRF.

Corpus is ~700 chunks, so everything lives in memory: a BM25 index and a normalised numpy matrix.
Dense search is skipped (BM25-only) when embeddings were not built or Azure is not configured.
"""
import json
import re
from functools import lru_cache

import numpy as np
from rank_bm25 import BM25Okapi

from . import config, embeddings

SCOPES = {"policy": {"handbook", "sop", "issue"}, "curriculum": {"course", "plan", "basket", "minor", "course_overview", "terms", "issue"}}
STOP = set("a an the of to in on for and or is are was be by with as at from that this it its what which who how do does can i my me we you".split())
RRF_K = 60


def tokenize(text):
    t = text.lower()
    t = re.sub(r"\b([a-z]{3,4})\s+(\d{3})\b", r"\1\2", t)  # "DATA 301" -> "data301"
    t = re.sub(r"(?<![a-z])([ab])\s*\+", r"\1plus", t)  # grades "A+", "B+"
    return [w for w in re.findall(r"[a-z]+\d*|\d+(?:\.\d+)?%?", t) if w not in STOP]


@lru_cache(maxsize=1)
def index():
    chunks = [json.loads(line) for line in open(config.CHUNKS_PATH, encoding="utf-8")]
    bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks])
    vecs = None
    built_with = config.EMB_MODEL_PATH.read_text().strip() if config.EMB_MODEL_PATH.exists() else None
    if config.EMB_PATH.exists() and built_with and built_with == embeddings.model_id():  # query model must match
        v = np.load(config.EMB_PATH)
        vecs = v if len(v) == len(chunks) else None
    return chunks, bm25, vecs


@lru_cache(maxsize=256)
def embed_query(text):
    return embeddings.embed([text])[0]


def search(query, scope="all", k=6, pool=40):
    chunks, bm25, vecs = index()
    allowed = np.array([scope == "all" or c["doc_type"] in SCOPES.get(scope, ()) for c in chunks])
    lex = bm25.get_scores(tokenize(query))
    lex = np.where(allowed, lex, -np.inf)
    ranks = [np.argsort(-lex)[:pool]]
    dense = None
    if vecs is not None:
        dense = np.where(allowed, vecs @ embed_query(query), -np.inf)
        ranks.append(np.argsort(-dense)[:pool])
    fused = {}
    for r in ranks:
        for pos, i in enumerate(r):
            if np.isfinite(lex[i]) or (dense is not None and np.isfinite(dense[i])):
                fused[int(i)] = fused.get(int(i), 0) + 1 / (RRF_K + pos + 1)
    top = sorted(fused, key=fused.get, reverse=True)[:k]
    qt = set(tokenize(query))
    coverage = len(qt & set(tokenize(chunks[top[0]]["text"]))) / len(qt) if (top and qt) else 0.0
    # Titan v2 calibration (12 probe queries): in-scope max cosine >= 0.37, off-topic <= 0.26 -> cut at 0.30.
    weak = float(np.max(dense)) < 0.30 if dense is not None else coverage < 0.5
    return [{**chunks[i], "score": round(fused[i], 4), "weak": weak} for i in top]
