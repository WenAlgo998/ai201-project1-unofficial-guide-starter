"""
Milestone 3 — Document ingestion and chunking for the Unofficial Guide.

Implements the Chunking Strategy from planning.md:
  - One chunk per student review (the natural atomic unit of this corpus).
  - Each chunk is prefixed with an attribution header "Professor <name> (<course>):"
    so the professor name and course travel with the review (no overlap needed).
  - Course codes are normalized (CSC 21200 / CSCI19100 -> CSC 212 / CSC 191).
  - Quality / difficulty / date / grade are kept as chunk metadata.

Run directly to load the corpus, build chunks, and inspect the output:
    python ingest.py
"""

import os
import re
import random
from dataclasses import dataclass, field

DOCUMENTS_DIR = "documents"


@dataclass
class Document:
    """One raw professor file after loading + light cleaning."""
    professor: str
    source_file: str
    source_url: str | None
    overall_rating: float | None
    reviews_section: str  # the text under "## Student reviews"


@dataclass
class Chunk:
    """One review, ready to embed."""
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


# --- 1. Document ingestion -------------------------------------------------

def _clean(text: str) -> str:
    """Light cleaning. The corpus is hand-curated markdown (no HTML/nav/ads),
    so this only normalizes whitespace and decodes the few HTML entities that
    can slip in from copied web text."""
    entities = {"&amp;": "&", "&nbsp;": " ", "&#39;": "'", "&quot;": '"',
                "&lt;": "<", "&gt;": ">"}
    for ent, char in entities.items():
        text = text.replace(ent, char)
    # Drop any stray HTML tags, just in case cleaning of a future source missed them.
    text = re.sub(r"<[^>]+>", "", text)
    return text


def load_documents(documents_dir: str = DOCUMENTS_DIR) -> list[Document]:
    """Read every .md file in documents/, clean it, and pull out the header
    facts plus the reviews section."""
    docs: list[Document] = []
    for filename in sorted(os.listdir(documents_dir)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(documents_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            raw = _clean(f.read())

        # Professor name from the H1: "# Professor <Name> — Computer Science, CCNY"
        h1 = re.search(r"^#\s+Professor\s+(.+?)\s+[—-]", raw, re.MULTILINE)
        professor = h1.group(1).strip() if h1 else filename.replace(".md", "")

        url_match = re.search(r"https?://\S+", raw)
        source_url = url_match.group(0) if url_match else None

        rating_match = re.search(r"Overall rating:\s*([\d.]+)", raw)
        overall_rating = float(rating_match.group(1)) if rating_match else None

        # Everything after the "## Student reviews" heading is the review body.
        split = re.split(r"^##\s+Student reviews\s*$", raw, flags=re.MULTILINE)
        reviews_section = split[1] if len(split) > 1 else ""

        docs.append(Document(
            professor=professor,
            source_file=filename,
            source_url=source_url,
            overall_rating=overall_rating,
            reviews_section=reviews_section,
        ))
    return docs


# --- 2. Chunking -----------------------------------------------------------

# Course code -> name, sourced from this project's own planning.md Documents
# table and the document headers (not outside knowledge). Codes we never named
# definitively are left as bare codes. Including the name in each chunk lets a
# query like "Data Structures" match a review that only contains "CSC 212".
COURSE_NAMES = {
    "CSC 103": "Introduction to Computing",
    "CSC 210": "Computer Organization",
    "CSC 212": "Data Structures",
    "CSC 301": "Discrete Mathematics",
    "CSC 322": "Software Engineering",
    "CSC 335": "Algorithms",
    "CSC 342": "Operating Systems",
    "CSC 343": "Operating Systems",
    "CSC 447": "Machine Learning",
    "CSC 448": "Artificial Intelligence",
    "CSC 470": "Computer Graphics",
    "CSC 472": "Computer Graphics",
    "CSC 473": "Computer Graphics",
}


def course_label(course: str | None) -> str | None:
    """'CSC 212' -> 'CSC 212 Data Structures' when the name is known, else the code."""
    if not course:
        return None
    name = COURSE_NAMES.get(course)
    return f"{course} {name}" if name else course


def normalize_course(raw: str | None) -> str | None:
    """CCNY writes the same course many ways: 'CSC 21200', 'CSC212', 'CSCI19100',
    'CS322'. Collapse them all to 'CSC <first three digits>' so a course-specific
    query matches regardless of how the student typed it."""
    if not raw:
        return None
    digits = re.search(r"\d+", raw)
    if not digits:
        return None
    return f"CSC {digits.group(0)[:3]}"


# Matches a review header line, e.g.:
#   **CSC 322 — Jun 8, 2026 (Quality 2.0, Difficulty 4.0, Grade C)**
#   **Nov 10, 2022 (Quality 2.0, Difficulty 5.0)**   (no course)
#   **CSC 472 — May 24, 2024**                        (no extras)
_HEADER = re.compile(r"^\*\*(.+?)\*\*\s*$", re.MULTILINE)


def _parse_header(inner: str) -> dict:
    """Pull course / date / quality / difficulty / grade out of the bold header."""
    extras = ""
    paren = re.search(r"\(([^)]*)\)\s*$", inner)
    if paren:
        extras = paren.group(1)
        inner = inner[:paren.start()].strip()

    # What's left is "COURSE — DATE" or just "DATE" (em-dash or hyphen separator).
    if re.search(r"\s[—-]\s", inner):
        course_raw, date = re.split(r"\s[—-]\s", inner, maxsplit=1)
    else:
        course_raw, date = None, inner

    def _num(label):
        m = re.search(label + r"\s+([\d.]+)", extras)
        return float(m.group(1)) if m else None

    grade = re.search(r"Grade\s+([A-Za-z+]+)", extras)

    return {
        "course": normalize_course(course_raw),
        "date": date.strip() if date else None,
        "quality": _num("Quality"),
        "difficulty": _num("Difficulty"),
        "grade": grade.group(1) if grade else None,
    }


def chunk_text(doc: Document) -> list[Chunk]:
    """Split one document into one chunk per review, prepending the attribution
    header so each chunk is self-contained."""
    chunks: list[Chunk] = []

    # Find every review header and the text that follows it (up to the next header).
    headers = list(_HEADER.finditer(doc.reviews_section))
    for i, h in enumerate(headers):
        meta = _parse_header(h.group(1))
        body_start = h.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(doc.reviews_section)
        body = doc.reviews_section[body_start:body_end].strip()

        if not body:  # skip headers with no review text
            continue

        # Attribution prefix: "Professor X (CSC 212 Data Structures): ..."
        # (course name included when known), or "Professor X: ..." with no course.
        label = course_label(meta["course"])
        prefix = f"Professor {doc.professor} ({label}): " if label else f"Professor {doc.professor}: "
        text = prefix + body

        chunks.append(Chunk(
            id=f"{doc.source_file.replace('.md', '')}-{len(chunks)}",
            text=text,
            metadata={
                "professor": doc.professor,
                "course": meta["course"],
                "course_name": COURSE_NAMES.get(meta["course"]),
                "date": meta["date"],
                "quality": meta["quality"],
                "difficulty": meta["difficulty"],
                "grade": meta["grade"],
                "overall_rating": doc.overall_rating,
                "source_file": doc.source_file,
                "source_url": doc.source_url,
            },
        ))
    return chunks


def build_chunks(documents_dir: str = DOCUMENTS_DIR) -> list[Chunk]:
    """Full pipeline: load every document and flatten into one list of chunks."""
    chunks: list[Chunk] = []
    for doc in load_documents(documents_dir):
        chunks.extend(chunk_text(doc))
    return chunks


# --- 3. Inspection (run this before trusting the chunks) -------------------

if __name__ == "__main__":
    docs = load_documents()
    chunks = build_chunks()

    print(f"Loaded {len(docs)} documents -> {len(chunks)} chunks "
          f"(~{len(chunks) / len(docs):.1f} per document)\n")

    lengths = [len(c.text) for c in chunks]
    print(f"Chunk length (chars): min={min(lengths)}, "
          f"max={max(lengths)}, avg={sum(lengths) // len(lengths)}")
    empties = [c for c in chunks if not c.text.strip()]
    print(f"Empty chunks: {len(empties)}")
    no_course = [c for c in chunks if c.metadata["course"] is None]
    print(f"Chunks with no course code: {len(no_course)}\n")

    print("=" * 70)
    print("5 RANDOM CHUNKS FOR INSPECTION")
    print("=" * 70)
    random.seed(1)
    for c in random.sample(chunks, 5):
        print(f"\n[{c.id}]  course={c.metadata['course']}  "
              f"quality={c.metadata['quality']}  difficulty={c.metadata['difficulty']}")
        print(c.text)
