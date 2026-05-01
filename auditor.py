"""
auditor.py — Core audit logic. Calls the Anthropic Claude API and parses results.
"""

import json
import re
from typing import Any

import anthropic

from prompts import build_system_prompt, build_user_prompt


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

SEVERITY_FILTER_MAP = {
    "critical": {"critical"},
    "high": {"critical", "high"},
    "medium": {"critical", "high", "medium"},
    "all": {"critical", "high", "medium", "low", "info"},
}


class AuditError(Exception):
    pass


class Auditor:
    """Wraps the Claude API to perform compliance audits."""

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4096

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def audit(
        self,
        env: str,
        framework: str,
        config_text: str,
        severity: str = "all",
        depth: str = "detailed",
    ) -> dict[str, Any]:
        """
        Run a compliance audit.

        Returns a dict with keys:
            summary  : { score, total, passed, failed, warnings }
            findings : list of finding dicts
            meta     : audit metadata
        """
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            env=env,
            framework=framework,
            config_text=config_text,
            severity=severity,
            depth=depth,
        )

        message = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw = "".join(
            block.text for block in message.content if hasattr(block, "text")
        )

        result = self._parse_response(raw)
        result = self._filter_by_severity(result, severity)
        result["meta"] = {
            "env": env,
            "framework": framework,
            "severity_filter": severity,
            "depth": depth,
            "model": self.MODEL,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }
        return result

    def _parse_response(self, raw: str) -> dict[str, Any]:
        """Strip markdown fences and parse JSON from model response."""
        cleaned = re.sub(r"```(?:json)?", "", raw).strip()
        # Find the outermost JSON object
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start == -1 or end == 0:
            raise AuditError(f"No JSON object found in model response.\nRaw:\n{raw[:500]}")
        try:
            data = json.loads(cleaned[start:end])
        except json.JSONDecodeError as e:
            raise AuditError(f"Failed to parse JSON from model response: {e}\nRaw:\n{raw[:500]}")

        if "findings" not in data or "summary" not in data:
            raise AuditError(f"Unexpected response shape — missing 'findings' or 'summary'.\nData: {data}")

        # Sort findings by severity
        data["findings"].sort(
            key=lambda f: SEVERITY_ORDER.get(f.get("severity", "info"), 99)
        )
        return data

    def _filter_by_severity(self, result: dict, severity: str) -> dict:
        allowed = SEVERITY_FILTER_MAP.get(severity, SEVERITY_FILTER_MAP["all"])
        filtered = [f for f in result["findings"] if f.get("severity", "info") in allowed]
        result["findings"] = filtered
        # Recompute summary counts from filtered findings
        passed = sum(1 for f in filtered if f.get("status") == "pass")
        failed = sum(1 for f in filtered if f.get("status") == "fail")
        warnings = sum(1 for f in filtered if f.get("status") == "warn")
        total = len(filtered)
        result["summary"]["total"] = total
        result["summary"]["passed"] = passed
        result["summary"]["failed"] = failed
        result["summary"]["warnings"] = warnings
        return result
