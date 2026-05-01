"""
agent.py — Compliance Audit Agent entrypoint

Usage:
    python src/agent.py --env aws --framework both --input examples/aws_config.json
    python src/agent.py --env linux --framework cis --text "sshd running, root login enabled, no firewall"
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from auditor import Auditor
from reporter import Reporter


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI-powered compliance auditor — CIS Benchmarks & NIST SP 800-53"
    )
    parser.add_argument(
        "--env",
        required=True,
        choices=["aws", "azure", "gcp", "linux", "windows", "k8s"],
        help="Target environment to audit",
    )
    parser.add_argument(
        "--framework",
        required=True,
        choices=["cis", "nist", "both", "soc2"],
        help="Compliance framework to audit against",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to config file (JSON, YAML, or plain text)",
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Inline config description (alternative to --input)",
    )
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "all"],
        default="all",
        help="Minimum severity threshold to include in report",
    )
    parser.add_argument(
        "--depth",
        choices=["standard", "detailed", "executive"],
        default="detailed",
        help="Report depth",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./reports",
        help="Output directory for reports",
    )
    return parser.parse_args()


def load_config(args) -> str:
    if args.input and args.text:
        print("Error: provide either --input or --text, not both.", file=sys.stderr)
        sys.exit(1)

    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        return path.read_text(encoding="utf-8")

    if args.text:
        return args.text

    print("Error: provide a config via --input <file> or --text '<description>'.", file=sys.stderr)
    sys.exit(1)


def main():
    args = parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    config_text = load_config(args)

    print(f"\n  Compliance Audit Agent")
    print(f"  Environment : {args.env.upper()}")
    print(f"  Framework   : {args.framework.upper()}")
    print(f"  Severity    : {args.severity}")
    print(f"  Depth       : {args.depth}")
    print(f"  Output      : {args.format}")
    print()

    auditor = Auditor(api_key=api_key)

    print("[1/3] Running audit…")
    result = auditor.audit(
        env=args.env,
        framework=args.framework,
        config_text=config_text,
        severity=args.severity,
        depth=args.depth,
    )

    print(f"[2/3] Audit complete — {len(result['findings'])} findings, score {result['summary']['score']}/100")

    reporter = Reporter()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    stem = f"audit_{timestamp}"

    print("[3/3] Writing report…")
    output_path = reporter.write(
        result=result,
        fmt=args.format,
        output_dir=output_dir,
        stem=stem,
        env=args.env,
        framework=args.framework,
    )

    print(f"\n  Report saved to: {output_path}")
    print(f"  Score : {result['summary']['score']}/100")
    print(f"  Passed  : {result['summary']['passed']}")
    print(f"  Failed  : {result['summary']['failed']}")
    print(f"  Warnings: {result['summary']['warnings']}")
    print()


if __name__ == "__main__":
    main()
