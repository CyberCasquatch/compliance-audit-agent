# Compliance Audit Agent

An AI-powered compliance auditing agent that evaluates cloud and system configurations against **CIS Benchmarks** and **NIST SP 800-53** controls, producing actionable findings with remediation guidance.

Built on the Anthropic Claude API.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

---

## Features

- Audits AWS, Azure, GCP, Linux, Windows Server, and Kubernetes environments
- Maps findings to CIS Benchmark control IDs and NIST SP 800-53 control families
- Produces a structured compliance score (0–100)
- Classifies findings by severity: Critical / High / Medium / Low / Info
- Generates specific, actionable remediation steps per finding
- Outputs reports as JSON, Markdown, or HTML
- CLI-first; easy to integrate into CI/CD pipelines

---

## Quickstart

### Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

### Install

```bash
git clone https://github.com/your-org/compliance-audit-agent.git
cd compliance-audit-agent
pip install -r requirements.txt
```

### Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Run an audit

```bash
# Audit from a config file
python src/agent.py --env aws --framework both --input examples/aws_config.json

# Audit from a text description
python src/agent.py --env aws --framework cis --text "AWS account, root MFA disabled, 3 public S3 buckets, CloudTrail off"

# Full options
python src/agent.py --help
```

### Output

By default the agent writes a Markdown report to `./reports/`. Use `--format json` or `--format html` to change the output format.

```
reports/
  audit_2024-01-15_143022.md
  audit_2024-01-15_143022.json
```

---

## Usage

```
usage: agent.py [-h] --env ENV --framework FRAMEWORK [--input INPUT]
                [--text TEXT] [--severity SEVERITY] [--depth DEPTH]
                [--format FORMAT] [--output OUTPUT]

optional arguments:
  --env         Target environment: aws | azure | gcp | linux | windows | k8s
  --framework   Benchmark: cis | nist | both | soc2
  --input       Path to config file (JSON, YAML, or plain text)
  --text        Inline config description (alternative to --input)
  --severity    Minimum severity to report: critical | high | medium | all (default: all)
  --depth       Report depth: standard | detailed | executive (default: detailed)
  --format      Output format: markdown | json | html (default: markdown)
  --output      Output directory (default: ./reports)
```

---

## Project structure

```
compliance-audit-agent/
├── src/
│   ├── agent.py          # Main agent entrypoint
│   ├── auditor.py        # Core audit logic and Claude API calls
│   ├── reporter.py       # Report generation (Markdown, JSON, HTML)
│   ├── frameworks.py     # CIS / NIST control definitions
│   └── prompts.py        # System and user prompt templates
├── examples/
│   ├── aws_config.json   # Example AWS config snapshot
│   ├── linux_config.txt  # Example Linux sysctl/sshd output
│   └── k8s_config.yaml   # Example Kubernetes audit config
├── scripts/
│   ├── collect_aws.sh    # Collect AWS config via CLI for auditing
│   └── collect_linux.sh  # Collect Linux config for auditing
├── docs/
│   ├── frameworks.md     # Notes on CIS and NIST frameworks
│   └── extending.md      # How to add new frameworks
├── tests/
│   └── test_agent.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Configuration collection scripts

Use the helper scripts to collect configuration data from your environment before auditing:

```bash
# AWS — requires AWS CLI configured
bash scripts/collect_aws.sh > my_aws_config.txt
python src/agent.py --env aws --framework both --input my_aws_config.txt

# Linux
bash scripts/collect_linux.sh > my_linux_config.txt
python src/agent.py --env linux --framework cis --input my_linux_config.txt
```

---

## Supported frameworks

| Framework | Coverage |
|-----------|----------|
| CIS Benchmarks Level 1 | AWS, Azure, GCP, Linux, Windows, K8s |
| CIS Benchmarks Level 2 | AWS, Azure, GCP, Linux |
| NIST SP 800-53 Rev 5 | All environments |
| SOC 2 Type II | Cloud environments |

---

## License

MIT — see [LICENSE](LICENSE).
