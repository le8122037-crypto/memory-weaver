import json
import os
from utils.llm_client import chat

_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "extractor.txt")


def _load_system_prompt():
    with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def run(full_text: str) -> dict:
    system_prompt = _load_system_prompt()
    user_message = f"以下是一位老人的口述历史记录，请按要求提取其中的关键信息：\n\n{full_text}"

    response = chat(system_prompt, user_message, temperature=0.3, max_tokens=4096)

    # Extract JSON from response (may be wrapped in ```json blocks)
    json_str = response.strip()
    if json_str.startswith("```"):
        lines = json_str.split("\n")
        json_str = "\n".join(lines[1:-1])

    try:
        events = json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback: try to find JSON array in the response
        import re
        match = re.search(r"\[[\s\S]*\]", json_str)
        if match:
            events = json.loads(match.group())
        else:
            events = [{"error": "Failed to parse events", "raw": response}]

    return {"events": events, "raw_response": response}
