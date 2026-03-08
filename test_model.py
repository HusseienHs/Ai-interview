import os
from openai import OpenAI

api_key = os.environ.get("HF_API_KEY")
if not api_key:
    raise RuntimeError(
        "Environment variable HF_API_KEY is not set.\n"
        "Set it to your Hugging Face token, e.g. in PowerShell: `$env:HF_API_KEY = \"hf_...\"`"
    )

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=api_key,
)

completion = client.chat.completions.create(
    model="moonshotai/Kimi-K2-Instruct-0905",
    messages=[
        {
            "role": "user",
            "content": "Explain the theory of relativity in simple terms."
        }
    ],
)

print(completion.choices[0].message.content)
