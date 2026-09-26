"""Four-stage evaluation (assignment Phases 4-5):  Basic LLM -> Structured prompt -> RAG -> RAG + tools + student data.

    python eval/run_eval.py                 # all stages, rule-based scoring
    python eval/run_eval.py --judge         # also ask the LLM to grade each answer against the expected outcome
    python eval/run_eval.py --stages full   # subset: basic,prompted,rag,full

Scoring per case (see eval/README section in the project README):
  correct       all `must` patterns + one `must_any` present, expected behaviour shown, no `must_not`
  partial       some required content or behaviour present
  hallucinated  a `must_not` pattern (fabricated/wrong specific) appears, or eligibility declared on missing info
  incorrect     otherwise
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage  # noqa: E402

from advisor import config, graph  # noqa: E402
from advisor.prompts import RULES  # noqa: E402
from advisor.retrieval import search  # noqa: E402

CASES = json.loads((ROOT / "eval" / "test_cases.json").read_text(encoding="utf-8"))
PROFILES = {p["id"]: p for p in json.loads((ROOT / "eval" / "profiles.json").read_text(encoding="utf-8"))}
OUT = ROOT / "eval" / "results"

PROMPTED = RULES.split("TOOL GUIDE")[0].replace("You reach them only\nthrough tools.", "You do not have the documents in this mode.") + \
    "\nNo documents or tools are available in this mode: if you are not certain, say you do not have the information."
CONFLICT = re.compile(r"conflict|disagree|inconsisten|does not (exist|appear)|doesn't (exist|appear)|not found|discrepan|same semester|mismatch|data issue|no precedence|however", re.I)
INSUFF = re.compile(r"(do(es)?n['’]?t|do(es)? not|cannot|can't|unable to) (contain|have|find|include|mention|specify|provide|confirm)|not (available|specified|mentioned|covered|included|listed|provided) in|no information", re.I)
DECLINE = re.compile(r"(only|can(not|'t)) (help|assist|answer)|outside (my|the) scope|not able to help|academic advis|limited to|recommend checking", re.I)


def stage_basic(case):
    return {"answer": graph.llm(False).invoke([HumanMessage(case["query"])]).content, "sources": []}


def stage_prompted(case):
    return {"answer": graph.llm(False).invoke([SystemMessage(PROMPTED), HumanMessage(case["query"])]).content, "sources": []}


def stage_rag(case):
    hits = search(case["query"], k=8)
    ctx = "\n\n".join(f"<passage id=\"S{i}\" source=\"{h['citation']}\">\n{h['text']}\n</passage>" for i, h in enumerate(hits, 1))
    sys_msg = RULES.split("TOOL GUIDE")[0] + "\nAnswer only from the passages below; cite passage ids like [S2].\n<documents>\n" + ctx + "\n</documents>"
    ans = graph.llm(False).invoke([SystemMessage(sys_msg), HumanMessage(case["query"])]).content
    cited = set(re.findall(r"\[(S\d+)\]", ans))
    return {"answer": ans, "sources": [h["citation"] for i, h in enumerate(hits, 1) if f"S{i}" in cited]}


def stage_full(case):
    out = graph.ask(case["query"], thread_id=f"eval-{case['id']}-{time.time()}", profile=PROFILES.get(case.get("profile")))
    return {"answer": out["answer"], "sources": [s["citation"] for s in out["sources"]]}


STAGES = {"basic": stage_basic, "prompted": stage_prompted, "rag": stage_rag, "full": stage_full}


def found(pat, text):
    return re.search(pat, text, re.I) is not None


def score(case, ans):
    must = case.get("must", [])
    got = [p for p in must if found(p, ans)]
    any_ok = not case.get("must_any") or any(found(p, ans) for p in case["must_any"])
    bad = [p for p in case.get("must_not", []) if found(p, ans)]
    behaviour = {
        "follow_up": ("?" in ans) if case.get("expect_follow_up") else None,
        "conflict": bool(CONFLICT.search(ans)) if case.get("expect_conflict") else None,
        "insufficient": bool(INSUFF.search(ans)) if case.get("expect_insufficient") else None,
        "decline": bool(DECLINE.search(ans)) if case.get("expect_decline") else None,
    }
    beh_ok = all(v for v in behaviour.values() if v is not None)
    if bad:
        label = "hallucinated"
    elif len(got) == len(must) and any_ok and beh_ok:
        label = "correct"
    elif got or (any_ok and case.get("must_any")) or any(v for v in behaviour.values() if v):
        label = "partial"
    else:
        label = "incorrect"
    return label, behaviour


def judge(case, ans):
    prompt = (f"Grade an academic-advisor answer against the verified expected outcome.\nQUESTION: {case['query']}\n"
              f"EXPECTED: {case['expected']}\nANSWER: {ans}\n\nReply with JSON only: "
              '{"label": "correct|partially_correct|unsupported_hallucinated|incorrect", "reason": "<one sentence>"}')
    raw = graph.llm(False).invoke([HumanMessage(prompt)]).content
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        return json.loads(m.group()) if m else {"label": "unparsed", "reason": raw[:200]}
    except json.JSONDecodeError:
        return {"label": "unparsed", "reason": raw[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", default="basic,prompted,rag,full")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated case ids")
    a = ap.parse_args()
    if not config.azure_ready(config.CHAT_DEPLOYMENT):
        sys.exit("Azure OpenAI chat is not configured (.env) - the evaluation needs an LLM.")
    cases = [c for c in CASES if not a.only or c["id"] in a.only.split(",")]
    OUT.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    rows = []
    for stage in a.stages.split(","):
        for c in cases:
            t0 = time.perf_counter()
            try:
                r = STAGES[stage](c)
            except Exception as e:
                r = {"answer": f"ERROR {type(e).__name__}: {e}", "sources": []}
            ms = round((time.perf_counter() - t0) * 1000)
            label, beh = score(c, r["answer"])
            src_ok = None
            if c.get("sources") and stage in ("rag", "full"):
                src_ok = any(re.search(p, s, re.I) for p in c["sources"] for s in r["sources"])
            row = {"stage": stage, "id": c["id"], "category": c["category"], "label": label, "latency_ms": ms,
                   "source_correct": src_ok, **{f"beh_{k}": v for k, v in beh.items()}, "n_sources": len(r["sources"]),
                   "query": c["query"], "answer": r["answer"], "sources": " | ".join(r["sources"])}
            if a.judge:
                j = judge(c, r["answer"])
                row["judge_label"], row["judge_reason"] = j.get("label"), j.get("reason")
            rows.append(row)
            print(f"{stage:9s} {c['id']:3s} {label:12s} {ms:6d} ms")
    with open(OUT / f"results-{stamp}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    summary = summarize(rows, cases)
    (OUT / f"summary-{stamp}.md").write_text(summary, encoding="utf-8")
    print("\n" + summary)


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "–"


def summarize(rows, cases):
    by = defaultdict(list)
    for r in rows:
        by[r["stage"]].append(r)
    elig = {c["id"] for c in cases if c.get("eligibility")}
    lines = ["| Metric | " + " | ".join(by) + " |", "|---|" + "---|" * len(by)]

    def line(name, f):
        lines.append(f"| {name} | " + " | ".join(f(rs) for rs in by.values()) + " |")
    line("Accuracy (correct)", lambda rs: pct(sum(r["label"] == "correct" for r in rs), len(rs)))
    line("Correct + partial", lambda rs: pct(sum(r["label"] in ("correct", "partial") for r in rs), len(rs)))
    line("Hallucination rate", lambda rs: pct(sum(r["label"] == "hallucinated" for r in rs), len(rs)))
    line("Correct eligibility decisions", lambda rs: pct(sum(r["label"] == "correct" for r in rs if r["id"] in elig), len(elig & {r["id"] for r in rs})))
    line("Incorrect recommendations (eligibility, count)", lambda rs: str(sum(r["label"] in ("incorrect", "hallucinated") for r in rs if r["id"] in elig)))
    line("Source/evidence correctness", lambda rs: pct(sum(r["source_correct"] is True for r in rs), sum(r["source_correct"] is not None for r in rs)))
    line("Missing information handled", lambda rs: pct(sum(r["label"] == "correct" for r in rs if r["category"] == "missing_info"), sum(r["category"] == "missing_info" for r in rs)))
    line("Conflicting rules handled", lambda rs: pct(sum(r["label"] == "correct" for r in rs if r["category"] == "conflict"), sum(r["category"] == "conflict" for r in rs)))
    line("Avg response time", lambda rs: f"{sum(r['latency_ms'] for r in rs) / len(rs) / 1000:.1f} s")
    line("Max response time", lambda rs: f"{max(r['latency_ms'] for r in rs) / 1000:.1f} s")
    if rows and "judge_label" in rows[0]:
        line("LLM-judge correct", lambda rs: pct(sum(r.get("judge_label") == "correct" for r in rs), len(rs)))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
