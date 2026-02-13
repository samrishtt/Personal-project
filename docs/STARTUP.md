# 🚀 SynapseForge - Startup Guide

## Prerequisites
- Python 3.10+
- pip (Python package manager)

---

## Installation & Setup

### Step 1: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 2: Activate Virtual Environment
**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Application

### Option A: Web UI (Flask Server)
**Using batch file (Windows):**
```bash
.\run_web.bat
```

**Or manually:**
```bash
python server.py
```

Navigate to: **http://localhost:5000**

---

## Testing

### Run Full Feature Tests
```bash
python test_v3_features.py
```

### Run API Tests
```bash
python test_api.py
```

### Run Synthesis Integration Test
```bash
python test_synthesis.py
```

---

## Project Structure

| File/Folder | Purpose |
|------------|---------|
| `server.py` | Flask REST API server |
| `app.py` | Web UI application |
| `debate_app/` | Core debate & reasoning engine |
| `debate_app/v3_core.py` | v3 research-grade features |
| `debate_app/v3_prompts.py` | v3 system prompts |
| `debate_app/agents/` | Agent providers (OpenAI, Google, Anthropic) |
| `debate_app/core/` | Core modules (prompts, pricing, base classes) |
| `static/` | CSS & JavaScript for web UI |
| `templates/` | HTML templates |
| `requirements.txt` | Python dependencies |

---

## API Endpoints

### Health Check
```
GET /api/health
```

### List Available Models
```
GET /api/models
```

### Run Debate/Synthesis
```
POST /api/run
Body: { "query": "Your query here", "num_agents": 5 }
```

---

## Key Features

✅ **Parallel Agent Execution** — 10 concurrent workers  
✅ **Multi-Provider Support** — OpenAI GPT-4, Google Gemini, Anthropic Claude  
✅ **Query Classification** — Auto-detects FACTUAL, CAUSAL, ETHICAL, CREATIVE  
✅ **Credence Tracking** — Bayesian confidence updates  
✅ **Context Pruning** — Smart claim filtering (400 tokens max)  
✅ **Real-time Streaming** — WebSocket event system  
✅ **Research-grade Output** — JSON with benchmarks  

---

## Troubleshooting

### ModuleNotFoundError
Make sure virtual environment is activated:
```bash
python --version  # Should show 3.10+
```

### Port 5000 Already in Use
Change port in `server.py`:
```python
if __name__ == '__main__':
    app.run(debug=False, port=8080)  # Change port here
```

### API Key Errors
Set environment variables for LLM providers:
```bash
$env:OPENAI_API_KEY = "your-key-here"
$env:GOOGLE_API_KEY = "your-key-here"
$env:ANTHROPIC_API_KEY = "your-key-here"
```

---

## Performance Notes

- **Parallel Execution**: 5 agents × 2 rounds = **~2.1 seconds** (vs 10+ sequential)
- **Throughput**: Handles 5-10 models concurrently ✅
- **Credence Updates**: Real-time Bayesian confidence tracking ✅

---

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Start server: `python server.py`
3. Open browser: `http://localhost:5000`
4. Run tests: `python test_v3_features.py`
5. Check API: Visit `/api/health`

---

Happy debating! 🎯
