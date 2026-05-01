"""
tests/test_agent.py — Unit tests for the compliance audit agent.

Run with: pytest tests/
"""

import json
import pytest
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auditor import Auditor, AuditError
from reporter import Reporter
from frameworks import get_controls_for_framework, get_control_by_id


# ────────────────────────────────────────────────────── Auditor._parse_response

VALID_RESPONSE = json.dumps({
    "summary": {"score": 60, "total": 5, "passed": 3, "failed": 1, "warnings": 1},
    "findings": [
        {
            "id": "CIS-1.5",
            "title": "Root MFA not enabled",
            "status": "fail",
            "severity": "critical",
            "framework": "CIS AWS 1.5",
            "category": "IAM",
            "detail": "MFA is not enabled on the root account.",
            "remediation": "Enable MFA on the root account via the AWS Console."
        },
        {
            "id": "CIS-2.2.1",
            "title": "CloudTrail enabled in all regions",
            "status": "pass",
            "severity": "high",
            "framework": "CIS AWS 2.2.1",
            "category": "Logging",
            "detail": "CloudTrail is enabled and covers all regions.",
            "remediation": ""
        }
    ]
})


class TestAuditorParse:
    def setup_method(self):
        self.auditor = Auditor.__new__(Auditor)

    def test_parse_clean_json(self):
        result = self.auditor._parse_response(VALID_RESPONSE)
        assert result["summary"]["score"] == 60
        assert len(result["findings"]) == 2

    def test_parse_json_with_fences(self):
        fenced = f"```json\n{VALID_RESPONSE}\n```"
        result = self.auditor._parse_response(fenced)
        assert result["summary"]["score"] == 60

    def test_parse_json_with_preamble(self):
        preamble = f"Here is the audit result:\n\n{VALID_RESPONSE}\n\nDone."
        result = self.auditor._parse_response(preamble)
        assert result["summary"]["total"] == 5

    def test_parse_raises_on_no_json(self):
        with pytest.raises(AuditError, match="No JSON"):
            self.auditor._parse_response("This is not JSON at all.")

    def test_parse_raises_on_missing_keys(self):
        incomplete = json.dumps({"foo": "bar"})
        with pytest.raises(AuditError, match="missing"):
            self.auditor._parse_response(incomplete)

    def test_findings_sorted_by_severity(self):
        result = self.auditor._parse_response(VALID_RESPONSE)
        severities = [f["severity"] for f in result["findings"]]
        # critical before high
        assert severities[0] == "critical"

    def test_filter_by_severity_high(self):
        result = self.auditor._parse_response(VALID_RESPONSE)
        filtered = self.auditor._filter_by_severity(result, "high")
        sevs = {f["severity"] for f in filtered["findings"]}
        assert "medium" not in sevs
        assert "low" not in sevs

    def test_filter_by_severity_all(self):
        result = self.auditor._parse_response(VALID_RESPONSE)
        filtered = self.auditor._filter_by_severity(result, "all")
        assert len(filtered["findings"]) == len(result["findings"])


# ────────────────────────────────────────────────────── Framework lookups

class TestFrameworks:
    def test_get_cis_controls(self):
        controls = get_controls_for_framework("cis")
        assert all(c.framework == "CIS" for c in controls)

    def test_get_nist_controls(self):
        controls = get_controls_for_framework("nist")
        assert all(c.framework == "NIST" for c in controls)

    def test_get_both_controls(self):
        controls = get_controls_for_framework("both")
        frameworks = {c.framework for c in controls}
        assert "CIS" in frameworks
        assert "NIST" in frameworks

    def test_lookup_by_id(self):
        control = get_control_by_id("CIS-1.5")
        assert control is not None
        assert "MFA" in control.title

    def test_lookup_missing_id(self):
        control = get_control_by_id("CIS-99.99")
        assert control is None

    def test_controls_have_required_fields(self):
        controls = get_controls_for_framework("both")
        for c in controls:
            assert c.id
            assert c.title
            assert c.severity in {"critical", "high", "medium", "low", "info"}
            assert c.category


# ────────────────────────────────────────────────────── Reporter

class TestReporter:
    def setup_method(self):
        self.reporter = Reporter()
        self.result = json.loads(VALID_RESPONSE)
        self.result["meta"] = {"env": "aws", "framework": "both", "model": "claude-sonnet-4-20250514", "input_tokens": 100, "output_tokens": 200}

    def test_write_json(self, tmp_path):
        path = self.reporter.write(self.result, "json", tmp_path, "test", "aws", "both")
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["summary"]["score"] == 60

    def test_write_markdown(self, tmp_path):
        path = self.reporter.write(self.result, "markdown", tmp_path, "test", "aws", "both")
        assert path.exists()
        content = path.read_text()
        assert "Compliance Audit Report" in content
        assert "Root MFA not enabled" in content

    def test_write_html(self, tmp_path):
        path = self.reporter.write(self.result, "html", tmp_path, "test", "aws", "both")
        assert path.exists()
        content = path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "60" in content

    def test_unknown_format_defaults_to_markdown(self, tmp_path):
        path = self.reporter.write(self.result, "xml", tmp_path, "test", "aws", "both")
        assert path.suffix == ".md"
