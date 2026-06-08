# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

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

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

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

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
