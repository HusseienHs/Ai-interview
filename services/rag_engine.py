import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Load questions dataset
# -----------------------------
with open("questions.json", "r") as f:
    data = json.load(f)

questions = [item["question"] for item in data]
skills = [item.get("skill", "").lower() for item in data]
difficulties = [item.get("difficulty", "medium") for item in data]

# -----------------------------
# Compute embeddings ONCE
# -----------------------------
embeddings = model.encode(questions, convert_to_numpy=True)

# Normalize embeddings for cosine similarity
faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]

# Build FAISS index once
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)


def retrieve_question(skill: str, difficulty: str = "medium", k: int = 3):
    """
    Retrieve k similar interview questions based on skill and difficulty.
    """

    skill = skill.lower()

    # Encode query
    query_embedding = model.encode([skill], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    # Search vector index
    distances, indices = index.search(query_embedding, k * 3)

    results = []

    for idx in indices[0]:
        if idx >= len(data):
            continue

        item = data[idx]

        if (
            item.get("difficulty", "medium") == difficulty
            and skill in item.get("skill", "").lower()
        ):
            results.append(item["question"])

        if len(results) >= k:
            break

    # fallback if not enough filtered results
    if len(results) < k:
        for idx in indices[0]:
            results.append(data[idx]["question"])
            if len(results) >= k:
                break

    return results