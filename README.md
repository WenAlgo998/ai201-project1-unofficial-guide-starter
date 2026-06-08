# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Setup & running

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your free Groq API key from https://console.groq.com
python app.py               # open http://localhost:7860
```

Pipeline scripts (each runnable on its own for inspection):
- `ingest.py` — load + clean documents, chunk into reviews (`python ingest.py` prints chunk stats + samples)
- `retrieval.py` — embed chunks into ChromaDB and test retrieval (`python retrieval.py` rebuilds the index)
- `query.py` — grounded generation via Groq (`python query.py` runs the eval questions)
- `app.py` — Gradio web interface

> Note: `torch` (pulled in by `sentence-transformers`) is incompatible with NumPy 2, so `requirements.txt` pins `numpy<2`.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

**Student reviews of Computer Science professors at The City College of New York (CCNY).**

The system makes searchable what CCNY CS students say about specific professors — teaching style, grading fairness, workload, exam structure, and which professor to take for a given course. CCNY's official catalog and CUNYfirst schedule list only course titles and credits; they say nothing about whether a professor reads off slides, curves exams, or assigns a heavy group project. That experiential knowledge is scattered across Rate My Professors one professor at a time and can't be queried as a whole — you can't ask "who should I take for Data Structures?" and get a synthesized answer. This guide collects those reviews into a single searchable corpus.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

All sources are individual professor pages on Rate My Professors (school 224 = City College of New York, Computer Science). Each page's reviews were extracted into a markdown file in `documents/`. The set deliberately spans the intro sequence through algorithms/theory, OS, AI, and ML, and mixes beloved and disliked professors.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Michael Grossberg (CSC 322 / 473) | Rate My Professors | [854471](https://www.ratemyprofessors.com/professor/854471) · `documents/grossberg-michael.md` |
| 2 | George Wolberg (CSC 212 / 470-472) | Rate My Professors | [175168](https://www.ratemyprofessors.com/professor/175168) · `documents/wolberg-george.md` |
| 3 | Irina Gladkova (CSC 301 / 217) | Rate My Professors | [422536](https://www.ratemyprofessors.com/professor/422536) · `documents/gladkova-irina.md` |
| 4 | Jie Wei (CSC 322) | Rate My Professors | [354797](https://www.ratemyprofessors.com/professor/354797) · `documents/wei-jie.md` |
| 5 | Izidor Gertner (CSC 210 / 342-343) | Rate My Professors | [489006](https://www.ratemyprofessors.com/professor/489006) · `documents/gertner-izidor.md` |
| 6 | Zhigang Zhu (CSC 212 + grad) | Rate My Professors | [824284](https://www.ratemyprofessors.com/professor/824284) · `documents/zhu-zhigang.md` |
| 7 | Erik Grimmelmann (CSC 30100 / 447) | Rate My Professors | [2380866](https://www.ratemyprofessors.com/professor/2380866) · `documents/grimmelmann-erik.md` |
| 8 | Douglas Troeger (CSC 335) | Rate My Professors | [432142](https://www.ratemyprofessors.com/professor/432142) · `documents/troeger-douglas.md` |
| 9 | Akira Kawaguchi (CSC 103) | Rate My Professors | [624278](https://www.ratemyprofessors.com/professor/624278) · `documents/kawaguchi-akira.md` |
| 10 | William Skeith (CSC 103) | Rate My Professors | [1316015](https://www.ratemyprofessors.com/professor/1316015) · `documents/skeith-william.md` |
| 11 | Stephen Lucci (CSC 304 / 448) | Rate My Professors | [534845](https://www.ratemyprofessors.com/professor/534845) · `documents/lucci-stephen.md` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** One chunk per student review — the natural atomic unit of the corpus. In practice each chunk is ~300–500 characters (measured range 60–385, average 206). I split on the review-header boundary (`**Course — Date (Quality/Difficulty)**`) inside each document rather than using a fixed character window.

**Overlap:** None. Reviews are independent opinions, so there is no fact spanning a boundary to recover with overlap. Instead, every chunk is prefixed with an attribution header — `Professor George Wolberg (CSC 212 Data Structures): …` — so the professor name and course travel with the review. This solves the real risk (losing attribution) that overlap would not.

**Preprocessing:** decode HTML entities and strip any stray tags (`_clean()` in `ingest.py`); parse the professor name from the H1 and the per-review course/date/quality/difficulty/grade from each bold header; normalize course codes so `CSC 21200`, `CSC212`, `CSCI19100` all collapse to `CSC <first three digits>`; and map known codes to course names (`CSC 212` → `Data Structures`) so a query phrased by course name can match a review that only contains the code.

**Why these choices fit your documents:** The documents are short, opinion-based reviews (1–3 sentences), not long guides. A fixed-character window would cut a review mid-sentence and merge two students' opposing opinions into one chunk — destructive for opinion text where polarity is the signal. Whole-file chunking would be the opposite failure, averaging five contradictory reviews into one blob so retrieval couldn't surface a specific opinion. One-review-per-chunk keeps each retrievable unit a single complete, self-contained thought.

**Final chunk count:** 55 chunks across 11 documents (≈5 reviews per professor).

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, with vectors stored in ChromaDB using cosine distance. It runs locally with no API key or rate limits, produces 384-dim embeddings, handles 256 tokens of context (far more than any single review needs), and is specifically strong at sentence-level semantic similarity — the right fit for short opinion text. Semantic search matters here because students phrase queries differently from reviews ("easy A" vs. a review's "no exams, easy HW"), and embeddings match on meaning rather than shared words.

**Production tradeoff reflection:** If cost weren't a constraint and this served real students, I'd weigh a hosted model such as OpenAI `text-embedding-3-large` or Voyage/Cohere embeddings. The gains I'd care about: (1) **accuracy on domain-specific text** — slang, professor nicknames ("Wes" for Skeith), and course codes are where MiniLM is weakest, and a larger model encodes those nuances better; and (2) **longer context**, irrelevant for short reviews but it would matter if I added full syllabus PDFs. The costs against those gains are **latency and dependency** — an API round-trip per query plus a hard dependency on an external service and key, versus MiniLM running locally in milliseconds. **Multilingual** support isn't a factor for an English-only corpus. For this project the local model wins; at production scale the accuracy gain on noisy domain text would likely justify a hosted model — and, as my failure case shows, no embedding model fully solves the negation/polarity problem, so I'd pair it with metadata filtering or a reranker rather than relying on embeddings alone.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The model (`llama-3.3-70b-versatile` via Groq, called at `temperature=0`) is given this system prompt, which *forbids* outside knowledge and *mandates* a fixed refusal rather than merely suggesting it:

> You are the Unofficial Guide to Computer Science professors at The City College of New York (CCNY). You answer student questions using ONLY the student reviews provided in the CONTEXT.
> Rules:
> - Use only facts stated in the CONTEXT. Never use outside knowledge about these professors, courses, or CCNY, and never guess.
> - If the CONTEXT does not contain enough information to answer the question, reply with exactly this sentence and nothing else: "I don't have enough information on that."
> - Refer to professors by name. Do not invent professors, courses, ratings, or quotes.
> - Do not refer to the reviews by their bracket numbers; just state what students said.
> - When reviews disagree about a professor, present both sides honestly.
> - Be concise: 2–5 sentences.

The retrieved chunks are passed as a numbered `CONTEXT` block, and the question is appended with "Answer using only the CONTEXT above." Because each chunk already carries its `Professor (Course)` prefix, every fact the model sees is pre-attributed.

**How source attribution is surfaced in the response:** Attribution is built **programmatically in code**, not left to the LLM. After generation, `_build_sources()` lists the professors from the retrieved set whose names actually appear in the generated answer, each with its Rate My Professors URL, and the Gradio UI shows them in a separate "Retrieved from" panel. If the model returns the fixed refusal sentence, the source list is suppressed (nothing was used). This guarantees citations are real retrieved documents and can't be hallucinated — and it only credits the reviews the answer genuinely drew from.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professor should I take for Data Structures (CSC 212) and why? | Wolberg — highly rated, review sessions mirror exams, caring/clear; vs. Zhu, a tough grader with pop quizzes. | Recommends Wolberg ("very nice", "explains the course well"); notes Zhu is mixed — tough grader / lots of homework but accessible. Cites Wolberg + Zhu. | Relevant (top 3 all CSC 212, d=0.32–0.42) | **Accurate** |
| 2 | How hard is Douglas Troeger's CSC 335, and how should I prepare? | Extremely hard ("hardest course in the CS curriculum"); tough grader, test-heavy; understand material before each midterm. | "Hardest course in the CCNY CS curriculum"; test-heavy, tough grader, graded on few questions, prepare before each midterm. Cites Troeger. | Relevant (all Troeger CSC 335) | **Accurate** |
| 3 | What do students say about cheating in Jie Wei's CSC 322 class? | ~90% of the class cheats on exams; grading feels unfair as a result. | "Everyone in this class cheats" and "90% of the class will cheat on exams." Cites Wei. | Relevant (top hit d=0.22) | **Accurate** |
| 4 | Who is a good professor to take for an easy A with a light workload? | Grimmelmann (4.8★, no exams, easy HW) or Lucci (easy, funny). | Names Lucci ("very easy and doable") and Kawaguchi, but **misses Grimmelmann** and muddies the answer with heavy-workload professors (Grossberg, Kawaguchi). | Partially relevant (top hit is Grossberg "the workload is a lot") | **Partially accurate** |
| 5 | Is William Skeith's intro CS class (CSC 103) okay for a complete beginner? | Risky for a true beginner — taught in C++; learn C++ basics first; but he curves exams and rewards genuine effort. | Challenging without prior C++ experience; exams hard; background knowledge helps. Cites Skeith. | Relevant (Skeith CSC 103 retrieved alongside Kawaguchi CSC 103) | **Accurate** |

**Summary:** 4 of 5 accurate, 1 partially accurate. Out-of-corpus questions (e.g. "Who teaches the quantum computing course at CCNY?") correctly return *"I don't have enough information on that."*

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "Who is a good professor to take for an easy A with a light workload?" (eval Q4). The failure is even starker for the paraphrase "Which professor has the lightest workload?", which the system refuses outright.

**What the system returned:** For Q4 it named Lucci (correct) but **missed Grimmelmann entirely** — the strongest answer in the corpus (4.8★, difficulty 2.1, reviews literally say "no exams" and "HW was easy"). The single most relevant chunk was never retrieved. Worse, the *top* retrieved chunk was Grossberg's review saying **"the workload is a lot"** (distance 0.45) — the exact opposite of what was asked — and the answer ended up listing heavy-workload professors. For "lightest workload," the top hit was again Grossberg's "VERY UNORGANIZED. The workload is a lot," so the model correctly refused rather than recommend him.

**Root cause (tied to a specific pipeline stage):** This is an **embedding-stage** failure, specifically the negation/polarity blindness of `all-MiniLM-L6-v2`. Cosine similarity keys on the shared concept "workload," and the model does not encode the difference between "light workload" and "the workload is a lot" — both embed close to the query. Grimmelmann's chunk, which expresses "easy / no exams" *without using the word "workload,"* lands farther away in vector space than Grossberg's opposite-polarity chunk that shares the surface term. So retrieval surfaces a semantically-adjacent-but-opposite chunk and buries the correct one below the top-k cutoff. Grounding then works as designed — it refuses or hedges because the truly relevant review wasn't in the context — but it can't fix what retrieval never delivered.

**What you would change to fix it:** (1) **Metadata filtering** — I already store `difficulty` and `quality` per chunk; for workload/difficulty queries I'd pre-filter to low-difficulty chunks (e.g. difficulty ≤ 2.5) before the semantic search, which would float Grimmelmann and Lucci to the top. (2) **A cross-encoder reranker** over a larger candidate set (e.g. retrieve k=20, rerank to 6) would catch polarity that the bi-encoder misses. (3) **A sentiment/polarity tag** computed at ingestion and stored as metadata, so "easy/positive" queries can match on it directly. I deliberately kept pure semantic retrieval for this submission to keep the system simple and the failure honest, rather than special-casing the eval questions.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the Chunking Strategy *before* coding forced the per-review decision early, and that decision rippled cleanly through every later stage. Because the spec said "one chunk per review with an attribution prefix," the ingestion code had an obvious target (split on review headers, prepend `Professor (Course):`), the metadata schema was decided in advance (professor, course, date, quality, difficulty), and grounding in Milestone 5 came almost for free — every chunk the LLM saw was already pre-attributed, so source citation became a code step rather than something I had to coax the model into. Having the Anticipated Challenges section also meant the attribution and course-code-ambiguity risks were already named, so I built `normalize_course()` defensively instead of discovering the problem during debugging.

**One way your implementation diverged from the spec, and why:** The spec said the attribution prefix would be `Professor <name> (<course code>):`. During Milestone 5 testing, eval Q1 ("which professor for **Data Structures**?") was refused, because no review *text* contains the words "Data Structures" — only the code `CSC 212` — and the grounding rules (correctly) wouldn't let the model assume the code and the name are the same thing. I diverged by adding a course-code→name map (sourced from my own Documents table, not outside knowledge) so the prefix became `Professor George Wolberg (CSC 212 Data Structures):`. This fixed both retrieval (the query now matches the chunk semantically) and generation, and I updated planning.md to record the change. It's the only divergence from the original spec.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Chunking implementation**

- *What I gave the AI:* My Chunking Strategy section from planning.md plus two sample files from `documents/` so it could see the real review-header format, and asked it to implement `load_documents()` and `chunk_text()` to my spec (one chunk per review, attribution prefix, course-code normalization, metadata).
- *What it produced:* A working parser that split on the `**…**` review headers, prepended `Professor <name> (<course>):`, and attached metadata — 55 chunks, 0 empty, verified by printing 5 random chunks.
- *What I changed or overrode:* I directed the chunking decision myself (one-chunk-per-review over the AI's more generic fixed-character default), and after testing I overrode the attribution format to also include the course *name*, not just the code — because pure-code attribution caused the Data Structures query to fail. I also kept the `normalize_course()` rule (first three digits) rather than a longer mapping, since that one rule covered every code variant in the corpus.

**Instance 2 — Diagnosing the retrieval failure case**

- *What I gave the AI:* The retrieval output for "easy A / light workload," where the top result was Grossberg's "the workload is a lot," and asked it to explain *why* a clearly-relevant query returned an opposite-polarity chunk.
- *What it produced:* An explanation that bi-encoder embeddings like all-MiniLM-L6-v2 are weak at negation/polarity — they match the shared concept "workload" regardless of sentiment — plus fix options (metadata filtering on difficulty, a cross-encoder reranker, sentiment tags).
- *What I changed or overrode:* I chose **not** to implement any of the fixes for this submission. Adding a course/difficulty filter just for the eval questions would have masked a genuine limitation; I decided the honest failure case was more valuable than a system that looked perfect, and documented it in the Failure Case Analysis instead.
