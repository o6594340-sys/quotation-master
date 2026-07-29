# Quotation Generator for Agencies

A lightweight MVP for building quotation estimates from multiple supplier offers for MICE agencies.

## What this MVP includes

- upload multiple source files and select a strategy
- choose the output language:
  - keep the quote in English
  - generate a polished Russian version
- preview the generated estimate in the UI
- track job status through processing stages
- download simple JSON and CSV exports

## Project structure

- backend/app/main.py — HTTP API entry point
- backend/app/services/quotation_service.py — job orchestration and state
- backend/app/services/estimate_builder.py — generate a simple estimate preview
- backend/app/services/export_service.py — create JSON/CSV export files
- frontend/index.html — UI shell
- frontend/app.js — client-side request handling and preview rendering
- frontend/styles.css — basic styling
- tests/ — regression tests for the core service logic

## Run locally

1. Install Python dependencies if needed:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Start the backend:
   ```bash
   python backend/app/main.py
   ```
3. Open the frontend in a browser:
   - open [frontend/index.html](frontend/index.html)
4. Create a job and choose the desired output language.

## API

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Create a job

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"sources":["quote1.pdf"],"strategy":"lowest_price","output_language":"translate_russian"}'
```

## GitHub publishing

To publish this repository to GitHub:

```bash
git remote remove origin
git remote add origin git@github.com:<your-username>/<your-repo-name>.git
git push -u origin master
```

## Status

This project is an MVP and is intended as the foundation for future parsing, matching, and richer quotation workflows.
