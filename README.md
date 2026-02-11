# SynapseForge — Multi-Model Collaborative Intelligence Engine

> **MIT Application Project** by Samrisht

SynapseForge fuses multiple AI models into a single collaborative intelligence engine. Unlike debate-style systems where models argue against each other, SynapseForge makes models **work together** — each contributing unique strengths to produce answers that are demonstrably superior to any single model.

## 🧠 Core Concept

Traditional multi-model systems pit AI models against each other in debate. SynapseForge takes a fundamentally different approach:

- **Collaborative, not competitive** — Models complement each other's knowledge
- **Specialized roles** — Contributors, Verifiers, Stress-Testers, and a final Synthesizer
- **Cross-validation** — Claims are verified across multiple models for reliability
- **Consensus detection** — Early convergence stops unnecessary rounds, saving cost
- **Provider-agnostic** — Integrate OpenAI, Google Gemini, Anthropic Claude, or any model with an API key

## ⚡ Quick Start

### Web Interface (Recommended)
```bash
pip install -r requirements.txt
python server.py
```
Then open **http://localhost:5000** in your browser.

### Streamlit Interface (Legacy)
```bash
streamlit run app.py
```

## 🔑 API Key Setup

Enter your API keys directly in the web interface, or create a `.env` file:
```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
```

## 🎭 Demo Mode

Don't have API keys? Select the **Demo** preset to use mock agents for a zero-cost demonstration of the platform.

## 🏗️ Architecture

```
SynapseForge/
├── server.py                    # Flask web server
├── app.py                       # Streamlit interface (legacy)
├── templates/index.html         # Modern web UI
├── static/
│   ├── styles.css               # Design system
│   └── app.js                   # Frontend logic
├── debate_app/
│   ├── agents/providers.py      # Multi-provider model agents
│   └── core/
│       ├── base.py              # Agent base classes
│       ├── prompts.py           # Collaborative system prompts
│       └── pricing.py           # Cost estimation
└── requirements.txt
```

## 🤖 Supported Models

| Provider | Models | Roles |
|----------|--------|-------|
| **OpenAI** | GPT-4o, GPT-4o mini, GPT-3.5 Turbo | Contributor, Judge, Verifier, Stress-Tester |
| **Google** | Gemini 1.5 Pro, Gemini 1.5 Flash | Contributor, Judge, Verifier, Stress-Tester |
| **Anthropic** | Claude 3 Opus, Claude 3 Haiku | Contributor, Judge, Verifier, Stress-Tester |
| **Mock** | Various mock agents | All roles (free demo) |

## 📊 Features

- **Studio** — Configure your model team, set budgets, and run collaborative synthesis
- **Synthesis Feed** — Real-time round-by-round transcript of model collaboration
- **Analytics** — Cost tracking, token usage, consensus trajectory, provider cost breakdown
- **Preset Configs** — Balanced, Rigorous, or Demo mode with one click
- **Export** — Download full run data as JSON

## 🔬 How It Works

1. **You ask a question** — Complex research queries work best
2. **Models collaborate** — Each model independently analyzes the question, then refines based on others' contributions
3. **Verification** — Optional verification agent cross-checks factual claims
4. **Stress-testing** — Optional adversarial agent tests edge cases
5. **Synthesis** — A judge model fuses all contributions into a single, superior answer
6. **Output** — You receive an answer that leverages the collective intelligence of multiple models

## 📈 Why Multi-Model Collaboration?

- **Reduces hallucination** — Cross-validation catches errors single models miss
- **Broader knowledge** — Different models have different training data strengths
- **Higher reliability** — Consensus-based answers are more trustworthy
- **Cost-efficient** — Early convergence detection prevents unnecessary API calls

---

*Built for MIT Application · 2026*
