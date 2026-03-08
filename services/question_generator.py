import os
from dotenv import load_dotenv
from openai import OpenAI
from services.rag_engine import retrieve_question

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables")

# -----------------------------
# Initialize LLM client
# -----------------------------
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)


def generate_question(role: str, level: str, topic: str, difficulty: str = "medium"):
    """
    Generate an interview question using RAG + LLM.
    """

    retrieved_questions = retrieve_question(topic, difficulty)

    context = "\n".join(retrieved_questions)

    prompt = f"""
You are a senior software engineering interviewer.

Generate ONE interview question suitable for the candidate level.

Difficulty rules:
- easy → basic concepts
- medium → practical engineering knowledge
- hard → advanced design or deep internals

The candidate is a student or early-career engineer.
Avoid extremely advanced compiler or memory model questions.

Candidate Profile:
Role: {role}
Experience Level: {level}
Topic: {topic}
Difficulty: {difficulty}

Example questions from real interviews:
{context}

Guidelines:
- Ask a clear technical question
- Focus on programming fundamentals or system knowledge
- Keep it similar in style to real software engineering interviews
- Avoid extremely niche or compiler-specific questions

Return ONLY the interview question.
"""

    try:

        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        question = completion.choices[0].message.content.strip()

        return question

    except Exception as e:

        print("Question generation error:", e)

        return "Could not generate interview question."


# -----------------------------
# Local test
# -----------------------------
if __name__ == "__main__":

    question = generate_question(
        role="C++ Software Engineer",
        level="Student",
        topic="C++",
        difficulty="medium",
    )

    print("\nGenerated Question:\n")
    print(question)