from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def extract_numbered_items(text: str, limit: int = 5) -> list[str]:
    items: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        line = re.sub(r"^\d+[.)、]\s*", "", line)
        if line:
            items.append(line)
    if not items and text.strip():
        items = [part.strip() for part in re.split(r"[;；\n]", text) if part.strip()]
    return items[:limit]


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
