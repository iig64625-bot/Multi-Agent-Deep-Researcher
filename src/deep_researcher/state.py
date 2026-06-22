from __future__ import annotations

from typing import Any, TypedDict


class Citation(TypedDict, total=False):
    id: int
    title: str
    url: str
    snippet: str
    source: str


class Finding(TypedDict, total=False):
    subquestion: str
    summary: str
    sources: list[Citation]


class CriticReview(TypedDict, total=False):
    score: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]


class ResearchState(TypedDict, total=False):
    question: str
    plan: list[str]
    findings: list[Finding]
    synthesis: str
    citations: list[Citation]
    report: str
    critic: CriticReview
    messages: list[str]
    rewrite_count: int
    settings: Any