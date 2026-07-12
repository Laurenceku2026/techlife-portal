"""Portal child-app catalog and per-organization access helpers."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence

PORTAL_APP_KEYS: Sequence[str] = ("feasibility", "dqa", "fa", "paravary", "eml")

APP_CATALOG: Dict[str, Dict[str, str]] = {
    "feasibility": {
        "name": "📊 Product Feasibility",
        "desc_zh": "产品可行性分析 - 挖掘市场与用户之声",
        "desc_en": "Product Feasibility - Voice of Market & Users",
    },
    "dqa": {
        "name": "🔍 AI-DQA",
        "desc_zh": "设计风险分析 - AI赋能DFMEA",
        "desc_en": "Design Risk Analysis - AI-powered DFMEA",
    },
    "fa": {
        "name": "🔬 AI-FA",
        "desc_zh": "智能故障分析 - AI驱动5-Why根因定位与8D报告",
        "desc_en": "Intelligent Failure Analysis - AI-powered 5-Why Root Cause & 8D Report",
    },
    "paravary": {
        "name": "📈 Para-Vary",
        "desc_zh": "蒙特卡洛模拟 - 累积公差仿真",
        "desc_en": "Monte Carlo Simulation - Tolerance Stack-up",
    },
    "eml": {
        "name": "💡 EML Calculator",
        "desc_zh": "健康照明EML/m-EDI计算器 - 光谱分析与节律效应评估",
        "desc_en": "Healthy Lighting EML/m-EDI Calculator - Spectral Analysis & Circadian Evaluation",
    },
}


def default_enabled_apps() -> List[str]:
    return list(PORTAL_APP_KEYS)


def normalize_enabled_apps(value: Any) -> List[str]:
    if value is None:
        return default_enabled_apps()
    parsed = value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return default_enabled_apps()
    if isinstance(parsed, list):
        filtered = [key for key in parsed if key in PORTAL_APP_KEYS]
        return filtered if filtered else default_enabled_apps()
    return default_enabled_apps()


def org_enabled_apps(org: Dict[str, Any] | None) -> List[str]:
    if not org:
        return default_enabled_apps()
    return normalize_enabled_apps(org.get("enabled_apps"))


def app_display_name(app_key: str, *, lang: str = "zh") -> str:
    entry = APP_CATALOG.get(app_key, {})
    return entry.get("name", app_key)


def app_description(app_key: str, *, lang: str = "zh") -> str:
    entry = APP_CATALOG.get(app_key, {})
    if lang == "en":
        return entry.get("desc_en", "")
    return entry.get("desc_zh", "")
