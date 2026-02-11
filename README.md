# DebateMind Studio

DebateMind Studio is a Streamlit app that runs a structured multi-agent debate, then synthesizes a final answer with a judge model.

## What Changed
- Upgraded UI with a modern studio layout, richer live transcript, and analytics dashboard.
- Added provider key health checks (session keys + `.env` fallback).
- Added a centralized model catalog and custom model routing.
- Added cost-aware round execution with early-stop consensus logic.
- Replaced placeholder analytics with real token/cost/confidence charts.

## Quick Start
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Create `.env` (optional, you can also enter keys in sidebar):
```env
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
```
3. Run:
```bash
streamlit run app.py
```

## How To Use
1. Open `Studio` tab.
2. Enter a research question.
3. Choose a preset or manually configure debaters, judge, fact-checker, and adversarial agent.
4. Set rounds, budget, and early-stop threshold.
5. Run the debate and inspect live rounds, final synthesis, and analytics.

## Custom Model Access
In sidebar -> `Custom Models`, add one model per line:
```text
provider:model_id|Optional Label
```
Examples:
```text
openai:gpt-4.1-mini|OpenAI GPT 4.1 Mini
anthropic:claude-3-5-sonnet-latest
```

## Notes
- Mock agents can be used for a zero-cost demo.
- Cost estimates use the pricing table in `debate_app/core/pricing.py`.
- Models not listed in pricing still run, but estimated cost may show as `$0.000000`.
