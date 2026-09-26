# Knowledge base validation report

**Result: PASS** – 42/42 checks passed.

| Status | Check | Detail |
|---|---|---|
| PASS | Every semester-spread course cell extracted (per-batch slot counts) |  |
| PASS | No unexpected cells outside the course grid |  |
| PASS | Every Struct course line extracted |  |
| PASS | Every minor-table row extracted |  |
| PASS | Each batch's semester plan totals 180 credits |  |
| PASS | Basket credits: course sums equal the Struct sheet for every batch |  |
| PASS | Every Fixed-Min vs computed basket mismatch is flagged as an issue |  |
| PASS | Every offered minor totals 24 credits (courses + TBA credits) |  |
| PASS | Every programme course sits in semester 1-8 |  |
| PASS | Every non-placeholder minor course has a semester 1-8 |  |
| PASS | Every confirmed course code is well-formed |  |
| PASS | Every unresolvable prerequisite code is flagged |  |
| PASS | Golden fact: 2023 COMP206 = S5, 3-0-2, 4 cr, prereq COMP204+COMP207 |  |
| PASS | Golden fact: 2023 DATA303 MLOps = S6, 1-0-2, 2 cr |  |
| PASS | Golden fact: 2022 DATA207 Human Centric AI = S5, B4, 2 cr |  |
| PASS | Golden fact: 2025 DATA301 prereq DATA206+MATH301 (DATA206 flagged) |  |
| PASS | Golden fact: 2022 MATH401 = Probabilistic Graph Models 3-0-2 (LTP from title) |  |
| PASS | Golden fact: 2022 COMP401 = Web Framework 2-0-4 |  |
| PASS | Golden fact: 2025 SPT#3 option 1 = Image Processing and Computer Vision, code TBA |  |
| PASS | Golden fact: 2025 SPT#3 option 2 = COMP405 Cloud & Cognitive Computing |  |
| PASS | Golden fact: 2022 SPT#4 option 2 = Cloud Computing, code not given |  |
| PASS | Golden fact: 2026 COMP211 Operating Systems = S4, B3, 3-0-2, 4 cr |  |
| PASS | Golden fact: 2024 PSYC101/ECON101 paired choice split into 2 options |  |
| PASS | Golden fact: Semester totals: 2024 S1=21, 2023 S3=29, 2025 S5=27, 2026 S3=20 |  |
| PASS | Golden fact: 2026 University Core: Fixed Min 24, Struct 18, courses 18 |  |
| PASS | Golden fact: 2025 Open/Minor basket = 32 in all three sources |  |
| PASS | Golden fact: Law minor 2025: 17 TBA credits |  |
| PASS | Golden fact: Economics minor 2024: 'No Students' |  |
| PASS | Golden fact: Start-up minor 2024 totals 24 (8 confirmed + 16 TBD) |  |
| PASS | Golden fact: Finance 2025 S4 course listed as 'New' (code pending), 4 cr |  |
| PASS | Golden fact: Psychology 2024 S3 = PSYC201 Biological Psychology / PSYC103 Foundations of Psychology I |  |
| PASS | Golden fact: CDES217 (Design 2024) 2-3-0 vs 4 cr flagged by the credit norm check |  |
| PASS | Golden fact: Batch 2024 semester 5 = Jul/Aug–Dec 2026; batch 2023 semester 8 = Jan–Apr/May 2027 |  |
| PASS | Golden fact: Attendance 75% vs 80% policy conflict registered |  |
| PASS | Golden fact: Struct_2026 Electives list includes Web Framework (4 cr) |  |
| PASS | Handbook Table 2 (grade points) present |  |
| PASS | Handbook PDF p.36 holds §8.14-8.16, not the POSH overlay text |  |
| PASS | No unmapped glyphs (U+FFFD) in the handbook markdown |  |
| PASS | Attendance 75% (§7.2) and 80% (Code of Conduct §4.5) both present in handbook text |  |
| PASS | Every handbook/SOP chunk carries page provenance |  |
| PASS | Chunk ids are unique |  |
| PASS | Every course card names its batch |  |

## Contents

| Table | Rows |
|---|---|
| offerings | 262 |
| options | 282 |
| baskets | 35 |
| structure_courses | 254 |
| minors | 168 |
| minor_batches | 31 |
| terms | 55 |
| courses | 148 |
| issues | 135 |
| sources | 4 |
| retrieval chunks | 678 ({'handbook': 128, 'sop': 16, 'course': 253, 'plan': 40, 'basket': 5, 'minor': 31, 'course_overview': 148, 'terms': 5, 'issue': 52}) |

## Data-quality issues found in the sources (surfaced to users, not silently fixed)

| Category | Count |
|---|---|
| basket_total_mismatch | 3 |
| batch_variant | 32 |
| course_code_missing | 11 |
| credit_norm_mismatch | 2 |
| ltp_in_title | 9 |
| minor_courses_tba | 14 |
| minor_not_offered | 1 |
| policy_conflict | 3 |
| prereq_not_in_batch_plan | 27 |
| prereq_same_or_later_semester | 6 |
| prereq_unknown_code | 14 |
| sheet_anomaly | 4 |
| struct_code_from_other_batch | 8 |
| suspicious_code | 1 |

### Warnings

- **MATH205 Statistics with R (batch 2022, S2) requires MATH202, scheduled in S2 of the same plan** – The prerequisite is scheduled in the same or a later semester than the course itself, so it cannot be completed beforehand as planned.
- **DATA202 Exploratory Data Analysis (batch 2022) requires MATH203, which is not in the batch 2022 semester plan** – Prerequisite text: 'DATA201, MATH203'. MATH203 exists in other batches or minors but is not scheduled for batch 2022.
- **DATA207 Human Centric AI (batch 2022) requires COMP210, which does not exist anywhere in the curriculum data** – Prerequisite text: 'COMP210/COMP301'. No course with code COMP210 appears in any semester plan or minor list, so this prerequisite cannot be verified (possible typo in the source).
- **COMP206 Microprocessors and Computer Architecture (batch 2023, S5) requires COMP207, scheduled in S5 of the same plan** – The prerequisite is scheduled in the same or a later semester than the course itself, so it cannot be completed beforehand as planned.
- **DATA202 Exploratory Data Analysis (batch 2023) requires MATH203, which is not in the batch 2023 semester plan** – Prerequisite text: 'DATA201, MATH203'. MATH203 exists in other batches or minors but is not scheduled for batch 2023.
- **DATA404 Multi Modal Learning (batch 2024, S6) requires DATA302, scheduled in S6 of the same plan** – The prerequisite is scheduled in the same or a later semester than the course itself, so it cannot be completed beforehand as planned.
- **DATA405 Reinforcement Learning (batch 2024) requires MATH202, which is not in the batch 2024 semester plan** – Prerequisite text: 'MATH202, MATH204'. MATH202 exists in other batches or minors but is not scheduled for batch 2024.
- **COMP302 Internet of Things (batch 2025, S6) requires COMP208, scheduled in S6 of the same plan** – The prerequisite is scheduled in the same or a later semester than the course itself, so it cannot be completed beforehand as planned.
- **MATH301 Optimization Techniques for Data Science (batch 2025) requires MATH201, which is not in the batch 2025 semester plan** – Prerequisite text: 'MATH201'. MATH201 exists in other batches or minors but is not scheduled for batch 2025.
- **DATA301 Machine Learning (batch 2025) requires DATA206, which does not exist anywhere in the curriculum data** – Prerequisite text: 'DATA206, MATH301'. No course with code DATA206 appears in any semester plan or minor list, so this prerequisite cannot be verified (possible typo in the source).
- **DATA404 Multi Modal Learning (batch 2025, S6) requires DATA302, scheduled in S6 of the same plan** – The prerequisite is scheduled in the same or a later semester than the course itself, so it cannot be completed beforehand as planned.
- **DATA405 Reinforcement Learning (batch 2025) requires MATH202, which is not in the batch 2025 semester plan** – Prerequisite text: 'MATH202, MATH204'. MATH202 exists in other batches or minors but is not scheduled for batch 2025.
- **DATA405 Reinforcement Learning (batch 2025) requires MATH204, which is not in the batch 2025 semester plan** – Prerequisite text: 'MATH202, MATH204'. MATH204 exists in other batches or minors but is not scheduled for batch 2025.
- **COMP206 Microprocessors and Computer Architecture (batch 2026) requires COMP207, which is not in the batch 2026 semester plan** – Prerequisite text: 'COMP204, COMP207'. COMP207 exists in other batches or minors but is not scheduled for batch 2026.
- **COMP302 Internet of Things (batch 2026) requires COMP132, which is not in the batch 2026 semester plan** – Prerequisite text: 'COMP132, COMP201, COMP206, COMP208, COMP301'. COMP132 exists in other batches or minors but is not scheduled for batch 2026.
- **COMP302 Internet of Things (batch 2026, S6) requires COMP208, scheduled in S6 of the same plan** – The prerequisite is scheduled in the same or a later semester than the course itself, so it cannot be completed beforehand as planned.
- **MATH301 Optimization Techniques for Data Science (batch 2026) requires MATH201, which is not in the batch 2026 semester plan** – Prerequisite text: 'MATH201'. MATH201 exists in other batches or minors but is not scheduled for batch 2026.
- **DATA301 Machine Learning (batch 2026) requires DATA206, which does not exist anywhere in the curriculum data** – Prerequisite text: 'DATA206, MATH301'. No course with code DATA206 appears in any semester plan or minor list, so this prerequisite cannot be verified (possible typo in the source).
- **Psychology minor (batch 2022): PSYC303 requires MATH131, which does not exist anywhere in the data** – Prerequisite text: 'PSYC101, PSYC202, MATH131'.
- **Psychology minor (batch 2025): PSYC202 requires PSYC101, which is not offered to batch 2025** – Prerequisite text: 'PSYC101'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Psychology minor (batch 2025): PSYC241 requires PSYC101, which is not offered to batch 2025** – Prerequisite text: 'PSYC101'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Psychology minor (batch 2025): PSYC306 requires PSYC101, which is not offered to batch 2025** – Prerequisite text: 'PSYC101, PSYC201'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Psychology minor (batch 2026): PSYC202 requires PSYC101, which is not offered to batch 2026** – Prerequisite text: 'PSYC101'. It is neither in the batch 2026 semester plan nor in this minor's course list for that batch.
- **Psychology minor (batch 2026): PSYC241 requires PSYC101, which is not offered to batch 2026** – Prerequisite text: 'PSYC101'. It is neither in the batch 2026 semester plan nor in this minor's course list for that batch.
- **Psychology minor (batch 2026): PSYC306 requires PSYC101, which is not offered to batch 2026** – Prerequisite text: 'PSYC101, PSYC201'. It is neither in the batch 2026 semester plan nor in this minor's course list for that batch.
- **Economics minor (batch 2022): ECON413 requires ECON202, which does not exist anywhere in the data** – Prerequisite text: 'ECON201, ECON202/ ECON207'.
- **Economics minor (batch 2022): ECON325 requires ECON202, which does not exist anywhere in the data** – Prerequisite text: 'ECON201, ECON202/ ECON207'.
- **Economics minor (batch 2023): ECON301 requires ECON202, which does not exist anywhere in the data** – Prerequisite text: 'ECON201, ECON202'.
- **Economics minor (batch 2025): ECON316 requires ECON201, which is not offered to batch 2025** – Prerequisite text: 'ECON201'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Economics minor (batch 2025): ECON315 requires ECON201, which is not offered to batch 2025** – Prerequisite text: 'ECON201, ECON209'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Economics minor (batch 2025): ECON301 requires ECON201, which is not offered to batch 2025** – Prerequisite text: 'ECON201, ECON202'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Economics minor (batch 2025): ECON301 requires ECON202, which does not exist anywhere in the data** – Prerequisite text: 'ECON201, ECON202'.
- **Economics minor (batch 2026): ECON316 requires ECON201, which is not offered to batch 2026** – Prerequisite text: 'ECON201'. It is neither in the batch 2026 semester plan nor in this minor's course list for that batch.
- **Economics minor (batch 2026): ECON315 requires ECON201, which is not offered to batch 2026** – Prerequisite text: 'ECON201, ECON209'. It is neither in the batch 2026 semester plan nor in this minor's course list for that batch.
- **Economics minor (batch 2026): ECON301 requires ECON201, which is not offered to batch 2026** – Prerequisite text: 'ECON201, ECON202'. It is neither in the batch 2026 semester plan nor in this minor's course list for that batch.
- **Economics minor (batch 2026): ECON301 requires ECON202, which does not exist anywhere in the data** – Prerequisite text: 'ECON201, ECON202'.
- **Finance minor (batch 2022): FINA333 requires MGMT208, which is not offered to batch 2022** – Prerequisite text: 'MGMT208'. It is neither in the batch 2022 semester plan nor in this minor's course list for that batch.
- **Finance minor (batch 2022): MGMT209 requires FINA201, which does not exist anywhere in the data** – Prerequisite text: 'FINA201' (Introduction to Financial Accounting).
- **Finance minor (batch 2022): MGMT203 requires MKMT201, which does not exist anywhere in the data** – Prerequisite text: 'MKMT201/ MGMT207/ FINA201' (Marketing Management/ Corporate Finance/ Financial and Management Accounting).
- **Finance minor (batch 2022): MGMT203 requires FINA201, which does not exist anywhere in the data** – Prerequisite text: 'MKMT201/ MGMT207/ FINA201' (Marketing Management/ Corporate Finance/ Financial and Management Accounting).
- **Finance minor (batch 2025): MGMT210 requires FINA333, which is not offered to batch 2025** – Prerequisite text: 'FINA333'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Finance minor (batch 2025): MGMT323 requires MGMT207, which is not offered to batch 2025** – Prerequisite text: 'MGMT207'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Marketing minor (batch 2022): MGMT203 requires MKMT201, which does not exist anywhere in the data** – Prerequisite text: 'MKMT201/ MGMT207/ FINA201' (Marketing Management/ Corporate Finance/ Financial and Management Accounting).
- **Marketing minor (batch 2022): MGMT203 requires FINA201, which does not exist anywhere in the data** – Prerequisite text: 'MKMT201/ MGMT207/ FINA201' (Marketing Management/ Corporate Finance/ Financial and Management Accounting).
- **Marketing minor (batch 2025): MGMT302 requires MKTG201, which is not offered to batch 2025** – Prerequisite text: 'MKTG201'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Marketing minor (batch 2025): MGMT314 requires MKTG201, which is not offered to batch 2025** – Prerequisite text: 'MKTG201'. It is neither in the batch 2025 semester plan nor in this minor's course list for that batch.
- **Start-up minor (batch 2024): MGMT326 requires MKTG201, which is not offered to batch 2024** – Prerequisite text: 'MKTG201'. It is neither in the batch 2024 semester plan nor in this minor's course list for that batch.
- **Batch 2026 University Core (B1) credits disagree between sources** – semester-spread Fixed Min: 24; Struct sheet: 18; sum of listed course credits: 18. The course-level sum and the Struct sheet agree; the Fixed Min column appears not to have been updated.
- **Batch 2026 Foundation (B2) credits disagree between sources** – semester-spread Fixed Min: 24; Struct sheet: 26; sum of listed course credits: 26. The course-level sum and the Struct sheet agree; the Fixed Min column appears not to have been updated.
- **Batch 2026 Program Core (B3) credits disagree between sources** – semester-spread Fixed Min: 46; Struct sheet: 50; sum of listed course credits: 50. The course-level sum and the Struct sheet agree; the Fixed Min column appears not to have been updated.
- **Minimum attendance: 75% (Academic Regulations, SOP) vs 80% (Code of Conduct)** – Academic Regulations clause 7.2 (Student Handbook, printed p.21) and SOP section 2 (p.2) set the minimum attendance to appear for end-semester examinations at 75% of classes conducted in every course (relaxable to no less than 65% for documented medical exigencies or approved State/National/International events, clauses 7.3-7.4 / SOP section 2). The Code of Conduct clause 4.5 in the same Handbook (Section IV, printed p.45) says 'Students must comply with the attendance requirement of 80%'. No precedence rule between these sections is stated in the provided documents; the Academic Regulations (amended 29 July 2025) and the SOP (17 Aug 2026) agree on 75% for exam eligibility.
- **Late registration: 'not permitted' vs 'up to one week'** – SOP section 1 ('Late Registration', p.1) states 'No late registration shall be permitted' except for medical exigencies or competitions/events (maximum two calendar weeks for medical cases). The same SOP section ('Course Registration Deadline', p.1) says the maximum permissible period for late registration is one calendar week, and Handbook clause 2.7 (printed p.16) permits late registration for any other reason for up to one calendar week with a late fee. The documents do not reconcile the 'not permitted' wording with the one-week allowance.
