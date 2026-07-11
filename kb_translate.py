"""Optional bilingual helpers for enterprise knowledge base import."""
from __future__ import annotations

import re
from typing import Callable, Optional, Tuple

import requests

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def is_chinese(text: str) -> bool:
    return bool(_CJK_RE.search(text or ""))


def _deepseek_translate(
    text: str,
    target_lang: str,
    *,
    api_key: str,
    base_url: str = "https://api.deepseek.com",
    model: str = "deepseek-chat",
) -> str:
    if not text or not api_key:
        return text
    lang_label = "英文" if target_lang == "en" else "中文"
    prompt = (
        f"请将以下文本翻译成{lang_label}，只输出翻译结果，不要其他内容：\n\n{text}"
        if target_lang == "en"
        else f"Please translate the following text into Chinese. Output translation only:\n\n{text}"
    )
    try:
        response = requests.post(
            f"{base_url.rstrip('/')}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.2,
            },
            timeout=30,
        )
        if response.status_code == 200:
            body = response.json()
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            return (content or text).strip()
    except Exception:
        pass
    return text


def make_kb_translators(
    api_key: str = "",
    base_url: str = "https://api.deepseek.com",
    model: str = "deepseek-chat",
) -> Tuple[Optional[Callable[[str], str]], Optional[Callable[[str], str]]]:
    if not api_key:
        return None, None

    def to_en(text: str) -> str:
        return _deepseek_translate(text, "en", api_key=api_key, base_url=base_url, model=model)

    def to_zh(text: str) -> str:
        return _deepseek_translate(text, "zh", api_key=api_key, base_url=base_url, model=model)

    return to_en, to_zh


def bilingualize_kb_content(
    text: str,
    *,
    translate_to_en: Optional[Callable[[str], str]] = None,
    translate_to_zh: Optional[Callable[[str], str]] = None,
) -> Tuple[str, str]:
    content = (text or "").strip()
    if not content:
        return "", ""

    if is_chinese(content):
        zh_text = content
        en_text = translate_to_en(content) if translate_to_en else content
    else:
        en_text = content
        zh_text = translate_to_zh(content) if translate_to_zh else content
    return zh_text, en_text or zh_text
