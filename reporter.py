"""
reporter.py — Generates Markdown, JSON, and HTML compliance reports.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
    "info": "⚪",
}

STATUS_SYMBOL = {
    "pass": "✅",
    "fail": "❌",
    "warn": "⚠️",
}


class Reporter:
    """Writes audit results to disk in the requested format."""

    def write(
        self,
        result: dict[str, Any],
        fmt: str,
        output_dir: Path,
        stem: str,
        env: str,
        framework: str,
    ) -> Path:
        writers = {
            "markdown": self._write_markdown,
            "json": self._write_json,
            "html": self._write_html,
        }
        writer = writers.get(fmt, self._write_markdown)
        return writer(result, output_dir, stem, env, framework)

    # ------------------------------------------------------------------ JSON

    def _write_json(self, result, output_dir, stem, env, framework) -> Path:
        path = output_dir / f"{stem}.json"
        path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return path

    # ------------------------------------------------------------------ Markdown

    def _write_markdown(self, result, output_dir, stem, env, framework) -> Path:
        s = result["summary"]
        meta = result.get("meta", {})
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score = s["score"]
        grade = "COMPLIANT" if score >= 80 else "PARTIAL" if score >= 60 else "NON-COMPLIANT"

        lines = [
            f"# Compliance Audit Report",
            f"",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| Date | {now} |",
            f"| Environment | {env.upper()} |",
            f"| Framework | {framework.upper()} |",
            f"| Model | {meta.get('model', 'N/A')} |",
            f"",
            f"## Summary",
            f"",
            f"**Compliance Score: {score}/100 — {grade}**",
            f"",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| ✅ Passed | {s['passed']} |",
            f"| ❌ Failed | {s['failed']} |",
            f"| ⚠️ Warnings | {s['warnings']} |",
            f"| Total checks | {s['total']} |",
            f"",
            f"---",
            f"",
            f"## Findings",
            f"",
        ]

        for f in result["findings"]:
            sev_icon = SEVERITY_EMOJI.get(f.get("severity", "info"), "⚪")
            status_icon = STATUS_SYMBOL.get(f.get("status", "info"), "❓")
            lines += [
                f"### {status_icon} {f.get('title', 'Untitled')}",
                f"",
                f"| Field | Value |",
                f"|-------|-------|",
                f"| ID | `{f.get('id', 'N/A')}` |",
                f"| Status | {f.get('status', '').upper()} |",
                f"| Severity | {sev_icon} {f.get('severity', '').upper()} |",
                f"| Framework | {f.get('framework', 'N/A')} |",
                f"| Category | {f.get('category', 'N/A')} |",
                f"",
            ]
            if f.get("detail"):
                lines += [f"**Finding:** {f['detail']}", f""]
            if f.get("remediation") and f.get("status") != "pass":
                lines += [f"**Remediation:** {f['remediation']}", f""]
            lines.append("---")
            lines.append("")

        path = output_dir / f"{stem}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    # ------------------------------------------------------------------ HTML

    def _write_html(self, result, output_dir, stem, env, framework) -> Path:
        s = result["summary"]
        score = s["score"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        grade = "Compliant" if score >= 80 else "Partially compliant" if score >= 60 else "Non-compliant"
        grade_color = "#2E7D4F" if score >= 80 else "#8A5A00" if score >= 60 else "#B33030"

        finding_rows = ""
        for f in result["findings"]:
            sev = f.get("severity", "info")
            status = f.get("status", "info")
            sev_colors = {
                "critical": "#B33030", "high": "#D85A30",
                "medium": "#8A5A00", "low": "#555", "info": "#185FA5"
            }
            status_icons = {"pass": "✓", "fail": "✕", "warn": "!"}
            status_colors = {"pass": "#2E7D4F", "fail": "#B33030", "warn": "#8A5A00"}
            remediation_html = ""
            if f.get("remediation") and status != "pass":
                remediation_html = f'<p style="margin:8px 0 0;font-size:12px;color:#185FA5;font-family:monospace;background:#EAF2FC;padding:8px 10px;border-radius:6px;">→ {f["remediation"]}</p>'
            finding_rows += f"""
            <div style="background:#F7F6F2;border-radius:8px;padding:14px 16px;margin-bottom:10px;border:0.5px solid rgba(0,0,0,0.1);">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <span style="width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:{status_colors.get(status,'#555')}20;color:{status_colors.get(status,'#555')}">{status_icons.get(status,'?')}</span>
                <strong style="font-size:14px;">{f.get('title','')}</strong>
              </div>
              <div style="font-size:11px;font-family:monospace;color:#888;margin-bottom:6px;">
                <span style="color:{sev_colors.get(sev,'#555')};font-weight:600;">{sev.upper()}</span>
                &nbsp;·&nbsp;{f.get('id','')}&nbsp;·&nbsp;{f.get('framework','')}&nbsp;·&nbsp;<span style="background:#E8E6E0;padding:2px 6px;border-radius:4px;">{f.get('category','')}</span>
              </div>
              {f'<p style="font-size:13px;color:#444;margin:0;">{f["detail"]}</p>' if f.get("detail") else ""}
              {remediation_html}
            </div>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Compliance Audit Report — {env.upper()} — {now}</title>
<style>
  body {{ font-family: 'DM Sans', system-ui, sans-serif; background: #F0EEE8; margin: 0; padding: 32px 24px; color: #1A1917; }}
  .container {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ font-size: 22px; font-weight: 600; letter-spacing: -0.02em; margin-bottom: 4px; }}
  .meta {{ font-size: 12px; color: #888; font-family: monospace; margin-bottom: 24px; }}
  .score-card {{ background: #fff; border-radius: 12px; padding: 20px 24px; border: 0.5px solid rgba(0,0,0,0.12); margin-bottom: 20px; display:flex; align-items:center; gap: 24px; }}
  .score-num {{ font-size: 48px; font-weight: 700; font-family: monospace; color: {grade_color}; line-height: 1; }}
  .score-label {{ font-size: 18px; color: {grade_color}; font-weight: 500; }}
  .score-meta {{ font-size: 12px; color: #888; margin-top: 4px; }}
  .stats {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 20px; }}
  .stat {{ background: #fff; border-radius: 8px; padding: 12px 14px; border: 0.5px solid rgba(0,0,0,0.10); }}
  .stat .n {{ font-size: 22px; font-weight: 600; font-family: monospace; }}
  .stat .l {{ font-size: 11px; color: #888; font-family: monospace; margin-top: 2px; }}
  .section-title {{ font-size: 11px; font-family: monospace; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 0.5px solid rgba(0,0,0,0.10); }}
  .panel {{ background: #fff; border-radius: 12px; padding: 20px 24px; border: 0.5px solid rgba(0,0,0,0.12); }}
</style>
</head>
<body>
<div class="container">
  <h1>Compliance Audit Report</h1>
  <p class="meta">Environment: {env.upper()} &nbsp;·&nbsp; Framework: {framework.upper()} &nbsp;·&nbsp; {now}</p>

  <div class="score-card">
    <div class="score-num">{score}</div>
    <div>
      <div class="score-label">{grade}</div>
      <div class="score-meta">Compliance score out of 100</div>
    </div>
  </div>

  <div class="stats">
    <div class="stat"><div class="n" style="color:#2E7D4F">{s['passed']}</div><div class="l">passed</div></div>
    <div class="stat"><div class="n" style="color:#B33030">{s['failed']}</div><div class="l">failed</div></div>
    <div class="stat"><div class="n" style="color:#8A5A00">{s['warnings']}</div><div class="l">warnings</div></div>
    <div class="stat"><div class="n">{s['total']}</div><div class="l">total checks</div></div>
  </div>

  <div class="panel">
    <div class="section-title">Findings</div>
    {finding_rows}
  </div>
</div>
</body>
</html>"""

        path = output_dir / f"{stem}.html"
        path.write_text(html, encoding="utf-8")
        return path
