"""
prompts.py — System and user prompt templates for the compliance audit agent.
"""

ENV_LABELS = {
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "Google Cloud Platform (GCP)",
    "linux": "Linux Server",
    "windows": "Windows Server",
    "k8s": "Kubernetes",
}

FRAMEWORK_LABELS = {
    "cis": "CIS Benchmarks Level 1 and Level 2",
    "nist": "NIST SP 800-53 Rev 5",
    "both": "CIS Benchmarks (Level 1 & 2) and NIST SP 800-53 Rev 5",
    "soc2": "SOC 2 Type II Trust Services Criteria",
}

DEPTH_INSTRUCTIONS = {
    "standard": "Produce 10–14 findings. Include a brief detail and one-line remediation per finding.",
    "detailed": "Produce 14–20 findings. Include a detailed explanation and specific, actionable remediation steps with CLI commands where relevant.",
    "executive": "Produce 6–10 top findings. Focus on business risk and high-level remediation themes. Avoid technical jargon.",
}


def build_system_prompt() -> str:
    return """You are an expert cloud and infrastructure security auditor with deep knowledge of:
- CIS Benchmarks (Level 1 and Level 2) for AWS, Azure, GCP, Linux, Windows, and Kubernetes
- NIST SP 800-53 Rev 5 control families
- SOC 2 Type II Trust Services Criteria

Your job is to analyze configuration snapshots and produce structured, accurate compliance findings.

CRITICAL: You must respond with ONLY a valid JSON object. No markdown formatting, no explanation, no preamble outside the JSON.

Return exactly this structure:
{
  "summary": {
    "score": <integer 0-100, representing overall compliance percentage>,
    "total": <total number of checks performed>,
    "passed": <number of passing checks>,
    "failed": <number of failing checks>,
    "warnings": <number of warning-level findings>
  },
  "findings": [
    {
      "id": "<unique finding ID, e.g. CIS-2.1.1 or NIST-AC-2>",
      "title": "<concise finding title, max 8 words>",
      "status": "<pass | fail | warn>",
      "severity": "<critical | high | medium | low | info>",
      "framework": "<exact control reference, e.g. CIS AWS 2.1.1 or NIST AC-2>",
      "category": "<one of: IAM | Network | Storage | Logging | Encryption | Config | Compute | Container>",
      "detail": "<1-2 sentences: what was found and why it matters>",
      "remediation": "<specific remediation step; include CLI command or exact setting if applicable>"
    }
  ]
}

Rules:
- Be accurate. If the config shows a real vulnerability, flag it. If a control is satisfied, mark it pass.
- Use real CIS or NIST control IDs. Do not invent IDs.
- Severity must reflect actual risk: critical = immediate exploitation risk, high = significant exposure, medium = notable gap, low = best practice deviation, info = informational.
- The compliance score must reflect the ratio of passing checks to total checks, weighted by severity.
- Never include any text outside the JSON object.
"""


def build_user_prompt(
    env: str,
    framework: str,
    config_text: str,
    severity: str,
    depth: str,
) -> str:
    env_label = ENV_LABELS.get(env, env)
    framework_label = FRAMEWORK_LABELS.get(framework, framework)
    depth_instruction = DEPTH_INSTRUCTIONS.get(depth, DEPTH_INSTRUCTIONS["detailed"])

    return f"""Audit the following {env_label} environment configuration against {framework_label}.

Severity filter: include findings at '{severity}' severity and above.
Depth instruction: {depth_instruction}

Configuration snapshot:
---
{config_text}
---

Audit every relevant control for this environment and framework. Be specific about what is present or missing in the config. Generate realistic findings based exactly on what is described. Return only the JSON object.
"""
