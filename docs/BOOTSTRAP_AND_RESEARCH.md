# Bootstrap & Multi-Aspect Research

The Developer Command Center now ships two reusable operational capabilities: a one-click bootstrap path and an evidence-preserving research engine.

## 1. One-click installation

The bootstrap path creates an isolated virtual environment, installs pinned dependencies, installs the project in editable mode with tests, and runs the complete quality gate.

### Windows

Double-click `setup.bat`.

### macOS / Linux

Run:

```bash
./setup.sh
```

Or use the portable Python entry point:

```bash
python bootstrap.py
```

The bootstrap intentionally fails early on Python versions below 3.10 and surfaces the exact failing command instead of leaving users to debug a partially configured environment.

## 2. Multi-aspect auto-research

Research is deliberately layered:

```text
Topic
  ↓
Aspect plan
  ├─ landscape
  ├─ technical
  ├─ implementation
  ├─ positioning
  └─ discovery
  ↓
Local evidence + direct URLs
  ↓
Optional cloud enrichment
  ↓
Structured Markdown / JSON output
```

### Local research

```bash
python research.py "developer tooling" --local docs --local README.md
```

Directories are scanned recursively for Markdown, text, JSON, Python, TOML, YAML, and similar text sources.

### Direct-URL research

```bash
python research.py "GitHub profile optimization" \
  --url https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories
```

The URL layer is intentionally dependency-light and uses Python's standard library.

### Custom aspects

```bash
python research.py "AI developer tools" \
  --aspect landscape \
  --aspect technical \
  --aspect competitors
```

### Optional cloud research

Set `RESEARCH_CLOUD_ENDPOINT` or pass `--cloud-endpoint` to an HTTP endpoint that accepts:

```json
{"topic":"...","aspects":["..."]}
```

If `RESEARCH_CLOUD_TOKEN` is present, it is sent as a Bearer token. Cloud research is optional; local and direct-URL evidence continue to work without credentials or a cloud provider.

## Evidence policy

The engine preserves source kind, locator, title, content, and status. Cloud output is marked separately and is not treated as verified evidence by itself.

This keeps the system useful offline while preventing optional AI enrichment from silently becoming an unsupported claim.

## Architecture role

```text
Bootstrap → reliable execution environment
Research  → evidence acquisition
Generator → deterministic presentation
Validator → structural/safety verification
CI        → continuous regression control
```

Together these capabilities reduce setup friction, improve research coverage, and create a reusable foundation for future project/repository automation.
