"""PDF adapter: pymupdf4llm page markdown -> cleaned text_section SourceUnits (one per page).

pymupdf4llm is used (not pypdf) because the Handbook has cross-contaminated text layers on
PDF pp.36/65 that pypdf merges into the wrong pages; PyMuPDF reads the visible text correctly.

Known source defects are fixed by explicit, reviewable PATCHES keyed by (file, pdf page).
Every patch was checked against the page image / surrounding text.
"""
import re
from pathlib import Path

import pymupdf4llm

from . import unit

TABLE_1 = """**Table 1. Evaluation System: Components and Weightage**

| Type of Course Structure | Evaluation Components | Weightage |
|---|---|---|
| Lecture-based Course — L in the L-T-P structure predominates (Examples: 3-0-0; 2-1-0; 3-0-2; etc.) | Continuous Assessments | 60% (minimum) to 70% (maximum) |
| | End Term Examination / Comprehensive | 30% (minimum) to 40% (maximum) |
| Practice-based Course — P in the L-T-P structure predominates (Examples: 0-0-4; 1-0-4; 1-0-2; etc.) | Continuous Assessments | 70% (minimum) to 100% (maximum) |
| | End Term Examination / Jury / Project / Viva Voce | 30% (maximum) |
| Practice/Skill based Courses like Industry Internship, Capstone project, Research Dissertation, Integrative Studio, Interdisciplinary Project and such similar Courses, and Non-Taught Credit Courses like Seminar, Summer / Short Internship, Social Engagement / Field Projects and such similar Courses, where the pedagogy does not lend itself to a typical L-T-P structure (Refer Clause 3.2) | Guidelines for the components of evaluation for the various types of courses, with recommended weightages / criteria for assessing the components, shall be specified in the concerned Program Regulations and Course Plans, as applicable. | |

"""

# Transcribed from the embedded image on PDF p.32 (the table has no text layer).
TABLE_2 = """

**Table 2. Letter Grades with Grade Points and Brief Qualitative Description**

| Letter Grade | Grade Point | Qualitative Description |
|---|---|---|
| O | 10 | Outstanding |
| A+ | 9 | Excellent |
| A | 8 | Very Good |
| B+ | 7 | Good |
| B | 6 | Above Average |
| C | 5 | Average |
| D | 4 | Pass |
| F | 0 | Fail |
| FA | 0 | Fail - Shortage of Attendance |
| S | – | Satisfactory |
| U | – | Unsatisfactory |
| I | – | Incomplete |
"""

TABLE_3 = """| Progression Stage | Minimum CGPA Requirement |
|---|---|
| Progression to Year 2 of the Program | Minimum CGPA of 4.00 (Eligibility Criteria to Register for Semester 3) |
| Progression to Year 3 and higher years of the Program | Minimum CGPA of 5.00 |

"""

F = "�"  # glyphs PyMuPDF could not map (bullets, math italics)

PATCHES = {
    ("4. Student Handbook Aug 2026.pdf", 23): [
        (r"^#+ Academic Calendar", "#### 1. Academic Calendar"),
    ],
    ("4. Student Handbook Aug 2026.pdf", 31): [
        (r"\|_Table 1\..*?\n\n(?=- 8\.8)", TABLE_1),
    ],
    ("4. Student Handbook Aug 2026.pdf", 32): [
        (r"(summarized in Table 2:)", r"\1" + TABLE_2),
    ],
    ("4. Student Handbook Aug 2026.pdf", 37): [  # formulas are rendered as images/glyphs
        (r"(computed as follows:)\s*where:", r"\1\n\nSGPA = Σₖ (Cₖ × Gₖ) / Σₖ Cₖ, summed over k = 1 … n\n\nwhere:", 1),
        (r"(CGPA is computed as follows:)\s*where:", r"\1\n\nCGPA = Σᵢ (Cᵢ × Gᵢ) / Σᵢ Cᵢ, summed over i = 1 … n\n\nwhere:"),
        (r"- is the number of Courses", "- n is the number of Courses"),
        (rf"(?:- )?{F}{F}\s+is the Credits assigned to Course {F} and {F}{F} is the Grade Point received by the student for the Course {F}\.",
         "- Cₖ is the Credits assigned to Course k and Gₖ is the Grade Point received by the student for the Course k.", 1),
        (rf"(?:- )?{F}{F}\s+is the Credits assigned to Course {F} and {F}{F} is the Grade Point received by the student for the Course {F}\.",
         "- Cᵢ is the Credits assigned to Course i and Gᵢ is the Grade Point received by the student for the Course i.", 1),
    ],
    ("4. Student Handbook Aug 2026.pdf", 42): [
        (r"\|\*\*Progression Stage\*\*.*?\n\n(?=- 12\.2)", TABLE_3),
    ],
    ("4. Student Handbook Aug 2026.pdf", 79): [
        (r"\|\|Possession or accessibility of materials such as paper, notebooks,\|\n\|---\|---\|\n\|Case 1\|",
         "|Case|Description|\n|---|---|\n|Case 1|Possession or accessibility of materials such as paper, notebooks, "),
        (r"intentionally tears of\|", "intentionally tears off the script or any part thereof inside or outside the examination hall.|"),
    ],
    ("4. Student Handbook Aug 2026.pdf", 80): [
        (r"\|\|the script or any part thereof inside or outside the examination hall\.\|\n\|---\|---\|",
         "|Case|Description|\n|---|---|"),
    ],
    ("4. Student Handbook Aug 2026.pdf", 91): [
        (rf"^#+ \*\*{F}+\*\*", "#### Important Contact Numbers"),
        (r"\|5\|Associate Director – Residential Life &\|9845143102\|\n\|\|Co-ordinatingOfficer\|\|",
         "|5|Associate Director – Residential Life & Co-ordinating Officer|9845143102|"),
    ],
}


def printed_page(file, pdf_page):
    """Handbook body pages carry printed numbers = PDF page - 8 (front matter unnumbered)."""
    if file.startswith("4. Student Handbook"):
        return pdf_page - 8 if pdf_page >= 9 else None
    return pdf_page


def clean(md, file, pdf_page):
    s = re.sub(r"</?(mark|u)>", "", md)
    s = re.sub(r"<sup>\**\s*([^<*]+?)\s*\**</sup>\s*", r"\1", s)
    for pat, rep, *count in PATCHES.get((file, pdf_page), []):
        s, n = re.subn(pat, rep, s, count=count[0] if count else 0, flags=re.S | re.M)
        if not n:
            raise ValueError(f"PDF patch did not apply: {file} p.{pdf_page}: {pat[:60]}")
    s = re.sub(F + r"+\s*", "", s)
    s = re.sub(r"^#{5,6} ", "#### ", s, flags=re.M)
    s = re.sub(r"^#{1,2} ", "### ", s, flags=re.M)  # "##" is reserved for document sections
    s = re.sub(r"(?m)^Page \*\*\d+\*\* of \*\*\d+\*\*\s*$", "", s)  # SOP footer
    s = re.sub(r"\n\s*\d{1,3}\s*$", "", s.rstrip())  # trailing printed page number
    s = re.sub(r"[ \t]+\n", "\n", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def extract(path):
    path = Path(path)
    out = []
    for page in pymupdf4llm.to_markdown(str(path), page_chunks=True, show_progress=False):
        n = page["metadata"]["page_number"]
        text = clean(page["text"], path.name, n)
        out.append(unit("text_section", path, f"pdf={n}", {"text": text, "pdf_page": n,
                                                           "printed_page": printed_page(path.name, n)}, page=n))
    return out
