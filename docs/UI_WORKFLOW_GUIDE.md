# 🎯 SynapseForge UI — Simplified Workflow Guide

## Overview

Your SynapseForge interface now has:
- ✅ **Smooth animated background** (floating particles + gradient orbs)
- ✅ **Cost calculator** (shows API costs for 10-model participation)
- ✅ **Full debate studio** (API keys, model selection, query input, results)
- ✅ **Three tabs** (Studio, Synthesis Feed, Analytics)

**Project selection cards removed** — Focus on core functionality.

---

## 🎨 UI Layout

```
┌─────────────────────────────────────┐
│   🎬 Animated Background            │
│   (Floating particles + orbs)       │
│                                     │
│  ⚡ SynapseForge (Hero Header)      │
│                                     │
│  💰 Cost Calculator Panel           │
│  ├─ Premium: $2.50                  │
│  ├─ Mid-Tier: $1.20                 │
│  ├─ Fast: $0.30                     │
│  └─ TOTAL: $4.00 (3 rounds)         │
│                                     │
│  [⚡ Studio][📜 Feed][📊 Analytics] │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ LEFT (Config)   │ RIGHT      │    │
│  ├─────────────────┤ (Input)    │    │
│  │ 🔑 API Keys     │            │    │
│  │ ⚙️ Config       │ 🤖 Models  │    │
│  │                 │            │    │
│  │ Sliders:        │ 💬 Query   │    │
│  │ • Rounds        │            │    │
│  │ • Budget        │ [Launch]   │    │
│  │ • Temperature   │            │    │
│  │ • Consensus     │            │    │
│  └─────────────────────────────┘    │
│                                     │
│  [Results Area - Synthesis]         │
│                                     │
└─────────────────────────────────────┘
```

---

## 🚀 How to Use (Step-by-Step)

### **Step 1: Set API Keys** (Left Panel)

Enter your API credentials:
```
🔑 OpenAI:     sk-...
🔑 Google:     AIza...
🔑 Anthropic:  sk-ant-...
```

**Status Indicators:**
- 🟢 Green = Ready
- 🔴 Red = Missing

---

### **Step 2: Configure Synthesis** (Left Panel)

Adjust these sliders:

| Slider | Range | Default | What It Does |
|--------|-------|---------|--------------|
| **Collaboration Rounds** | 1-8 | 3 | How many debate rounds agents participate |
| **Budget Cap** | $0.05-$10 | $0.75 | Max API cost allowed |
| **Temperature** | 0.00-1.00 | 0.20 | Creativity (0=focused, 1=random) |
| **Consensus Threshold** | 20%-90% | 55% | When to stop early if agents agree |

**Cost Updates Automatically:**
- Change rounds → Total cost updates instantly
- 3 rounds: $4.00
- 5 rounds: $6.67
- 8 rounds: $10.67

---

### **Step 3: Select Models** (Right Panel)

**Three ways to choose:**

#### **Option A: Quick Presets**
```
⚖️ Balanced    → 2 debaters, cheap & fast
🔬 Rigorous    → 3 debaters, high quality
🎭 Demo        → Mock agents (free, no API keys)
```

#### **Option B: Manual Selection**
Click model chips to add/remove:
```
🟢 OpenAI GPT-4o
🟡 Google Gemini 1.5 Pro
🔴 Claude 3 Opus
```

#### **Option C: Role-Based Selection**
Assign specific models to roles:
- **Judge/Synthesizer** → synthesis quality
- **Verification Agent** → fact-checking
- **Stress-Test Agent** → contradict weak arguments

---

### **Step 4: Enter Your Query**

Write your research question:
```
📌 Example:
"What are the most promising approaches to AGI safety, 
and how should research priorities be allocated?"
```

**Metrics Update Automatically:**
- Team Size: 5 agents
- Models: 3 unique models
- Providers: 3 (OpenAI, Google, Anthropic)
- Rounds: 3

---

### **Step 5: Launch Synthesis**

Click: **⚡ Launch Collaborative Synthesis**

**What happens:**
1. 🔄 All models run in **parallel** (not sequential)
2. 💬 Each agent generates a response
3. ✅ Verifier checks claims
4. 🎯 Consensus detection stops early if possible
5. 📊 Final synthesis combines best insights

**Estimated Time:** 2-5 seconds (depending on rounds)

---

## 💡 Cost Calculator Explained

Your UI shows **estimated costs for 10 simultaneous models**:

```
┌──────────────────────────────────────────┐
│        Cost Breakdown (Per Round)         │
├──────────────────────────────────────────┤
│ Premium Models                    $2.50  │
│ • OpenAI GPT-4o                          │
│ • Anthropic Claude 3 Opus                │
│                                          │
│ Mid-Tier Models                   $1.20  │
│ • OpenAI GPT-4o Mini                     │
│ • Google Gemini 1.5 Pro                  │
│                                          │
│ Fast Models                       $0.30  │
│ • Google Gemini Flash                    │
│ • Anthropic Claude Haiku                 │
│                                          │
├──────────────────────────────────────────┤
│ TOTAL (1 round)               $4.00     │
│ TOTAL (3 rounds)              $12.00    │
│ TOTAL (5 rounds)              $20.00    │
└──────────────────────────────────────────┘
```

**How costs are calculated:**
```
Cost = (Input Tokens / 1M) × Input Price
     + (Output Tokens / 1M) × Output Price
```

---

## 📊 Results Tab (After Synthesis)

After launching, you'll see:

### **Synthesis Panel**
```
⚡ SynapseForge — Collaborative Synthesis

Metrics:
├─ Execution Time: 2.1s
├─ Models Used: 5
├─ Total Cost: $0.47
└─ Consensus Reached: Yes

Final Answer:
The most promising approaches are...
[Full synthesized response with credence tracking]
```

### **Feed Tab** (Collaboration Trace)
See all agent responses in order:
```
Round 1:
├─ Skeptic: "ML needs large datasets..."
├─ Optimist: "Transfer learning reduces data..."
└─ Verifier: "Both valid, credence: 0.78"

Round 2:
├─ Challenger: "Counter-examples show..."
└─ Judge: "Synthesized view..."
```

### **Analytics Tab** (Performance Metrics)
```
Execution Timeline:     [=====>] 2.1s
Model Distribution:    ◉ OpenAI ◉ Google ◉ Anthropic
Cost Comparison:       Single-agent: $0.89 | Multi: $0.47
Consensus Score:       87% (High agreement)
```

---

## ⚙️ Advanced Configuration

### **Temperature Tuning**
```
Temperature = 0.20  → Focused, deterministic responses
                        Good for factual questions

Temperature = 0.50  → Balanced
                        Good for most queries

Temperature = 0.80  → Creative, exploratory
                        Good for brainstorming
```

### **Budget Management**
```
Budget = $0.75   → Single round with fast models
Budget = $5.00   → Multiple rounds with mix
Budget = $20.00  → Rigorous 5-round with premium models
```

### **Consensus Threshold**
```
Threshold = 55%  → Stop when narrow consensus
Threshold = 75%  → Need strong agreement
Threshold = 85%  → Only stop on near-unanimity
```

---

## 🎯 Quick Use Cases

### **Academic Research (MIT Project)**
```
Models: 5-7
Rounds: 3-4
Budget: $2.00
Config: Rigorous preset + high consensus threshold
Example Query: "Analyze the limitations of this thesis..."
```

### **AI Safety Research**
```
Models: 8-10
Rounds: 4-5
Budget: $5.00
Config: Rigorous preset + stress-test agent
Example Query: "What are failure modes of this alignment approach?"
```

### **Quick Analysis**
```
Models: 2-3
Rounds: 1-2
Budget: $0.50
Config: Demo preset or balanced
Example Query: "Summarize the key insights from this paper"
```

---

## 🔧 Flow Diagram

```
START
  ↓
[Enter API Keys] → Status: 🔴 Missing → ❌ Can't run
  ↓
[Adjust Sliders] → Cost updates automatically
  ↓
[Select Models] → Metrics update (team size, providers)
  ↓
[Enter Query]
  ↓
[Click Launch]
  ↓
🔄 Parallel Execution (ThreadPoolExecutor, 10 workers)
  ├─ Round 1: All agents generate responses
  ├─ Verifier: Check claims, update credence
  ├─ Consensus: If threshold met, STOP
  └─ Round 2+: Continue if needed
  ↓
✅ Synthesis Complete
  ├─ Results: Final synthesized answer
  ├─ Feed: Trace of all agent interactions
  └─ Analytics: Performance metrics
  ↓
END
```

---

## 🌟 Animation Details

### **Background Motion**
- **5 floating particles** drift smoothly for 20-25 seconds
- **3 gradient orbs** scale and move for 28-35 seconds
- **Non-blocking** — doesn't interfere with interactions
- **Colors matched** to Indigo/Violet/Cyan theme

### **Interactive Animations**
- **Model chips** glow when selected
- **Sliders** smoothly update cost in real-time
- **Button hover** lifts with shadow
- **Results appear** with fade-in animation

---

## 💾 Data Persistence

Your browser saves:
- API key status (not the actual keys)
- Last used preset
- Previous queries (local storage)

**Security:** API keys never sent to server until explicitly used.

---

## 🚀 Common Workflows

### **Workflow 1: Quick Fact-Check**
```
1. Use Demo preset (free)
2. Lower rounds to 1
3. Ask focused question
4. Get instant results
Time: <10s | Cost: $0.00
```

### **Workflow 2: Rigorous Research**
```
1. Use Rigorous preset
2. Set rounds to 4
3. Increase budget to $5
4. Ask complex question
5. Review feed & analytics
Time: 5-10s | Cost: $1.50-2.50
```

### **Workflow 3: Custom Configuration**
```
1. Manually select models
2. Assign specific roles
3. Tune temperature & consensus
4. Monitor cost calculator
5. Launch when ready
Time: Flexible | Cost: Controlled
```

---

## ❓ FAQ

**Q: Can I use mock agents to test?**
A: Yes! Use the Demo preset → free, no API keys needed

**Q: How long does a synthesis take?**
A: ~2 seconds for 5 agents × 2 rounds (parallel execution)

**Q: Can I stop early if consensus is reached?**
A: Yes! Set high consensus threshold → stops after round 1

**Q: What if I run out of budget?**
A: Synthesis stops when budget cap is hit → saves money

**Q: Can I see all agent responses?**
A: Yes! Check the "Synthesis Feed" tab for full trace

**Q: How is cost calculated?**
A: Based on input/output tokens × model pricing per 1M tokens

---

## 📝 Pro Tips

💡 **Lower temperature for research** (0.15-0.30)
💡 **Higher temperature for brainstorming** (0.70-0.90)
💡 **Always use at least 1 skeptic model** (balanced view)
💡 **Use verification agent** (catches hallucinations)
💡 **Monitor cost calculator** (avoid surprise costs)
💡 **Start with Demo preset** (understand the flow)

---

Enjoy your marvelous SynapseForge UI! 🌟
