from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def rank_skills(job_description, skills):

    job_embedding = model.encode([job_description])[0]

    skill_embeddings = model.encode(skills)

    scores = []

    for i, skill in enumerate(skills):

        similarity = np.dot(job_embedding, skill_embeddings[i]) / (
            np.linalg.norm(job_embedding) *
            np.linalg.norm(skill_embeddings[i])
        )

        scores.append((skill, similarity))

    scores.sort(key=lambda x: x[1], reverse=True)

    ranked_skills = [skill for skill, _ in scores]

    return ranked_skills