// SynapseForge — Frontend Logic (V2 + SAM-AI Integration)
// ──────────────────────────────────────────────────────────

// ═════════════════════════════════════════════════════════════════
// 💰 COST CALCULATOR
// ═════════════════════════════════════════════════════════════════

function updateCostEstimate() {
  const costEstimates = { premium: 2.50, midtier: 1.20, fast: 0.30 };
  const rounds = parseInt(document.getElementById('cfg-rounds')?.value) || 3;
  const totalCost = (costEstimates.premium + costEstimates.midtier + costEstimates.fast) * rounds;
  const totalCostEl = document.getElementById('total-cost');
  const costDetail = document.querySelector('.cost-item.highlight .cost-detail');
  if (totalCostEl) totalCostEl.textContent = `$${totalCost.toFixed(2)}`;
  if (costDetail) costDetail.textContent = `For ${rounds} ${rounds === 1 ? 'round' : 'rounds'} of debate`;
}

// ═════════════════════════════════════════════════════════════════
// MODEL CATALOG & PRESETS
// ═════════════════════════════════════════════════════════════════

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
let samAiAvailable = false;

// ═════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═════════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
  buildModelChips();
  buildRoleSelects();
  bindEvents();
  applyPreset("Balanced");
  updateUI();
  checkSamAiStatus();
  updateCostEstimate();
});

// ─── Check SAM-AI Status ───
async function checkSamAiStatus() {
  const banner = document.getElementById("sam-status-banner");
  const icon = document.getElementById("sam-status-icon");
  const title = document.getElementById("sam-status-title");
  const detail = document.getElementById("sam-status-detail");

  try {
    const resp = await fetch("/api/health");
    const data = await resp.json();
    samAiAvailable = data.sam_ai_available;

    if (samAiAvailable) {
      banner.className = "sam-status-banner sam-available";
      icon.textContent = "🧠";
      title.textContent = "SAM-AI Engine Online";
      detail.textContent = "Neuro-symbolic analysis ready — truth levels & formal verification active";
    } else {
      banner.className = "sam-status-banner sam-unavailable";
      icon.textContent = "⚠️";
      title.textContent = "SAM-AI Engine Offline";
      detail.textContent = data.sam_ai_error || "SAM-AI module not loaded";
    }
  } catch (err) {
    banner.className = "sam-status-banner sam-unavailable";
    icon.textContent = "❌";
    title.textContent = "Server Connection Error";
    detail.textContent = "Cannot connect to SynapseForge server";
  }
}

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
  document.getElementById("cfg-rounds").addEventListener("input", e => {
    document.getElementById("val-rounds").textContent = e.target.value;
    updateCostEstimate();
    updateUI();
  });
  document.getElementById("cfg-budget").addEventListener("input", e => {
    document.getElementById("val-budget").textContent = "$" + (e.target.value / 100).toFixed(2);
  });
  document.getElementById("cfg-temp").addEventListener("input", e => {
    document.getElementById("val-temp").textContent = (e.target.value / 100).toFixed(2);
  });
  document.getElementById("cfg-consensus").addEventListener("input", e => {
    document.getElementById("val-consensus").textContent = e.target.value + "%";
  });

  // Preset
  document.getElementById("preset-select").addEventListener("change", e => {
    applyPreset(e.target.value);
    updateUI();
  });

  // Query
  document.getElementById("query-input").addEventListener("input", () => updateUI());

  // Role selects
  ["select-judge", "select-fact", "select-adversarial"].forEach(id => {
    document.getElementById(id).addEventListener("change", () => updateUI());
  });

  // Buttons
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

// ═════════════════════════════════════════════════════════════════
// RUN SYNTHESIS
// ═════════════════════════════════════════════════════════════════

async function runSynthesis() {
  const loading = document.getElementById("loading");
  const loadingText = document.getElementById("loading-text");
  const loadingSub = document.getElementById("loading-sub");
  loading.style.display = "flex";
  loadingText.textContent = "Models collaborating...";
  loadingSub.textContent = "Sending query to selected AI models";

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
    loadingText.textContent = "⚡ Running collaborative synthesis...";
    loadingSub.textContent = `${payload.debaters.length} models × ${payload.rounds} rounds`;
    const resp = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      throw new Error(errData.error || "Server error: " + resp.status);
    }

    lastRun = await resp.json();
    renderResults(lastRun);
    renderFeed(lastRun);
    renderAnalytics(lastRun);

    // Run SAM-AI analysis automatically
    if (lastRun.sam_ai_available && lastRun.final_answer) {
      loadingText.textContent = "🧠 Running SAM-AI analysis...";
      loadingSub.textContent = "Neuro-symbolic reasoning engine evaluating synthesis";
      await runSamAnalysis(lastRun);
    } else {
      renderSamUnavailable(lastRun);
    }
  } catch (err) {
    showToast("❌ " + err.message, "error");
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
  document.getElementById("sam-empty").style.display = "block";
  document.getElementById("sam-content").style.display = "none";
  document.getElementById("analytics-empty").style.display = "block";
  document.getElementById("analytics-content").style.display = "none";
}

// ═════════════════════════════════════════════════════════════════
// RENDER STUDIO RESULTS
// ═════════════════════════════════════════════════════════════════

function renderResults(run) {
  const area = document.getElementById("results-area");
  area.style.display = "block";
  document.getElementById("btn-clear").style.display = "block";

  const statusIcon = run.stopped_reason?.includes("consensus") ? "✅" : "⚡";
  const metricsHtml = `
    <div class="metric-card"><div class="metric-value">${run.rounds_completed}/${run.rounds_requested}</div><div class="metric-label">Rounds</div></div>
    <div class="metric-card"><div class="metric-value">$${(run.total_cost || 0).toFixed(4)}</div><div class="metric-label">Total Cost</div></div>
    <div class="metric-card"><div class="metric-value">${run.warnings?.length || 0}</div><div class="metric-label">Warnings</div></div>
    <div class="metric-card"><div class="metric-value">${statusIcon}</div><div class="metric-label">Status</div></div>
  `;
  document.getElementById("result-metrics").innerHTML = metricsHtml;

  // Render final answer with markdown-like formatting
  const bodyEl = document.getElementById("synthesis-body");
  bodyEl.innerHTML = formatContent(run.final_answer || "No synthesis generated.");

  // Warnings
  const warningsArea = document.getElementById("warnings-area");
  warningsArea.innerHTML = "";
  (run.warnings || []).forEach(w => {
    warningsArea.innerHTML += `<div class="warning-card">⚠️ ${escapeHtml(w)}</div>`;
  });

  area.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ═════════════════════════════════════════════════════════════════
// RENDER FEED
// ═════════════════════════════════════════════════════════════════

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
      <div class="round-header" onclick="this.nextElementSibling.classList.toggle('collapsed')">
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
  const providerClass = (r.provider || "").toLowerCase().replace(/\s/g, "");

  // Build truth badge if available
  let truthBadge = "";
  if (r.truth_level) {
    const tl = r.truth_level;
    const truthPct = ((tl.truth_score || 0) * 100).toFixed(0);
    const rating = tl.reliability_rating || "UNKNOWN";
    const ratingClass = rating === "HIGH" ? "truth-high" : rating === "MODERATE" ? "truth-mod" : "truth-low";
    const icon = rating === "HIGH" ? "🟢" : rating === "MODERATE" ? "🟡" : "🔴";
    truthBadge = `<span class="truth-badge ${ratingClass}">${icon} ${truthPct}% · ${rating}</span>`;
  }

  return `
    <div class="response-card">
      <div class="response-header">
        <div class="response-agent">
          <span class="provider-dot provider-${providerClass}"></span>
          ${escapeHtml(r.agent || "Agent")}
          ${truthBadge}
        </div>
        <div class="response-meta">
          <span class="role-tag role-${r.role || 'unknown'}">${r.role || ""}</span>
          <span>${escapeHtml(r.model || "")}</span>
          <span>Conf: ${confPct}%</span>
          <span>$${(r.cost || 0).toFixed(5)}</span>
        </div>
      </div>
      <div class="response-body">${formatContent(r.content || "")}</div>
    </div>
  `;
}

// ═════════════════════════════════════════════════════════════════
// SAM-AI ANALYSIS
// ═════════════════════════════════════════════════════════════════

async function runSamAnalysis(run) {
  document.getElementById("sam-empty").style.display = "none";
  document.getElementById("sam-content").style.display = "block";

  // Render Phase 1: Individual Truth Levels (from inline truth_levels)
  renderPhase1(run);

  // Render Phase 2: Debate rounds with trust tracking
  renderPhase2(run);

  // Render Phase 3: Consensus output
  renderPhase3(run);

  // Phase 4: Call the /api/analyze endpoint
  const analysisLoading = document.getElementById("sam-analysis-loading");
  const analysisResults = document.getElementById("sam-analysis-results");
  const analysisError = document.getElementById("sam-analysis-error");

  analysisLoading.style.display = "block";
  analysisResults.style.display = "none";
  analysisError.style.display = "none";

  try {
    // Collect all first-round debater responses for individual truth analysis
    const firstRound = (run.rounds || [])[0] || {};
    const debaterResponses = (firstRound.responses || []).filter(r => r.role === "debater");

    const resp = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: run.final_answer,
        responses: debaterResponses.map(r => ({
          content: r.content,
          confidence: r.confidence,
          agent: r.agent,
          model: r.model,
        })),
      }),
    });

    const data = await resp.json();
    analysisLoading.style.display = "none";

    if (data.success) {
      renderPhase4(data);
      analysisResults.style.display = "block";
    } else {
      analysisError.style.display = "block";
      analysisError.innerHTML = `
        <div class="sam-error-card">
          <h4>⚠️ Analysis Could Not Complete</h4>
          <p>${escapeHtml(data.error || "Unknown error")}</p>
        </div>
      `;
    }
  } catch (err) {
    analysisLoading.style.display = "none";
    analysisError.style.display = "block";
    analysisError.innerHTML = `
      <div class="sam-error-card">
        <h4>❌ Analysis Request Failed</h4>
        <p>${escapeHtml(err.message)}</p>
      </div>
    `;
  }
}

function renderSamUnavailable(run) {
  document.getElementById("sam-empty").style.display = "none";
  document.getElementById("sam-content").style.display = "block";

  // Still render phase 1-3 from run data
  renderPhase1(run);
  renderPhase2(run);
  renderPhase3(run);

  // Show unavailable message for Phase 4
  const analysisResults = document.getElementById("sam-analysis-results");
  analysisResults.style.display = "block";
  analysisResults.innerHTML = `
    <div class="sam-error-card">
      <h4>⚠️ SAM-AI Module Not Available</h4>
      <p>The SAM-AI neuro-symbolic engine is not loaded on this server. Truth levels and formal analysis are disabled.</p>
      <p style="font-size:0.85rem;color:var(--text-muted);margin-top:8px">
        Ensure the V1 SAM-AI project is at the correct path and the integration bridge can import the modules.
      </p>
    </div>
  `;
}

// ─── Phase 1: Individual Truth Levels ───
function renderPhase1(run) {
  const container = document.getElementById("sam-individual-cards");
  container.innerHTML = "";

  const firstRound = (run.rounds || [])[0] || {};
  const debaters = (firstRound.responses || []).filter(r => r.role === "debater");

  if (debaters.length === 0) {
    container.innerHTML = '<div class="sam-info-card">No individual responses recorded.</div>';
    return;
  }

  debaters.forEach(r => {
    const tl = r.truth_level || {};
    const score = tl.truth_score || 0;
    const rating = tl.reliability_rating || "UNKNOWN";
    const pct = (score * 100).toFixed(0);
    const rClass = rating === "HIGH" ? "truth-high" : rating === "MODERATE" ? "truth-mod" : "truth-low";
    const icon = rating === "HIGH" ? "🟢" : rating === "MODERATE" ? "🟡" : "🔴";

    const calibrated = tl.calibrated_confidence ? (tl.calibrated_confidence * 100).toFixed(1) : "N/A";
    const entropy = tl.entropy ? tl.entropy.toFixed(4) : "N/A";
    const category = tl.category || "unknown";

    container.innerHTML += `
      <div class="sam-truth-card">
        <div class="sam-truth-header">
          <strong>${escapeHtml(r.agent || "Agent")}</strong>
          <span class="sam-model-tag">${escapeHtml(r.provider || "")} · ${escapeHtml(r.model || "")}</span>
        </div>
        <div class="sam-truth-score">
          <span class="truth-badge ${rClass}">${icon} ${pct}% Truth · ${rating}</span>
        </div>
        <div class="sam-truth-metrics">
          <div class="sam-micro-metric">
            <span class="micro-label">Calibrated</span>
            <span class="micro-value">${calibrated}%</span>
          </div>
          <div class="sam-micro-metric">
            <span class="micro-label">Entropy</span>
            <span class="micro-value">${entropy}</span>
          </div>
          <div class="sam-micro-metric">
            <span class="micro-label">Category</span>
            <span class="micro-value">${escapeHtml(category)}</span>
          </div>
        </div>
        <div class="sam-score-bar">
          <div class="sam-score-fill" style="width:${Math.min(100, Math.max(0, score * 100))}%"></div>
        </div>
      </div>
    `;
  });
}

// ─── Phase 2: Debate Rounds ───
function renderPhase2(run) {
  const container = document.getElementById("sam-debate-rounds");
  container.innerHTML = "";

  const rounds = run.rounds || [];
  if (rounds.length <= 1) {
    container.innerHTML = '<div class="sam-info-card">Only one round — no multi-round debate to analyze.</div>';
    return;
  }

  rounds.slice(1).forEach(round => {
    const consensus = ((round.consensus || 0) * 100).toFixed(0);
    let html = `
      <div class="sam-round-card">
        <div class="sam-round-header" onclick="this.nextElementSibling.classList.toggle('collapsed')">
          <span>Round ${round.round}</span>
          <div class="sam-round-badges">
            <span class="round-badge badge-amber">$${(round.round_cost || 0).toFixed(5)}</span>
            <span class="round-badge badge-green">${consensus}% consensus</span>
          </div>
        </div>
        <div class="sam-round-body">
    `;

    (round.responses || []).forEach(r => {
      const confPct = ((r.confidence || 0) * 100).toFixed(0);
      let truthHtml = "";
      if (r.truth_level) {
        const tl = r.truth_level;
        const tPct = ((tl.truth_score || 0) * 100).toFixed(0);
        const rating = tl.reliability_rating || "UNKNOWN";
        const rClass = rating === "HIGH" ? "truth-high" : rating === "MODERATE" ? "truth-mod" : "truth-low";
        const icon = rating === "HIGH" ? "🟢" : rating === "MODERATE" ? "🟡" : "🔴";
        truthHtml = `<span class="truth-badge ${rClass}">${icon} ${tPct}%</span>`;
      }

      html += `
        <div class="sam-mini-response">
          <div class="sam-mini-header">
            <strong>${escapeHtml(r.agent || "")}</strong>
            <span class="sam-mini-role">${r.role || ""}</span>
            ${truthHtml}
            <span class="sam-mini-conf">Conf: ${confPct}%</span>
          </div>
          <div class="sam-mini-content">${escapeHtml(truncate(r.content || "", 400))}</div>
        </div>
      `;
    });

    html += `</div></div>`;
    container.innerHTML += html;
  });
}

// ─── Phase 3: Synthesis Output ───
function renderPhase3(run) {
  const container = document.getElementById("sam-synthesis-output");

  if (!run.judge) {
    container.innerHTML = '<div class="sam-info-card">No judge synthesis available.</div>';
    return;
  }

  const j = run.judge;
  const confPct = ((j.confidence || 0) * 100).toFixed(0);

  container.innerHTML = `
    <div class="sam-synthesis-card">
      <div class="sam-synth-header">
        <div>
          <strong>${escapeHtml(j.agent || "Synthesizer")}</strong>
          <span class="sam-model-tag">${escapeHtml(j.provider || "")} · ${escapeHtml(j.model || "")}</span>
        </div>
        <div class="sam-synth-meta">
          <span>Confidence: ${confPct}%</span>
          <span>Cost: $${(j.cost || 0).toFixed(5)}</span>
          <span>Tokens: ${(j.tokens_total || 0).toLocaleString()}</span>
        </div>
      </div>
      <div class="sam-synth-body">${formatContent(j.content || "")}</div>
    </div>
  `;
}

// ─── Phase 4: SAM-AI Formal Analysis Results ───
function renderPhase4(data) {
  const container = document.getElementById("sam-analysis-results");
  const analysis = data.analysis || {};

  if (!analysis.success) {
    container.innerHTML = `
      <div class="sam-error-card">
        <h4>⚠️ Analysis Returned Error</h4>
        <p>${escapeHtml(analysis.error || "Unknown error")}</p>
      </div>
    `;
    return;
  }

  const meta = analysis.meta_evaluation || {};
  const unc = analysis.uncertainty || {};
  const corr = analysis.correction || {};
  const reasoning = analysis.reasoning || {};

  const quality = meta.overall_quality || 0;
  const qualityPct = (quality * 100).toFixed(1);
  const qColor = quality >= 0.75 ? "#34d399" : quality >= 0.5 ? "#fbbf24" : "#f87171";

  const isValid = meta.is_valid;
  const structural = meta.structural_score || 0;
  const consistency = meta.consistency_score || 0;

  const calibrated = unc.calibrated_confidence || 0;
  const entropy = unc.entropy || 0;
  const reliability = unc.reliability_rating || "UNKNOWN";
  const relIcon = { "HIGH": "🟢", "MODERATE": "🟡", "LOW": "🟠", "VERY_LOW": "🔴" }[reliability] || "⚪";

  const issues = meta.issues || [];
  const warnings = meta.warnings || [];
  const wasCorrected = corr.was_corrected || false;

  container.innerHTML = `
    <!-- Score Overview -->
    <div class="sam-scores-grid">
      <div class="sam-score-card">
        <div class="sam-score-title">Overall Quality</div>
        <div class="sam-score-big" style="color:${qColor}">${qualityPct}%</div>
        <div class="sam-bar-bg"><div class="sam-bar-fill" style="width:${qualityPct}%;background:${qColor}"></div></div>
      </div>
      <div class="sam-score-card">
        <div class="sam-score-title">Structural Validity</div>
        <div class="sam-score-big">${isValid ? '<span style="color:#34d399">✓ VALID</span>' : '<span style="color:#f87171">✗ INVALID</span>'}</div>
        <div class="sam-bar-bg"><div class="sam-bar-fill" style="width:${(structural * 100).toFixed(1)}%;background:#22c55e"></div></div>
        <div class="sam-score-sub">${(structural * 100).toFixed(1)}%</div>
      </div>
      <div class="sam-score-card">
        <div class="sam-score-title">Calibrated Confidence</div>
        <div class="sam-score-big">${(calibrated * 100).toFixed(1)}%</div>
        <div class="sam-score-sub">${relIcon} ${reliability}</div>
      </div>
      <div class="sam-score-card">
        <div class="sam-score-title">Information Entropy</div>
        <div class="sam-score-big">${entropy.toFixed(4)}</div>
        <div class="sam-bar-bg"><div class="sam-bar-fill" style="width:${(consistency * 100).toFixed(1)}%;background:#3b82f6"></div></div>
        <div class="sam-score-sub">Consistency: ${(consistency * 100).toFixed(1)}%</div>
      </div>
    </div>

    <!-- Issues & Warnings -->
    <div class="sam-issues-section">
      ${issues.length > 0 ? `
        <div class="sam-issues-card sam-issues-bad">
          <h4>🚨 Issues Detected</h4>
          ${issues.map(i => `<div class="sam-issue-item sam-issue-error">✖ ${escapeHtml(i)}</div>`).join('')}
        </div>
      ` : ''}
      ${warnings.length > 0 ? `
        <div class="sam-issues-card sam-issues-warn">
          <h4>⚠️ Warnings</h4>
          ${warnings.map(w => `<div class="sam-issue-item sam-issue-warning">⚡ ${escapeHtml(w)}</div>`).join('')}
        </div>
      ` : ''}
      ${issues.length === 0 && warnings.length === 0 ? `
        <div class="sam-issues-card sam-issues-good">
          <h4>✅ Clean Analysis</h4>
          <p>No logical fallacies or structural inconsistencies detected.</p>
        </div>
      ` : ''}
    </div>

    <!-- Self-Correction -->
    <div class="sam-correction-card ${wasCorrected ? 'corrected' : 'not-corrected'}">
      <h4>🔄 Self-Correction Engine</h4>
      ${wasCorrected ? `
        <p class="correction-triggered">TRIGGERED — ${corr.correction_rounds || 0} correction round(s)</p>
        <p>Quality improved: ${((corr.quality_before || 0) * 100).toFixed(1)}% → ${((corr.quality_after || 0) * 100).toFixed(1)}%</p>
        <div class="sam-bar-bg" style="margin-top:8px">
          <div class="sam-bar-fill" style="width:${((corr.quality_after || 0) * 100).toFixed(1)}%;background:linear-gradient(90deg,#fbbf24,#34d399)"></div>
        </div>
      ` : `
        <p class="correction-clean">NOT NEEDED — Output quality above threshold</p>
      `}
    </div>

    <!-- Individual Truth Levels from API -->
    ${data.individual_truths && data.individual_truths.length > 0 ? `
      <div class="sam-individual-api">
        <h4>🔬 API-Computed Individual Truth Levels</h4>
        <div class="sam-grid">
          ${data.individual_truths.map(t => {
    const tPct = ((t.truth_score || 0) * 100).toFixed(0);
    const tRating = t.reliability_rating || "UNKNOWN";
    const tClass = tRating === "HIGH" ? "truth-high" : tRating === "MODERATE" ? "truth-mod" : "truth-low";
    const tIcon = tRating === "HIGH" ? "🟢" : tRating === "MODERATE" ? "🟡" : "🔴";
    return `
              <div class="sam-mini-truth">
                <strong>${escapeHtml(t.agent || "Agent")}</strong>
                <span class="truth-badge ${tClass}">${tIcon} ${tPct}% · ${tRating}</span>
              </div>
            `;
  }).join('')}
        </div>
      </div>
    ` : ''}
  `;
}

// ═════════════════════════════════════════════════════════════════
// RENDER ANALYTICS
// ═════════════════════════════════════════════════════════════════

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

  const roundCosts = (run.rounds || []).map(rd => ({ round: rd.round, cost: rd.round_cost || 0, consensus: ((rd.consensus || 0) * 100).toFixed(0) }));

  const providerCosts = {};
  allResponses.forEach(r => {
    const p = r.provider || "Unknown";
    providerCosts[p] = (providerCosts[p] || 0) + (r.cost || 0);
  });

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

// ═════════════════════════════════════════════════════════════════
// CANVAS CHARTS
// ═════════════════════════════════════════════════════════════════

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
  ctx.beginPath(); ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2);
  ctx.fillStyle = "#111827"; ctx.fill();
  labels.forEach((l, i) => {
    const y = 30 + i * 22;
    ctx.fillStyle = colors[i % colors.length];
    ctx.fillRect(w * 0.72, y, 10, 10);
    ctx.fillStyle = "#94a3b8"; ctx.font = "11px Inter"; ctx.textAlign = "left";
    ctx.fillText(`${l}: $${data[i].toFixed(4)}`, w * 0.72 + 16, y + 9);
  });
}

// ═════════════════════════════════════════════════════════════════
// UTILITIES
// ═════════════════════════════════════════════════════════════════

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function truncate(text, limit) {
  if (!text) return "";
  return text.length > limit ? text.slice(0, limit).trim() + " ..." : text;
}

function formatContent(text) {
  if (!text) return "";
  // Basic markdown-like formatting
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/\n/g, '<br>');
  return html;
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = "toast toast-" + type;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100px)";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
