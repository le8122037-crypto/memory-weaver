import json
import os
from utils.llm_client import chat

_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "planner.txt")


def _load_system_prompt():
    with open(_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def run(events: list, full_text: str) -> dict:
    system_prompt = _load_system_prompt()
    events_json = json.dumps(events, ensure_ascii=False, indent=2)
    user_message = (
        f"以下是已提取的事件列表（JSON格式）：\n```json\n{events_json}\n```\n\n"
        f"以下是原始口述文本，供你核对细节和寻找关键原句：\n\n{full_text}"
    )

    response = chat(system_prompt, user_message, temperature=0.5, max_tokens=4096)

    json_str = response.strip()
    if json_str.startswith("```"):
        lines = json_str.split("\n")
        json_str = "\n".join(lines[1:-1])

    try:
        timeline = json.loads(json_str)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{[\s\S]*\}", json_str)
        if match:
            timeline = json.loads(match.group())
        else:
            timeline = {"error": "Failed to parse timeline", "raw": response}

    return {"timeline": timeline, "raw_response": response}
