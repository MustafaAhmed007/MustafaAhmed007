# Contributing

Thanks for improving the Developer Command Center.

## Development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest
```

Generate the checked-in assets:

```bash
python generator.py
```

Validate the generated SVGs without rewriting files:

```bash
python generator.py --validate
```

Run tests:

```bash
pytest -q
```

## Change policy

- Keep generated output reproducible.
- Do not add secrets or private credentials.
- Do not invent metrics, clients, achievements, or proof-of-work.
- Keep README auto-generated content between its existing markers.
- Add regression coverage for generator behavior that changes.

## Pull requests

Describe the user-facing improvement, the files changed, and how you validated it. Generated asset changes should include the source/config change that produced them.
