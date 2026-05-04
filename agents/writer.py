import json
import os
from utils.llm_client import chat

_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "writer.txt")


def _load_system_prompt():
    with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def run(timeline: dict, full_text: str) -> dict:
    system_prompt = _load_system_prompt()
    timeline_json = json.dumps(timeline, ensure_ascii=False, indent=2)
    user_message = (
        f"以下是传记大纲（JSON格式）：\n```json\n{timeline_json}\n```\n\n"
        f"以下是老人口述的原始文本，供你从中提取生动的细节和原话：\n\n{full_text}"
    )

    response = chat(system_prompt, user_message, temperature=0.8, max_tokens=8192)

    return {"biography": response, "raw_response": response}
