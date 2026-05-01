# Extending the Agent

## Adding a new environment

1. Add the environment key and label to `ENV_LABELS` in `src/prompts.py`
2. Add the environment to the `--env` choices in `src/agent.py`
3. Optionally create a `scripts/collect_<env>.sh` helper
4. Add example config to `examples/`

## Adding a new framework

1. Add the framework key and label to `FRAMEWORK_LABELS` in `src/prompts.py`
2. Add control definitions to `src/frameworks.py`
3. Add the framework to the `--framework` choices in `src/agent.py`

## Customising the system prompt

Edit `src/prompts.py` → `build_system_prompt()`. You can add:
- Domain-specific context (e.g. HIPAA, PCI-DSS)
- Output format changes
- Stricter or looser scoring instructions

## Integrating into CI/CD

The agent exits with code 0 on success. To fail a pipeline on poor compliance:

```bash
#!/bin/bash
python src/agent.py --env aws --framework cis --input config.json --format json --output /tmp/reports
SCORE=$(python -c "import json; d=json.load(open('/tmp/reports/$(ls /tmp/reports | tail -1)')); print(d['summary']['score'])")
if [ "$SCORE" -lt 70 ]; then
  echo "Compliance score $SCORE below threshold (70). Failing build."
  exit 1
fi
```

## Output format — adding SARIF

The SARIF (Static Analysis Results Interchange Format) is useful for GitHub Advanced Security integration. To add a SARIF writer, add a `_write_sarif` method to `src/reporter.py`:

```python
def _write_sarif(self, result, output_dir, stem, env, framework) -> Path:
    runs = []
    for f in result['findings']:
        runs.append({
            "ruleId": f.get('id', 'UNKNOWN'),
            "message": {"text": f.get('detail', '')},
            "level": "error" if f.get('status') == 'fail' else "warning",
        })
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{"tool": {"driver": {"name": "compliance-audit-agent"}}, "results": runs}]
    }
    path = output_dir / f"{stem}.sarif"
    path.write_text(json.dumps(sarif, indent=2), encoding='utf-8')
    return path
```
