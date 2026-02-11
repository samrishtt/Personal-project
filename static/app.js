// SynapseForge — Frontend Logic
// ──────────────────────────────

const MODEL_CATALOG = [
    { label: "OpenAI GPT-4o", provider: "openai", model_id: "gpt-4o", roles: ["debater", "judge", "fact_checker", "adversarial"] },
    { label: "OpenAI GPT-4o mini", provider: "openai", model_id: "gpt-4o-mini", roles: ["debater", "fact_checker", "adversarial"] },
    { label: "OpenAI GPT-3.5 Turbo", provider: "openai", model_id: "gpt-3.5-turbo", roles: ["debater"] },
    { label: "Google Gemini 1.5 Pro", provider: "google", model_id: "gemini-1.5-pro", roles: ["debater", "judge", "fact_checker", "adversarial"] },
    { label: "Google Gemini 1.5 Flash", provider: "google", model_id: "gemini-1.5-flash", roles: ["debater", "fact_checker", "adversarial"] },
    { label: "Anthropic Claude 3 Opus", provider: "anthropic", model_id: "claude-3-opus-20240229", roles: ["debater", "judge", "fact_checker", "adversarial"] },
    { label: "Anthropic Claude 3 Haiku", provider: "anthropic", model_id: "claude-3-haiku-20240307", roles: ["debater", "fact_checker", "adversarial"] },
    { label: "Mock Skeptic", provider: "mock", model_id: "mock-skeptic", roles: ["debater"] },
    { label: "Mock Optimist", provider: "mock", model_id: "mock-optimist", roles: ["debater"] },
    { label: "Mock Fact Checker", provider: "mock", model_id: "mock-fact-checker", roles: ["fact_checker"] },
    { label: "Mock Challenger", provider: "mock", model_id: "mock-adversarial", roles: ["adversarial"] },
    { label: "Mock Judge", provider: "mock", model_id: "mock-judge", roles: ["judge"] },
];

const PRESETS = {
    Balanced: { debaters: ["OpenAI GPT-4o mini", "Google Gemini 1.5 Flash"], judge: "OpenAI GPT-4o", fact: "", adv: "" },
    Rigorous: { debaters: ["OpenAI GPT-4o", "Anthropic Claude 3 Opus", "Google Gemini 1.5 Pro"], judge: "OpenAI GPT-4o", fact: "Anthropic Claude 3 Haiku", adv: "OpenAI GPT-4o mini" },
    Demo: { debaters: ["Mock Skeptic", "Mock Optimist"], judge: "Mock Judge", fact: "Mock Fact Checker", adv: "Mock Challenger" },
};

let selectedDebaters = new Set();
let lastRun = null;

// ─── Init ───
document.addEventListener("DOMContentLoaded", () => {
    buildModelChips();
    buildRoleSelects();
    bindEvents();
    applyPreset("Demo");
    updateUI();
});

// ─── Model Chips ───
function buildModelChips() {
    const container = document.getElementById("model-chips");
    container.innerHTML = "";
    MODEL_CATALOG.filter(m => m.roles.includes("debater")).forEach(m => {
        const chip = document.createElement("div");
        chip.className = "model-chip";
        chip.dataset.label = m.label;
        chip.innerHTML = `<span class="provider-dot provider-${m.provider}"></span>${m.label}`;
        chip.addEventListener("click", () => {
            if (selectedDebaters.has(m.label)) selectedDebaters.delete(m.label);
            else selectedDebaters.add(m.label);
            updateUI();
        });
        container.appendChild(chip);
    });
}

function buildRoleSelects() {
    const judgeEl = document.getElementById("select-judge");
    const factEl = document.getElementById("select-fact");
    const advEl = document.getElementById("select-adversarial");
    judgeEl.innerHTML = "";
    factEl.innerHTML = '<option value="">None</option>';
    advEl.innerHTML = '<option value="">None</option>';
    MODEL_CATALOG.forEach(m => {
        if (m.roles.includes("judge")) judgeEl.innerHTML += `<option value="${m.label}">${m.label}</option>`;
        if (m.roles.includes("fact_checker")) factEl.innerHTML += `<option value="${m.label}">${m.label}</option>`;
        if (m.roles.includes("adversarial")) advEl.innerHTML += `<option value="${m.label}">${m.label}</option>`;
    });
}

// ─── Events ───
function bindEvents() {
    // Tabs
    document.querySelectorAll(".nav-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById("tab-" + tab.dataset.tab).classList.add("active");
        });
    });

    // API key inputs
    document.querySelectorAll(".key-input").forEach(inp => {
        inp.addEventListener("input", () => updateKeyStatus());
    });

    // Sliders
    document.getElementById("cfg-rounds").addEventListener("input", e => { document.getElementById("val-rounds").textContent = e.target.value; updateUI(); });
    document.getElementById("cfg-budget").addEventListener("input", e => { document.getElementById("val-budget").textContent = "$" + (e.target.value / 100).toFixed(2); });
    document.getElementById("cfg-temp").addEventListener("input", e => { document.getElementById("val-temp").textContent = (e.target.value / 100).toFixed(2); });
    document.getElementById("cfg-consensus").addEventListener("input", e => { document.getElementById("val-consensus").textContent = e.target.value + "%"; });

    // Preset
    document.getElementById("preset-select").addEventListener("change", e => { applyPreset(e.target.value); updateUI(); });

    // Query
    document.getElementById("query-input").addEventListener("input", () => updateUI());

    // Role selects
    ["select-judge", "select-fact", "select-adversarial"].forEach(id => {
        document.getElementById(id).addEventListener("change", () => updateUI());
    });

    // Run button
    document.getElementById("btn-run").addEventListener("click", runSynthesis);
    document.getElementById("btn-clear").addEventListener("click", clearResults);
}

function updateKeyStatus() {
    ["openai", "google", "anthropic"].forEach(p => {
        const val = document.getElementById("key-" + p).value.trim();
        const el = document.getElementById("status-" + p);
        if (val) { el.textContent = "Ready"; el.className = "key-status ready"; }
        else { el.textContent = "Missing"; el.className = "key-status missing"; }
    });
    updateUI();
}

// ─── Preset ───
function applyPreset(name) {
    const p = PRESETS[name];
    if (!p) return;
    selectedDebaters = new Set(p.debaters);
    document.getElementById("select-judge").value = p.judge;
    document.getElementById("select-fact").value = p.fact;
    document.getElementById("select-adversarial").value = p.adv;
    document.getElementById("preset-select").value = name;
    updateUI();
}

// ─── UI Sync ───
function updateUI() {
    // Chip highlight
    document.querySelectorAll(".model-chip").forEach(c => {
        c.classList.toggle("selected", selectedDebaters.has(c.dataset.label));
    });

    // Metrics
    const judge = document.getElementById("select-judge").value;
    const fact = document.getElementById("select-fact").value;
    const adv = document.getElementById("select-adversarial").value;
    const teamSize = selectedDebaters.size + (judge ? 1 : 0) + (fact ? 1 : 0) + (adv ? 1 : 0);
    const providers = new Set();
    [...selectedDebaters, judge, fact, adv].forEach(label => {
        const m = MODEL_CATALOG.find(x => x.label === label);
        if (m) providers.add(m.provider);
    });
    document.getElementById("m-lineup").textContent = teamSize;
    document.getElementById("m-models").textContent = selectedDebaters.size;
    document.getElementById("m-providers").textContent = providers.size;
    document.getElementById("m-rounds").textContent = document.getElementById("cfg-rounds").value;

    // Run button
    const query = document.getElementById("query-input").value.trim();
    const needsKeys = getRequiredKeys();
    const missingKeys = needsKeys.filter(p => !document.getElementById("key-" + p).value.trim());
    const canRun = query && selectedDebaters.size >= 1 && judge && missingKeys.length === 0;
    document.getElementById("btn-run").disabled = !canRun;
}

function getRequiredKeys() {
    const allLabels = [...selectedDebaters, document.getElementById("select-judge").value, document.getElementById("select-fact").value, document.getElementById("select-adversarial").value];
    const providers = new Set();
    allLabels.forEach(label => {
        const m = MODEL_CATALOG.find(x => x.label === label);
        if (m && m.provider !== "mock") providers.add(m.provider);
    });
    return [...providers];
}

// ─── Run Synthesis ───
async function runSynthesis() {
    const loading = document.getElementById("loading");
    const loadingText = document.getElementById("loading-text");
    loading.style.display = "flex";

    const payload = {
        query: document.getElementById("query-input").value.trim(),
        debaters: [...selectedDebaters],
        judge: document.getElementById("select-judge").value,
        fact_checker: document.getElementById("select-fact").value || null,
        adversarial: document.getElementById("select-adversarial").value || null,
        rounds: parseInt(document.getElementById("cfg-rounds").value),
        budget: parseInt(document.getElementById("cfg-budget").value) / 100,
        temp: parseInt(document.getElementById("cfg-temp").value) / 100,
        consensus_threshold: parseInt(document.getElementById("cfg-consensus").value) / 100,
        keys: {
            openai: document.getElementById("key-openai").value.trim(),
            google: document.getElementById("key-google").value.trim(),
            anthropic: document.getElementById("key-anthropic").value.trim(),
        }
    };

    try {
        loadingText.textContent = "Models collaborating...";
        const resp = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!resp.ok) throw new Error("Server error: " + resp.status);
        lastRun = await resp.json();
        renderResults(lastRun);
        renderFeed(lastRun);
        renderAnalytics(lastRun);
    } catch (err) {
        alert("Synthesis failed: " + err.message);
    } finally {
        loading.style.display = "none";
    }
}

function clearResults() {
    lastRun = null;
    document.getElementById("results-area").style.display = "none";
    document.getElementById("btn-clear").style.display = "none";
    document.getElementById("feed-empty").style.display = "block";
    document.getElementById("feed-content").style.display = "none";
    document.getElementById("analytics-empty").style.display = "block";
    document.getElementById("analytics-content").style.display = "none";
}

// ─── Render Studio Results ───
function renderResults(run) {
    const area = document.getElementById("results-area");
    area.style.display = "block";
    document.getElementById("btn-clear").style.display = "block";

    const metricsHtml = `
    <div class="metric-card"><div class="metric-value">${run.rounds_completed}/${run.rounds_requested}</div><div class="metric-label">Rounds</div></div>
    <div class="metric-card"><div class="metric-value">$${(run.total_cost || 0).toFixed(4)}</div><div class="metric-label">Total Cost</div></div>
    <div class="metric-card"><div class="metric-value">${run.warnings?.length || 0}</div><div class="metric-label">Warnings</div></div>
    <div class="metric-card"><div class="metric-value">${run.stopped_reason?.includes("consensus") ? "✅" : "⚡"}</div><div class="metric-label">Status</div></div>
  `;
    document.getElementById("result-metrics").innerHTML = metricsHtml;
    document.getElementById("synthesis-body").textContent = run.final_answer || "No synthesis generated.";

    // Auto scroll
    area.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ─── Render Feed ───
function renderFeed(run) {
    document.getElementById("feed-empty").style.display = "none";
    const container = document.getElementById("feed-content");
    container.style.display = "block";
    container.innerHTML = "";

    (run.rounds || []).forEach(round => {
        const roundDiv = document.createElement("div");
        roundDiv.className = "section";
        const consensus = ((round.consensus || 0) * 100).toFixed(0);
        roundDiv.innerHTML = `
      <div class="round-header" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'block':'none'">
        <span style="font-weight:600">Round ${round.round}</span>
        <div style="display:flex;gap:12px">
          <span class="round-badge badge-amber">Cost: $${(round.round_cost || 0).toFixed(5)}</span>
          <span class="round-badge badge-green">Consensus: ${consensus}%</span>
        </div>
      </div>
      <div class="round-responses"></div>
    `;
        const respContainer = roundDiv.querySelector(".round-responses");
        (round.responses || []).forEach(r => {
            respContainer.innerHTML += buildResponseCard(r);
        });
        container.appendChild(roundDiv);
    });

    if (run.judge) {
        container.innerHTML += `
      <div class="section">
        <div class="section-title"><span class="icon">⚖️</span> Synthesis Engine Output</div>
        ${buildResponseCard(run.judge)}
      </div>`;
    }
}

function buildResponseCard(r) {
    const confPct = ((r.confidence || 0) * 100).toFixed(0);
    return `
    <div class="response-card">
      <div class="response-header">
        <div class="response-agent">
          <span class="provider-dot provider-${(r.provider || '').toLowerCase().replace(/\s/g, '')}"></span>
          ${r.agent || "Agent"}
        </div>
        <div class="response-meta">
          <span>${r.role || ""}</span>
          <span>${r.model || ""}</span>
          <span>Conf: ${confPct}%</span>
          <span>$${(r.cost || 0).toFixed(5)}</span>
        </div>
      </div>
      <div class="response-body">${escapeHtml(r.content || "")}</div>
    </div>
  `;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ─── Render Analytics ───
function renderAnalytics(run) {
    document.getElementById("analytics-empty").style.display = "none";
    const container = document.getElementById("analytics-content");
    container.style.display = "block";

    const allResponses = [];
    (run.rounds || []).forEach(rd => (rd.responses || []).forEach(r => allResponses.push(r)));
    if (run.judge) allResponses.push(run.judge);

    const totalTokens = allResponses.reduce((s, r) => s + (r.tokens_total || 0), 0);
    const avgConf = allResponses.length ? (allResponses.reduce((s, r) => s + (r.confidence || 0), 0) / allResponses.length * 100).toFixed(1) : "0";
    const agents = new Set(allResponses.map(r => r.agent));

    // Cost per round data
    const roundCosts = (run.rounds || []).map(rd => ({ round: rd.round, cost: rd.round_cost || 0, consensus: ((rd.consensus || 0) * 100).toFixed(0) }));

    // Provider cost breakdown
    const providerCosts = {};
    allResponses.forEach(r => {
        const p = r.provider || "Unknown";
        providerCosts[p] = (providerCosts[p] || 0) + (r.cost || 0);
    });

    // Token breakdown per agent
    const agentTokens = {};
    allResponses.forEach(r => {
        const a = r.agent || "Unknown";
        agentTokens[a] = (agentTokens[a] || 0) + (r.tokens_total || 0);
    });

    container.innerHTML = `
    <div class="grid-4" style="margin-bottom:24px">
      <div class="metric-card"><div class="metric-value">$${(run.total_cost || 0).toFixed(4)}</div><div class="metric-label">Total Cost</div></div>
      <div class="metric-card"><div class="metric-value">${totalTokens.toLocaleString()}</div><div class="metric-label">Total Tokens</div></div>
      <div class="metric-card"><div class="metric-value">${avgConf}%</div><div class="metric-label">Avg Confidence</div></div>
      <div class="metric-card"><div class="metric-value">${agents.size}</div><div class="metric-label">Agents</div></div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title" style="margin-bottom:12px"><span class="icon">📈</span> Cost per Round</div>
        <canvas id="chart-cost" height="220"></canvas>
      </div>
      <div class="card">
        <div class="card-title" style="margin-bottom:12px"><span class="icon">🎯</span> Consensus Trajectory</div>
        <canvas id="chart-consensus" height="220"></canvas>
      </div>
    </div>
    <div class="grid-2" style="margin-top:20px">
      <div class="card">
        <div class="card-title" style="margin-bottom:12px"><span class="icon">🔤</span> Tokens by Agent</div>
        <canvas id="chart-tokens" height="220"></canvas>
      </div>
      <div class="card">
        <div class="card-title" style="margin-bottom:12px"><span class="icon">💰</span> Cost by Provider</div>
        <canvas id="chart-provider" height="220"></canvas>
      </div>
    </div>
  `;

    drawCharts(roundCosts, agentTokens, providerCosts);
}

// Simple Canvas Charts
function drawCharts(roundCosts, agentTokens, providerCosts) {
    drawLineChart("chart-cost", roundCosts.map(r => r.round), roundCosts.map(r => r.cost), "Cost ($)", "#6366f1");
    drawLineChart("chart-consensus", roundCosts.map(r => r.round), roundCosts.map(r => +r.consensus), "Consensus %", "#10b981");
    drawBarChart("chart-tokens", Object.keys(agentTokens), Object.values(agentTokens));
    drawPieChart("chart-provider", Object.keys(providerCosts), Object.values(providerCosts));
}

function drawLineChart(id, labels, data, ylabel, color) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width = canvas.clientWidth * 2;
    const H = canvas.height = canvas.clientHeight * 2;
    ctx.scale(2, 2);
    const w = W / 2, h = H / 2;
    const pad = { t: 20, r: 20, b: 30, l: 50 };
    const plotW = w - pad.l - pad.r, plotH = h - pad.t - pad.b;

    const maxVal = Math.max(...data, 0.001);
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = pad.t + (plotH * i / 4);
        ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l + plotW, y); ctx.stroke();
        ctx.fillStyle = "#64748b"; ctx.font = "10px Inter";
        ctx.textAlign = "right";
        ctx.fillText((maxVal * (1 - i / 4)).toFixed(maxVal < 1 ? 4 : 0), pad.l - 6, y + 3);
    }

    if (data.length < 2) return;
    const grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + plotH);
    grad.addColorStop(0, color + "40"); grad.addColorStop(1, color + "00");

    ctx.beginPath();
    data.forEach((v, i) => {
        const x = pad.l + (i / (data.length - 1)) * plotW;
        const y = pad.t + plotH - (v / maxVal) * plotH;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    const lastX = pad.l + plotW, lastY = pad.t + plotH;
    ctx.lineTo(lastX, lastY); ctx.lineTo(pad.l, lastY); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();

    ctx.beginPath();
    data.forEach((v, i) => {
        const x = pad.l + (i / (data.length - 1)) * plotW;
        const y = pad.t + plotH - (v / maxVal) * plotH;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();

    data.forEach((v, i) => {
        const x = pad.l + (i / (data.length - 1)) * plotW;
        const y = pad.t + plotH - (v / maxVal) * plotH;
        ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = color; ctx.fill();
        ctx.fillStyle = "#94a3b8"; ctx.font = "10px Inter"; ctx.textAlign = "center";
        ctx.fillText("R" + labels[i], x, h - 8);
    });
}

function drawBarChart(id, labels, data) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width = canvas.clientWidth * 2;
    const H = canvas.height = canvas.clientHeight * 2;
    ctx.scale(2, 2);
    const w = W / 2, h = H / 2;
    const pad = { t: 20, r: 20, b: 40, l: 50 };
    const plotW = w - pad.l - pad.r, plotH = h - pad.t - pad.b;
    const maxVal = Math.max(...data, 1);
    const colors = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e", "#a855f7"];
    const barW = Math.min(plotW / data.length * 0.6, 40);

    data.forEach((v, i) => {
        const x = pad.l + (i + 0.5) * (plotW / data.length) - barW / 2;
        const barH = (v / maxVal) * plotH;
        const y = pad.t + plotH - barH;
        const grad = ctx.createLinearGradient(0, y, 0, y + barH);
        grad.addColorStop(0, colors[i % colors.length]); grad.addColorStop(1, colors[i % colors.length] + "60");
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(x, y, barW, barH, 4);
        ctx.fill();
        ctx.fillStyle = "#94a3b8"; ctx.font = "9px Inter"; ctx.textAlign = "center";
        const short = labels[i].length > 10 ? labels[i].slice(0, 10) + "…" : labels[i];
        ctx.fillText(short, x + barW / 2, h - 8);
    });
}

function drawPieChart(id, labels, data) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width = canvas.clientWidth * 2;
    const H = canvas.height = canvas.clientHeight * 2;
    ctx.scale(2, 2);
    const w = W / 2, h = H / 2;
    const cx = w * 0.4, cy = h / 2, r = Math.min(w, h) * 0.35;
    const total = data.reduce((s, v) => s + v, 0) || 1;
    const colors = ["#6366f1", "#f59e0b", "#f43f5e", "#10b981", "#06b6d4", "#8b5cf6"];
    let angle = -Math.PI / 2;
    data.forEach((v, i) => {
        const slice = (v / total) * Math.PI * 2;
        ctx.beginPath(); ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, r, angle, angle + slice);
        ctx.closePath(); ctx.fillStyle = colors[i % colors.length]; ctx.fill();
        angle += slice;
    });
    // Center hole
    ctx.beginPath(); ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
    ctx.fillStyle = "#111827"; ctx.fill();

    // Legend
    labels.forEach((l, i) => {
        const y = 30 + i * 22;
        ctx.fillStyle = colors[i % colors.length];
        ctx.fillRect(w * 0.72, y, 10, 10);
        ctx.fillStyle = "#94a3b8"; ctx.font = "11px Inter"; ctx.textAlign = "left";
        ctx.fillText(`${l}: $${data[i].toFixed(4)}`, w * 0.72 + 16, y + 9);
    });
}
