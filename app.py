"""
Milestone 5 — Gradio web interface for the Unofficial Guide.

Run:
    python app.py
then open http://localhost:7860

Type a question about a CCNY Computer Science professor; the app retrieves the
most relevant student reviews, generates a grounded answer, and lists the
professors (with Rate My Professors links) the answer drew from.
"""

import gradio as gr

from query import ask

EXAMPLES = [
    "How hard is Douglas Troeger's CSC 335, and how should I prepare?",
    "What do students say about cheating in Jie Wei's CSC 322 class?",
    "Who is a good professor to take for an easy A with a light workload?",
    "Is William Skeith's CSC 103 okay for a complete beginner?",
]


def handle_query(question):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(no sources — not enough information in the reviews)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide — CCNY CS Professors") as demo:
    gr.Markdown(
        "# The Unofficial Guide — CCNY CS Professors\n"
        "Ask what students *actually* say about Computer Science professors at "
        "The City College of New York. Answers come **only** from collected "
        "Rate My Professors reviews — if the reviews don't cover it, the guide says so."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Which professor is best for CSC 322?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    gr.Examples(examples=EXAMPLES, inputs=inp)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
