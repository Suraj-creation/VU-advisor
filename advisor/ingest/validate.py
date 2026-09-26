"""Build-time invariants + golden facts. Every golden fact was checked by hand against the source cells."""
import re
from collections import Counter, defaultdict

# Layout snapshot of the source workbooks (update deliberately if the sources change).
EXPECTED_SLOTS = {2022: 55, 2023: 54, 2024: 52, 2025: 52, 2026: 49}
EXPECTED_STRUCT_ROWS = 254
EXPECTED_MINOR_ROWS = 165  # 151 course rows + 14 TBA/TBD/"Don't know" credit placeholders ("No Students" excluded)
KNOWN_ANOMALIES = {("Sem_Spread_DS_2026", "BL12"), ("Sem_Spread_DS_2026", "BL13")}


def run(units, t, chunks, handbook_md):
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    opts, offs, minors = t["options"], t["offerings"], t["minors"]
    issue_ids = {i["id"] for i in t["issues"]}
    cats = Counter(i["category"] for i in t["issues"])

    def opt(batch, code=None, sem=None, title=None):
        hits = [o for o in opts if o["batch"] == batch and (code is None or o["code"] == code)
                and (sem is None or o["semester"] == sem) and (title is None or o["title"] == title)]
        assert len(hits) == 1, f"expected one option for {batch} {code} {sem} {title}, got {len(hits)}"
        return hits[0]

    # ---- coverage / layout
    got = Counter(o["batch"] for o in offs)
    check("Every semester-spread course cell extracted (per-batch slot counts)", dict(got) == EXPECTED_SLOTS, str(dict(got)))
    anomalies = {(u["source"]["sheet"], u["source"]["locator"]) for u in units if u["content"]["table"] == "anomaly"}
    check("No unexpected cells outside the course grid", anomalies <= KNOWN_ANOMALIES, str(sorted(anomalies - KNOWN_ANOMALIES)))
    check("Every Struct course line extracted", len(t["structure_courses"]) == EXPECTED_STRUCT_ROWS, str(len(t["structure_courses"])))
    base_minor = [m for m in minors if m["option_no"] == 1]
    check("Every minor-table row extracted", len(base_minor) == EXPECTED_MINOR_ROWS, str(len(base_minor)))

    # ---- arithmetic invariants
    per_batch = defaultdict(float)
    for o in offs:
        per_batch[o["batch"]] += o["C"] or 0
    check("Each batch's semester plan totals 180 credits", all(v == 180 for v in per_batch.values()), str(dict(per_batch)))
    struct_ok = all(b["credits_struct"] == b["credits_computed"] for b in t["baskets"])
    check("Basket credits: course sums equal the Struct sheet for every batch", struct_ok,
          str([(b["batch"], b["basket_code"], b["credits_struct"], b["credits_computed"]) for b in t["baskets"] if b["credits_struct"] != b["credits_computed"]]))
    unflagged = [(b["batch"], b["basket_code"]) for b in t["baskets"]
                 if b["fixed_min_semspread"] != b["credits_computed"] and f"basket::{b['batch']}::{b['basket_code']}" not in issue_ids]
    check("Every Fixed-Min vs computed basket mismatch is flagged as an issue", not unflagged, str(unflagged))
    bad_minor = [(s["minor"], s["batch"], s["total_credits"]) for s in t["minor_batches"] if s["status"] == "offered" and s["total_credits"] != 24]
    check("Every offered minor totals 24 credits (courses + TBA credits)", not bad_minor, str(bad_minor))
    check("Every programme course sits in semester 1-8", all(1 <= o["semester"] <= 8 for o in offs))
    check("Every non-placeholder minor course has a semester 1-8",
          all(1 <= (m["semester"] or 0) <= 8 for m in minors if not m["is_placeholder"]))
    check("Every confirmed course code is well-formed",
          all(re.fullmatch(r"[A-Z]{3,4}\d{3}", o["code"]) for o in opts if o["code_status"] == "ok"))
    known = {o["code"] for o in opts if o["code_status"] == "ok"} | {m["code"] for m in minors if m["code"]}
    dangling = [(o["batch"], o["code"], g) for o in opts for grp in o["prereq_groups"] for g in grp
                if re.fullmatch(r"[A-Z]{3,4}\d{3}", g) and g not in known
                and f"prereq_unknown::{o['batch']}::{o['code']}::{g}" not in issue_ids]
    check("Every unresolvable prerequisite code is flagged", not dangling, str(dangling))

    # ---- golden facts (hand-verified against the sheets)
    g = []
    try:
        o = opt(2023, "COMP206"); g.append(("2023 COMP206 = S5, 3-0-2, 4 cr, prereq COMP204+COMP207",
                                            (o["semester"], o["L"], o["T"], o["P"], o["C"], o["prereq_groups"]) == (5, 3, 0, 2, 4, [["COMP204"], ["COMP207"]])))
        o = opt(2023, "DATA303"); g.append(("2023 DATA303 MLOps = S6, 1-0-2, 2 cr", (o["semester"], o["L"], o["T"], o["P"], o["C"]) == (6, 1, 0, 2, 2)))
        o = opt(2022, "DATA207"); g.append(("2022 DATA207 Human Centric AI = S5, B4, 2 cr", (o["semester"], o["basket_code"], o["C"], o["title"]) == (5, "B4", 2, "Human Centric AI")))
        o = opt(2025, "DATA301"); g.append(("2025 DATA301 prereq DATA206+MATH301 (DATA206 flagged)",
                                            o["prereq_groups"] == [["DATA206"], ["MATH301"]] and "prereq_unknown::2025::DATA301::DATA206" in issue_ids))
        o = opt(2022, "MATH401"); g.append(("2022 MATH401 = Probabilistic Graph Models 3-0-2 (LTP from title)", (o["title"], o["L"], o["T"], o["P"], o["C"]) == ("Probabilistic Graph Models", 3, 0, 2, 4)))
        o = opt(2022, "COMP401"); g.append(("2022 COMP401 = Web Framework 2-0-4", (o["title"], o["L"], o["T"], o["P"]) == ("Web Framework", 2, 0, 4)))
        o = opt(2025, "TBA", 7); g.append(("2025 SPT#3 option 1 = Image Processing and Computer Vision, code TBA", o["title"] == "Image Processing and Computer Vision"))
        o = opt(2025, "COMP405", 7); g.append(("2025 SPT#3 option 2 = COMP405 Cloud & Cognitive Computing", o["title"] == "Cloud & Cognitive Computing"))
        o = opt(2022, None, 7, "Cloud Computing"); g.append(("2022 SPT#4 option 2 = Cloud Computing, code not given", o["code_status"] == "not_given"))
        o = opt(2026, "COMP211"); g.append(("2026 COMP211 Operating Systems = S4, B3, 3-0-2, 4 cr", (o["semester"], o["basket_code"], o["L"], o["T"], o["P"], o["C"]) == (4, "B3", 3, 0, 2, 4)))
        o = opt(2024, "PSYC101"); g.append(("2024 PSYC101/ECON101 paired choice split into 2 options", opt(2024, "ECON101")["offering_id"] == o["offering_id"]))
        sems = defaultdict(float)
        for x in offs:
            sems[(x["batch"], x["semester"])] += x["C"] or 0
        g.append(("Semester totals: 2024 S1=21, 2023 S3=29, 2025 S5=27, 2026 S3=20",
                  (sems[(2024, 1)], sems[(2023, 3)], sems[(2025, 5)], sems[(2026, 3)]) == (21, 29, 27, 20)))
        b = {(x["batch"], x["basket_code"]): x for x in t["baskets"]}
        g.append(("2026 University Core: Fixed Min 24, Struct 18, courses 18", (b[(2026, "B1")]["fixed_min_semspread"], b[(2026, "B1")]["credits_struct"], b[(2026, "B1")]["credits_computed"]) == (24, 18, 18)))
        g.append(("2025 Open/Minor basket = 32 in all three sources", (b[(2025, "B6")]["fixed_min_semspread"], b[(2025, "B6")]["credits_struct"], b[(2025, "B6")]["credits_computed"]) == (32, 32, 32)))
        ms = {(x["minor"], x["batch"]): x for x in t["minor_batches"]}
        g.append(("Law minor 2025: 17 TBA credits", ms[("Law", 2025)]["tba_credits"] == 17))
        g.append(("Economics minor 2024: 'No Students'", ms[("Economics", 2024)]["status"] == "no_students"))
        g.append(("Start-up minor 2024 totals 24 (8 confirmed + 16 TBD)", (ms[("Start-up", 2024)]["total_credits"], ms[("Start-up", 2024)]["tba_credits"]) == (24, 16)))
        fin = [m for m in minors if m["minor"] == "Finance" and m["batch"] == 2025 and m["semester"] == 4]
        g.append(("Finance 2025 S4 course listed as 'New' (code pending), 4 cr", len(fin) == 1 and fin[0]["code_status"] == "new_course_code_pending" and fin[0]["C"] == 4))
        psy = {m["code"]: m["title"] for m in minors if m["minor"] == "Psychology" and m["batch"] == 2024 and m["semester"] == 3}
        g.append(("Psychology 2024 S3 = PSYC201 Biological Psychology / PSYC103 Foundations of Psychology I",
                  psy == {"PSYC201": "Biological Psychology", "PSYC103": "Foundations of Psychology I"}))
        g.append(("CDES217 (Design 2024) 2-3-0 vs 4 cr flagged by the credit norm check", "credit_norm::minor::Design::2024::CDES217" in issue_ids))
        tm = {(x["batch"], x["semester"]): x for x in t["terms"]}
        g.append(("Batch 2024 semester 5 = Jul/Aug–Dec 2026; batch 2023 semester 8 = Jan–Apr/May 2027",
                  (tm[(2024, 5)]["calendar_year"], tm[(2024, 5)]["months"], tm[(2023, 8)]["calendar_year"], tm[(2023, 8)]["months"]) == (2026, "Jul/Aug–Dec", 2027, "Jan–Apr/May")))
        g.append(("Attendance 75% vs 80% policy conflict registered", "policy::attendance_threshold" in issue_ids))
        g.append(("Struct_2026 Electives list includes Web Framework (4 cr)",
                  any(s["batch"] == 2026 and s["section"] == "Electives" and s["title"] == "Web Framework" and s["credits"] == 4 for s in t["structure_courses"])))
    except AssertionError as e:
        g.append((f"golden fact lookup failed: {e}", False))
    for name, ok in g:
        check(f"Golden fact: {name}", ok)

    # ---- documents & chunks
    check("Handbook Table 2 (grade points) present", "| A+ | 9 | Excellent |" in handbook_md and "| FA | 0 |" in handbook_md)
    p36 = handbook_md.split("<!-- pdf=36 ")[1].split("<!-- pdf=")[0] if "<!-- pdf=36 " in handbook_md else ""
    check("Handbook PDF p.36 holds §8.14-8.16, not the POSH overlay text", "8.15 Transcript" in p36 and "POSH" not in p36)
    check("No unmapped glyphs (U+FFFD) in the handbook markdown", "�" not in handbook_md)
    check("Attendance 75% (§7.2) and 80% (Code of Conduct §4.5) both present in handbook text",
          "seventy five percent (75%)" in handbook_md and "attendance requirement of 80%" in handbook_md)
    doc_chunks = [c for c in chunks if c["doc_type"] in ("handbook", "sop")]
    check("Every handbook/SOP chunk carries page provenance", all(c["meta"]["printed_pages"] for c in doc_chunks),
          str([c["id"] for c in doc_chunks if not c["meta"]["printed_pages"]][:5]))
    check("Chunk ids are unique", len({c["id"] for c in chunks}) == len(chunks))
    check("Every course card names its batch", all(" batch " in c["text"] for c in chunks if c["doc_type"] == "course"))

    ok = all(c[1] for c in checks)
    lines = ["# Knowledge base validation report", "",
             f"**Result: {'PASS' if ok else 'FAIL'}** – {sum(c[1] for c in checks)}/{len(checks)} checks passed.", "",
             "| Status | Check | Detail |", "|---|---|---|"]
    lines += [f"| {'PASS' if okk else '**FAIL**'} | {n} | {d if not okk else ''} |" for n, okk, d in checks]
    lines += ["", "## Contents", "", "| Table | Rows |", "|---|---|"]
    lines += [f"| {k} | {len(v)} |" for k, v in t.items()]
    lines += [f"| retrieval chunks | {len(chunks)} ({dict(Counter(c['doc_type'] for c in chunks))}) |", "",
              "## Data-quality issues found in the sources (surfaced to users, not silently fixed)", "",
              "| Category | Count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(cats.items())]
    lines += ["", "### Warnings", ""] + [f"- **{i['title']}** – {i['detail']}" for i in t["issues"] if i["severity"] == "warning"]
    return ok, "\n".join(lines) + "\n"
