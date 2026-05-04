from openai import OpenAI, APIConnectionError, APITimeoutError
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, add_usage


def _get_client():
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=60.0)


def chat(system_prompt: str, user_message: str,
         temperature: float = 0.7, max_tokens: int = 4096) -> str:
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except APITimeoutError:
        raise RuntimeError("LLM API 请求超时，请检查网络或 API 服务状态")
    except APIConnectionError:
        raise RuntimeError(f"无法连接到 LLM 服务 ({LLM_BASE_URL})，请检查 API 地址和网络")
    except Exception as e:
        err = str(e)
        if "401" in err or "403" in err or "auth" in err.lower():
            raise RuntimeError("API Key 无效，请检查 .env 中的 LLM_API_KEY")
        raise RuntimeError(f"LLM 调用失败: {err}")

    usage = response.usage
    if usage:
        add_usage(usage.prompt_tokens, usage.completion_tokens)

    return response.choices[0].message.content
