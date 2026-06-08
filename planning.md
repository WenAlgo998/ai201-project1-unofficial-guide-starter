# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

**Student reviews of Computer Science professors at The City College of New York (CCNY).**

This guide makes searchable what CCNY CS students actually say about specific professors — teaching style, grading fairness, workload, exam structure, and which courses to take with whom. The official CCNY course catalog and CUNYfirst schedule list only course titles and credits; they reveal nothing about whether a professor reads off slides, curves exams, assigns a heavy group project, or roasts students for asking questions. That experiential knowledge lives scattered across Rate My Professors pages, one professor at a time, and is impossible to query as a whole — you can't ask "which professor should I take for Data Structures?" and get a synthesized answer. This system collects those reviews into one searchable corpus.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

All sources are individual professor pages on Rate My Professors (school 224 = City College of New York), Computer Science department. Each page's reviews were extracted into one markdown file under `documents/`. Together they span the intro sequence, data structures, software engineering, algorithms/theory, discrete math, OS, AI, and ML — and a deliberate mix of beloved and disliked professors so retrieval has contrasting opinions to surface.

| # | Source (professor) | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Michael Grossberg | CSC 322 Software Engineering / CSC 473 — polarizing (3.6★) | [RMP](https://www.ratemyprofessors.com/professor/854471) → `documents/grossberg-michael.md` |
| 2 | George Wolberg | CSC 212 Data Structures / CSC 470-472 — highly rated (4.5★) | [RMP](https://www.ratemyprofessors.com/professor/175168) → `documents/wolberg-george.md` |
| 3 | Irina Gladkova | CSC 301 Discrete Math / CSC 217 — divisive (2.4★) | [RMP](https://www.ratemyprofessors.com/professor/422536) → `documents/gladkova-irina.md` |
| 4 | Jie Wei | CSC 322 Software Engineering — cheating/leetcode themes (3.4★) | [RMP](https://www.ratemyprofessors.com/professor/354797) → `documents/wei-jie.md` |
| 5 | Izidor Gertner | CSC 210 / CSC 342-343 Operating Systems — chaotic (2.6★) | [RMP](https://www.ratemyprofessors.com/professor/489006) → `documents/gertner-izidor.md` |
| 6 | Zhigang Zhu | CSC 212 Data Structures + grad — tough grader (3.7★) | [RMP](https://www.ratemyprofessors.com/professor/824284) → `documents/zhu-zhigang.md` |
| 7 | Erik Grimmelmann | CSC 30100 / CSC 447 Machine Learning / Senior Design — beloved (4.8★) | [RMP](https://www.ratemyprofessors.com/professor/2380866) → `documents/grimmelmann-erik.md` |
| 8 | Douglas Troeger | CSC 335 Algorithms/Theory — "hardest course in the CS curriculum" (1.9★) | [RMP](https://www.ratemyprofessors.com/professor/432142) → `documents/troeger-douglas.md` |
| 9 | Akira Kawaguchi | CSC 103 Intro to CS (dept. chair) — fast-paced (2.3★) | [RMP](https://www.ratemyprofessors.com/professor/624278) → `documents/kawaguchi-akira.md` |
| 10 | William Skeith | CSC 103 Intro to CS in C++ — fair curves, anti-AI (3.8★) | [RMP](https://www.ratemyprofessors.com/professor/1316015) → `documents/skeith-william.md` |
| 11 | Stephen Lucci | CSC 304 / CSC 448 Artificial Intelligence — easy & funny (3.9★) | [RMP](https://www.ratemyprofessors.com/professor/534845) → `documents/lucci-stephen.md` |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which professor should I take for Data Structures (CSC 212) and why? | Wolberg — highly rated (4.5★), review sessions mirror the exams, caring and clear; vs. Zhu who is a tough grader with pop quizzes. |
| 2 | How hard is Douglas Troeger's CSC 335, and how should I prepare? | Extremely hard — students call it "the hardest course in the CS curriculum" (1.9★, difficulty 4.7). Be fully prepared before each midterm; tough grader, test-heavy, write comments and avoid syntax errors on exams. |
| 3 | What do students say about cheating in Jie Wei's CSC 322 software engineering class? | Multiple reviews say ~90% of the class cheats on exams and the grading scheme feels unfair because of it; coding questions resemble LeetCode easy/medium. |
| 4 | Who is a good professor to take for an easy A with a light workload? | Erik Grimmelmann (4.8★, difficulty 2.1, no exams, easy HW/projects) or Stephen Lucci (3.9★, difficulty 2.4, funny, easy grader). |
| 5 | Is William Skeith's intro CS class (CSC 103) okay for a complete beginner? | Risky for a true beginner — taught in C++; reviews advise learning C++ basics (loops, functions, recursion, linked lists) beforehand. But he curves exams well and is fair to students who genuinely try (and strict about AI use). |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Contradictory reviews for the same professor.** Almost every professor has both 5★ and 1★ reviews (e.g., Gladkova at 2.4★ has glowing and scathing comments side by side). Retrieval may surface only one polarity depending on the query wording, producing a one-sided answer. The system needs to present the spread of opinion, not the first chunk it finds.

2. **Course-number ambiguity and noise.** The same course appears as "CSC 212", "CSC 21200", and "CSC212" across reviews, and some comments are pure noise ("British cigarette", slang, typos). A query about a specific course code may miss reviews that wrote it differently, and noisy chunks can crowd out substantive ones. Preprocessing/normalization and chunk sizing (M2) will need to account for this.

3. **Attribution across professors with overlapping courses.** CSC 322 is taught by both Grossberg and Wei; CSC 103 by both Kawaguchi and Skeith. If chunks lose the professor name, a "who teaches CSC 322?" answer could blend the two. Each chunk must carry the professor name as metadata.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
