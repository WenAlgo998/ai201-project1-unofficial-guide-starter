"""
Milestone 5 — Grounded generation for the Unofficial Guide.

ask(question) retrieves the top-k professor-review chunks, builds a strictly
grounded prompt, calls Groq (llama-3.3-70b-versatile), and returns the answer
plus a programmatically-built source list (NOT left to the LLM to invent).

Grounding is enforced two ways:
  1. A system prompt that forbids outside knowledge and mandates a fixed refusal
     sentence when the context is insufficient.
  2. Sources are attached in code from the retrieved chunks' metadata, so
     attribution is guaranteed and can't be hallucinated.
"""

import os
from groq import Groq
from dotenv import load_dotenv

from retrieval import retrieve, DEFAULT_K

load_dotenv()
_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

REFUSAL = "I don't have enough information on that."

SYSTEM_PROMPT = f"""You are the Unofficial Guide to Computer Science professors at \
The City College of New York (CCNY). You answer student questions using ONLY the \
student reviews provided in the CONTEXT.

Rules:
- Use only facts stated in the CONTEXT. Never use outside knowledge about these \
professors, courses, or CCNY, and never guess.
- If the CONTEXT does not contain enough information to answer the question, reply \
with exactly this sentence and nothing else: "{REFUSAL}"
- Refer to professors by name. Do not invent professors, courses, ratings, or quotes.
- Do not refer to the reviews by their bracket numbers (e.g. "review [3]"); just state what students said.
- When reviews disagree about a professor, present both sides honestly.
- Be concise: 2-5 sentences."""


def _format_context(hits: list[dict]) -> str:
    """Number each retrieved review and label it with professor + course so the
    model can ground claims and the student can trace them."""
    lines = []
    for i, hit in enumerate(hits, 1):
        m = hit["metadata"]
        label = f"{m.get('professor')}"
        if m.get("course"):
            label += f", {m['course']}"
        lines.append(f"[{i}] ({label}) {hit['text']}")
    return "\n\n".join(lines)


def _build_sources(hits: list[dict], answer: str) -> list[str]:
    """One line per professor from the retrieved set that the answer actually
    mentions, with the RMP URL. Built in code (not LLM-generated) so attribution
    is guaranteed and only credits the reviews the answer drew from. Falls back to
    all retrieved professors if the answer names none."""
    matched, fallback, seen_m, seen_f = [], [], set(), set()
    for hit in hits:
        m = hit["metadata"]
        prof = m.get("professor")
        if not prof:
            continue
        url = m.get("source_url", "")
        line = f"{prof} — Rate My Professors ({url})" if url else prof
        if prof not in seen_f:
            seen_f.add(prof)
            fallback.append(line)
        # Credit a professor only if their name appears in the generated answer.
        if prof in answer and prof not in seen_m:
            seen_m.add(prof)
            matched.append(line)
    return matched or fallback


def ask(question: str, k: int = DEFAULT_K) -> dict:
    """Full RAG turn: retrieve -> grounded prompt -> Groq -> answer + sources."""
    hits = retrieve(question, k=k)
    context = _format_context(hits)

    user_prompt = (
        f"CONTEXT (student reviews):\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        f"Answer using only the CONTEXT above."
    )

    response = _client.chat.completions.create(
        model=MODEL,
        temperature=0,  # deterministic, less room to drift off the context
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # If the model declined, don't attach sources (nothing was actually used).
    sources = [] if answer.startswith(REFUSAL) else _build_sources(hits, answer)
    return {"answer": answer, "sources": sources, "hits": hits}


if __name__ == "__main__":
    tests = [
        "What do students say about cheating in Jie Wei's CSC 322 class?",
        "Which professor should I take for Data Structures and why?",
        "Who teaches the quantum computing course at CCNY?",  # out-of-corpus
    ]
    for q in tests:
        print("=" * 78)
        print("Q:", q)
        result = ask(q)
        print("\nANSWER:\n", result["answer"])
        if result["sources"]:
            print("\nRETRIEVED FROM:")
            for s in result["sources"]:
                print("  •", s)
        print()
