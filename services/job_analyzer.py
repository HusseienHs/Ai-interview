import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables")

# Initialize LLM client
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)


def _extract_json(text: str):
    """
    Safely extract JSON from LLM response.
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {
        "role": "Unknown",
        "seniority": "Unknown",
        "required_skills": [],
        "focus_areas": [],
    }


def analyze_job(description: str) -> dict:
    """
    Analyze job description and extract structured role information.
    """

    # Prevent extremely large prompts
    description = description[:4000]

    prompt = f"""
You are an expert technical recruiter.

Extract structured information from the job description.

Return ONLY valid JSON. Do not include explanations or markdown.

JSON format:

{{
  "role": "job title",
  "seniority": "Junior | Mid | Senior | Student/Intern",
  "required_skills": ["skill1", "skill2"],
  "focus_areas": ["area1", "area2"]
}}

Guidelines:
- Extract programming languages, tools, and technologies as skills.
- Focus areas should describe the type of engineering work.
- Do not invent information that is not in the description.

Job Description:
{description}
"""

    try:
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        response = completion.choices[0].message.content

        result = _extract_json(response)

        return result

    except Exception as e:
        print("Job analysis error:", e)

        return {
            "role": "Unknown",
            "seniority": "Unknown",
            "required_skills": [],
            "focus_areas": [],
        }