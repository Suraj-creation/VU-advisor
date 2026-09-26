"""Rebuild every table from the source files (no writes) and assert all validation invariants + golden facts."""
from advisor import config
from advisor.ingest import build, excel, validate


def test_knowledge_base_invariants_and_golden_facts():
    units = excel.extract(config.SOURCES["semester_spread"]) + excel.extract(config.SOURCES["minors"])
    offerings, options = build.build_offerings(units)
    baskets = build.build_baskets(units, options, offerings)
    structure = build.build_structure(units, options, offerings)
    minors, summary = build.build_minors(units)
    terms = build.build_terms()
    courses = build.build_courses(options, minors)
    issues = build.build_issues(units, offerings, options, baskets, structure, minors, summary)
    tables = {"offerings": offerings, "options": options, "baskets": baskets, "structure_courses": structure,
              "minors": minors, "minor_batches": summary, "terms": terms, "courses": courses, "issues": issues}
    handbook = (config.CURATED / "handbook.md").read_text(encoding="utf-8")
    chunks = build.chunk_markdown(handbook, "handbook", "Student Handbook") + build.chunk_markdown(
        (config.CURATED / "sop.md").read_text(encoding="utf-8"), "sop", "SOP")
    ok, report = validate.run(units, tables, chunks, handbook)
    assert ok, "\n".join(line for line in report.splitlines() if "FAIL" in line)


def test_split_options_pairs_codes_titles_and_ltp():
    slot, opts = build.split_options("MATH401/\nCOMP401", "SPT-Course #1-Probabilistic Graph Models LTP: 3-0-2\n/Web Framework LTP: 2-0-4",
                                     "NIL/NIL", 2, 0, 4, 4)
    assert slot == "Specialization course #1"
    assert [(o["code"], o["title"], o["L"], o["T"], o["P"]) for o in opts] == [
        ("MATH401", "Probabilistic Graph Models", 3, 0, 2), ("COMP401", "Web Framework", 2, 0, 4)]


def test_prereq_parsing():
    assert build.parse_prereq("ECON201, ECON202/ ECON207")[1] == [["ECON201"], ["ECON202", "ECON207"]]
    assert build.parse_prereq("NIL") == ("NIL", [])
    assert build.parse_prereq("DATA 301")[1] == [["DATA301"]]
