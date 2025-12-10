import os
import openai
from dotenv import load_dotenv

load_dotenv()  # load .env

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    resp = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role":"user","content":"Show revenue by month"}],
        temperature=0
    )
    print(resp.choices[0].message.content)
except Exception as e:
    print("LLM test failed:", e)
