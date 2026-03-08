import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

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

# -----------------------------
# Cache for expected concepts
# -----------------------------
concept_cache = {}

# -----------------------------
# Utility: Extract JSON safely
# -----------------------------
def extract_json(text):
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            data = json.loads(text[start:end])

            if "score" in data:
                data["score"] = max(0, min(10, int(data["score"])))

            return data
    except:
        pass

    return {
        "score": 0,
        "technical_accuracy": "Evaluation failed.",
        "depth": "Evaluation failed.",
        "missing_concepts": [],
        "improved_answer": "Could not generate improved answer."
    }

# -----------------------------
# Detect if answer repeats question
# -----------------------------
def is_repeating_question(question, answer):

    q = question.strip().lower()
    a = answer.strip().lower()

    if a == q:
        return True

    q_words = set(q.split())
    a_words = set(a.split())

    if len(q_words) == 0:
        return False

    similarity = len(q_words & a_words) / len(q_words)

    return similarity > 0.9


# -----------------------------
# Extract expected concepts
# -----------------------------
def extract_expected_concepts(question):

    if question in concept_cache:
        return concept_cache[question]

    prompt = f"""
List the key technical concepts required to correctly answer this interview question.

Question:
{question}

Return ONLY a JSON array.

Example:
["concept1","concept2","concept3"]
"""

    try:

        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[
                {"role": "system", "content": "You are a software engineering interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        text = completion.choices[0].message.content

        start = text.find("[")
        end = text.rfind("]") + 1

        if start != -1 and end != -1:
            concepts = json.loads(text[start:end])
            concept_cache[question] = concepts
            return concepts

    except:
        pass

    return []


# -----------------------------
# Check answer relevance
# -----------------------------
def is_relevant_answer(question, answer):

    prompt = f"""
Determine if the candidate answer is relevant to the interview question.

Question:
{question}

Answer:
{answer}

Return ONLY JSON:
{{"relevant": true}} or {{"relevant": false}}
"""

    try:

        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[
                {"role": "system", "content": "You evaluate interview answers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = extract_json(completion.choices[0].message.content)

        return result.get("relevant", True)

    except:
        return True


# -----------------------------
# Main Evaluation Function
# -----------------------------
def evaluate_answer(question, answer, level="mid"):

    answer_clean = answer.strip()

    # -----------------------------
    # Guard 1: Empty answer
    # -----------------------------
    if len(answer_clean) == 0:
        return {
            "score": 0,
            "technical_accuracy": "No answer provided.",
            "depth": "No explanation.",
            "missing_concepts": [],
            "improved_answer": "Provide a clear technical explanation of the concept."
        }

    # -----------------------------
    # Guard 2: Very short answer
    # -----------------------------
    if len(answer_clean) < 10:
        return {
            "score": 0,
            "technical_accuracy": "Answer too short to demonstrate understanding.",
            "depth": "No meaningful explanation.",
            "missing_concepts": [],
            "improved_answer": "Provide a clear explanation of the concept."
        }

    # -----------------------------
    # Guard 3: Copied question
    # -----------------------------
    if is_repeating_question(question, answer):
        return {
            "score": 0,
            "technical_accuracy": "The candidate repeated the question without answering.",
            "depth": "No technical explanation provided.",
            "missing_concepts": [],
            "improved_answer": "Provide a technical explanation that answers the question."
        }

    # -----------------------------
    # Guard 4: Irrelevant answer
    # -----------------------------
    if not is_relevant_answer(question, answer):
        return {
            "score": 0,
            "technical_accuracy": "Answer is unrelated to the question.",
            "depth": "No relevant explanation.",
            "missing_concepts": [],
            "improved_answer": "Provide an answer that directly addresses the question."
        }

    # -----------------------------
    # Extract expected concepts
    # -----------------------------
    expected_concepts = extract_expected_concepts(question)

    # -----------------------------
    # Prompt for evaluation
    # -----------------------------
    prompt = f"""
You are a strict senior technical interviewer evaluating candidate answers.

Candidate Level: {level}

Question:
{question}

Expected concepts in a strong answer:
{expected_concepts}

Candidate Answer:
{answer}

Evaluation rubric:

0 = no understanding
1-2 = extremely poor
3-4 = weak answer
5-6 = basic understanding
7-8 = good answer
9-10 = excellent answer

Evaluate:
- technical accuracy
- depth of explanation
- coverage of expected concepts

Return ONLY valid JSON:

{{
"score": number,
"technical_accuracy": "short explanation",
"depth": "short explanation",
"missing_concepts": ["concept1", "concept2"],
"improved_answer": "a concise improved answer (2-3 sentences)"
}}
"""

    try:

        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer evaluating interview answers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        response = completion.choices[0].message.content

        result = extract_json(response)

        result.setdefault("score", 0)
        result.setdefault("technical_accuracy", "")
        result.setdefault("depth", "")
        result.setdefault("missing_concepts", [])
        result.setdefault("improved_answer", "")

        return result

    except Exception as e:

        print("Evaluation error:", e)

        return {
            "score": 0,
            "technical_accuracy": "Evaluation failed.",
            "depth": "Evaluation failed.",
            "missing_concepts": [],
            "improved_answer": "Could not evaluate the answer."
        }


# -----------------------------
# Local testing
# -----------------------------
if __name__ == "__main__":

    question = "Explain what a pointer is in C."

    answer = input("Enter candidate answer:\n")

    result = evaluate_answer(question, answer)

    print("\nEvaluation:\n")
    print(json.dumps(result, indent=2))