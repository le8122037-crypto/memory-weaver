import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Token tracking for demo purposes
token_usage = {"prompt": 0, "completion": 0, "total": 0}


def add_usage(prompt_tokens: int, completion_tokens: int):
    token_usage["prompt"] += prompt_tokens
    token_usage["completion"] += completion_tokens
    token_usage["total"] += prompt_tokens + completion_tokens
