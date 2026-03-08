import streamlit as st
import random

from services.question_generator import generate_question
from services.job_analyzer import analyze_job
from services.answer_evaluator import evaluate_answer
from services.skill_ranker import rank_skills


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Interview Trainer",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Interview Trainer")


# -----------------------------
# Session State Initialization
# -----------------------------
def init_session():

    defaults = {
        "job_info": None,
        "skill_scores": {},
        "difficulty": "medium",
        "question": None,
        "current_skill": None,
        "history": []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session()


# -----------------------------
# Utility Functions
# -----------------------------
def get_weak_skill():

    scores = st.session_state.skill_scores

    if not scores:
        return None

    averages = {
        skill: sum(vals) / len(vals)
        for skill, vals in scores.items()
    }

    return min(averages, key=averages.get)


def update_difficulty(score):

    if score >= 8:
        return "hard"

    if score <= 4:
        return "easy"

    return "medium"


def select_topic(job_info):

    skills = job_info["skill_priority"]

    if len(skills) >= 3:
        return random.choice(skills[:3])  # prefer top ranked skills

    return random.choice(skills)


# -----------------------------
# Layout
# -----------------------------
col1, col2 = st.columns([2, 1])


# =============================
# LEFT PANEL
# =============================
with col1:

    st.header("Job Description")

    job_desc = st.text_area(
        "Paste the job description",
        height=220
    )

    if st.button("Analyze Job"):

        if not job_desc.strip():
            st.warning("Please paste a job description.")
        else:

            with st.spinner("Analyzing job description..."):

                job_info = analyze_job(job_desc)

                # NEW: semantic skill ranking
                skill_priority = rank_skills(
                    job_desc,
                    job_info["required_skills"]
                )

                job_info["skill_priority"] = skill_priority

                st.session_state.job_info = job_info

            st.success("Job analyzed successfully")

            st.subheader("Extracted Information")
            st.json(job_info)


    # -------------------------
    # Generate Interview Question
    # -------------------------
    if st.session_state.job_info:

        if st.button("Generate Question"):

            job_info = st.session_state.job_info

            role = job_info["role"]
            level = job_info["seniority"]

            weak_skill = get_weak_skill()

            if weak_skill:
                topic = weak_skill
            else:
                topic = select_topic(job_info)

            with st.spinner("Generating interview question..."):

                question = generate_question(
                    role,
                    level,
                    topic,
                    st.session_state.difficulty
                )

            st.session_state.question = question
            st.session_state.current_skill = topic

        if st.session_state.question:

            st.subheader("Interview Question")

            st.info(st.session_state.question)

            answer = st.text_area(
                "Your Answer",
                height=180
            )

            if st.button("Submit Answer"):

                if not answer.strip():
                    st.warning("Please provide an answer.")
                else:

                    with st.spinner("Evaluating answer..."):

                        evaluation = evaluate_answer(
                            st.session_state.question,
                            answer,
                            st.session_state.job_info["seniority"]
                        )

                    score = evaluation["score"]

                    st.subheader("Evaluation")

                    st.metric("Score", f"{score}/10")

                    # Difficulty update
                    st.session_state.difficulty = update_difficulty(score)

                    # Skill tracking
                    skill = st.session_state.current_skill

                    if skill not in st.session_state.skill_scores:
                        st.session_state.skill_scores[skill] = []

                    st.session_state.skill_scores[skill].append(score)

                    # Feedback
                    st.write("### Technical Accuracy")
                    st.write(evaluation["technical_accuracy"])

                    st.write("### Depth")
                    st.write(evaluation["depth"])

                    st.write("### Missing Concepts")
                    st.write(evaluation["missing_concepts"])

                    st.write("### Improved Answer")
                    st.write(evaluation["improved_answer"])

                    # Save history
                    st.session_state.history.append({
                        "question": st.session_state.question,
                        "score": score,
                        "skill": skill
                    })

                    # Reset question
                    st.session_state.question = None


# =============================
# RIGHT PANEL (Analytics)
# =============================
with col2:

    st.header("Interview Analytics")

    if st.session_state.skill_scores:

        st.subheader("Skill Performance")

        for skill, scores in st.session_state.skill_scores.items():

            avg = sum(scores) / len(scores)

            st.write(f"**{skill}**")

            st.progress(avg / 10)

            st.caption(f"Average Score: {round(avg,2)}/10")


    if st.session_state.history:

        st.subheader("Interview History")

        for item in reversed(st.session_state.history[-5:]):

            st.write("**Question:**")
            st.write(item["question"])

            st.write("Score:", item["score"])

            st.write("---")