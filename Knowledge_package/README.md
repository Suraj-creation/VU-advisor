# Academic Advisor Knowledge Package — Verified

Generated from the two uploaded source workbooks:
- Semester_Spread_Structures_Sept_2026.xlsx
- MinorCoursesforBTech_Students.xlsx

## Verification status

PASS WITH CORRECTIONS.

The original source workbooks remain unchanged and are the source of truth.

## Key correction

`COMP401` was present as a standalone code in one source row with a blank title. It was incorrectly promoted to a canonical course entity in the first package and consequently generated a misleading retrieval document. It is now represented in `12_reference_codes.json` and `08_unresolved_entries.json` as reference-only/unresolved. No course title is inferred.

## Derived normalization

Clear mechanical issues were corrected only in derived fields:
- MGMT209 → Financial Statement Analysis
- MGMT330 → Introduction to Financial Accounting (R)
- UCOR205 → Socio-Cultural Perspectives on Indian Life

All raw source observations remain preserved.

## Retrieval

`10_retrieval_documents.jsonl` has unique IDs and provenance. Canonical course documents contain source observations rather than only a source-file label.

## Counts

- Semester offering records: 249
- Curriculum structure course records: 246
- Basket requirement records: 35
- Minor course records: 148
- Canonical course entities: 132
- Reference-only stable course codes: 1
- Distinct stable course codes observed: 133
- Retrieval documents: 826
- Conflicts/variants: 17
- Unresolved/special entries: 26

## Files

- 01_course_master.json
- 02_semester_offerings.json
- 03_curriculum_structure_courses.json
- 04_curriculum_basket_requirements.json
- 05_minor_courses.json
- 06_terminology_glossary.json
- 07_conflicts_and_variants.json
- 08_unresolved_entries.json
- 09_package_summary.json
- 10_retrieval_documents.jsonl
- 11_provenance_index.json
- 12_reference_codes.json
- 13_verification_report.json
- academic_advisor_normalized.xlsx
