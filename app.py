from __future__ import annotations

import json
import re
import time
from itertools import combinations
from typing import Dict, List, Optional, Sequence, Tuple

import streamlit as st
try:
    import pandas as pd
except Exception as exc:
    pd = None
    _PANDAS_IMPORT_ERROR = str(exc)

try:
    import plotly.express as px
except Exception as exc:
    px = None
    _PLOTLY_IMPORT_ERROR = str(exc)

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv() -> None:  # type: ignore[override]
        return None

from debate_app.agents.providers import (
    MODEL_CATALOG,
    PROVIDER_ENV_KEYS,
    PROVIDER_LABELS,
    ModelSpec,
    build_agent_from_spec,
    build_custom_model_spec,
    provider_has_key,
)
from debate_app.core.prompts import (
    ADVERSARIAL_SYSTEM_PROMPT,
    DEBATER_SYSTEM_PROMPT,
    FACT_CHECKER_SYSTEM_PROMPT,
    JUDGE_SYSTEM_PROMPT,
)

# ── SAM-AI Integration ─────────────────────────────────────────────────────
try:
    from integration.sam_bridge import compute_truth_level, run_full_analysis
    SAM_AI_AVAILABLE = True
except Exception as _sam_err:
    SAM_AI_AVAILABLE = False
    _SAM_AI_IMPORT_ERROR = str(_sam_err)

load_dotenv()
st.set_page_config(page_title="SynapseForge Studio", page_icon="⚡", layout="wide")

PRESETS = {
    "Balanced": {
        "debaters": ["OpenAI GPT-4o mini", "Google Gemini 1.5 Flash"],
        "judge": "OpenAI GPT-4o",
        "fact_checker": "None",
        "adversarial": "None",
    },
    "Rigorous": {
        "debaters": ["OpenAI GPT-4o", "Anthropic Claude 3 Opus", "Google Gemini 1.5 Pro"],
        "judge": "OpenAI GPT-4o",
        "fact_checker": "Anthropic Claude 3 Haiku",
        "adversarial": "OpenAI GPT-4o mini",
    },
    "Demo": {
        "debaters": ["Mock Skeptic", "Mock Optimist"],
        "judge": "Mock Judge",
        "fact_checker": "Mock Fact Checker",
        "adversarial": "Mock Challenger",
    },
}

CUSTOM_MODEL_REGEX = re.compile(
    r"^(openai|google|anthropic|mock)\s*:\s*([^|]+?)(?:\s*\|\s*(.+))?$",
    re.IGNORECASE,
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
            .stApp {
                background:
                    radial-gradient(circle at 10% -10%, #202736 0%, transparent 20%),
                    radial-gradient(circle at 90% -10%, #1e293b 0%, transparent 20%),
                    linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                font-family: 'Space Grotesk', sans-serif;
                color: #f8fafc;
            }
            .hero {
                border-radius: 20px;
                padding: 2rem;
                border: 1px solid rgba(148, 163, 184, 0.1);
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.05) 100%);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
                margin-bottom: 2rem;
                text-align: center;
            }
            .hero h1 { margin: 0; background: linear-gradient(to right, #818cf8, #c084fc, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; }
            .hero p { margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 1.1rem; }
            .panel {
                border: 1px solid rgba(255, 255, 255, 0.08);
                background: rgba(30, 41, 59, 0.6);
                border-radius: 14px;
                padding: 1rem;
                margin-bottom: 0.75rem;
                backdrop-filter: blur(8px);
            }
            .status-good { color: #34d399; font-weight: 600; }
            .status-bad { color: #f87171; font-weight: 600; }
            .mono { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: #64748b; }
            .answer {
                border: 1px solid rgba(99, 102, 241, 0.2);
                border-left: 4px solid #818cf8;
                border-radius: 12px;
                padding: 1.5rem;
                background: rgba(30, 41, 59, 0.8);
                line-height: 1.7;
            }
            .truth-gauge {
                display: inline-block;
                background: rgba(52, 211, 153, 0.1);
                border: 1px solid rgba(52, 211, 153, 0.3);
                border-radius: 20px;
                padding: 0.2rem 0.7rem;
                font-size: 0.82rem;
                font-weight: 600;
            }
            .truth-high { color: #34d399; border-color: rgba(52,211,153,0.4); background: rgba(52,211,153,0.12); }
            .truth-mod  { color: #fbbf24; border-color: rgba(251,191,36,0.4); background: rgba(251,191,36,0.12); }
            .truth-low  { color: #f87171; border-color: rgba(248,113,113,0.4); background: rgba(248,113,113,0.12); }
            .score-bar-bg { background: rgba(255,255,255,0.08); border-radius: 8px; height: 10px; margin: 4px 0; }
            .score-bar-fg { height: 10px; border-radius: 8px; transition: width 0.5s ease; }
            .analysis-card {
                border: 1px solid rgba(129,140,248,0.2);
                background: rgba(30,27,75,0.5);
                border-radius: 14px;
                padding: 1.2rem;
                margin-bottom: 0.8rem;
                backdrop-filter: blur(8px);
            }
            .analysis-title { font-size: 1rem; font-weight: 600; color: #a78bfa; margin-bottom: 0.6rem; }
            .badge-pass { background:#064e3b; color:#6ee7b7; border-radius:6px; padding:2px 8px; font-size:0.8rem; }
            .badge-fail { background:#7f1d1d; color:#fca5a5; border-radius:6px; padding:2px 8px; font-size:0.8rem; }
            .badge-warn { background:#78350f; color:#fcd34d; border-radius:6px; padding:2px 8px; font-size:0.8rem; }
            .phase-header {
                font-size: 1.15rem; font-weight: 700; color: #c4b5fd;
                border-bottom: 2px solid rgba(167,139,250,0.3);
                padding-bottom: 0.5rem; margin-bottom: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "keys": {"openai": "", "google": "", "anthropic": ""},
        "custom_models": "",
        "preset": "Balanced",
        "debaters": PRESETS["Balanced"]["debaters"],
        "judge": PRESETS["Balanced"]["judge"],
        "fact_checker": PRESETS["Balanced"]["fact_checker"],
        "adversarial": PRESETS["Balanced"]["adversarial"],
        "query": "",
        "max_rounds": 3,
        "budget": 0.75,
        "temp": 0.2,
        "consensus_threshold": 0.55,
        "delay_ms": 0,
        "run": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def parse_custom_models(raw_text: str) -> Tuple[List[ModelSpec], List[str]]:
    specs: List[ModelSpec] = []
    errors: List[str] = []
    for idx, raw in enumerate((raw_text or "").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = CUSTOM_MODEL_REGEX.match(line)
        if not match:
            errors.append(f"Line {idx}: use provider:model_id|Optional Label")
            continue
        provider, model_id, label = match.groups()
        try:
            specs.append(
                build_custom_model_spec(
                    provider=provider,
                    model_id=model_id.strip(),
                    label=label.strip() if label else None,
                    role_hints=("debater", "judge", "fact_checker", "adversarial"),
                )
            )
        except ValueError as exc:
            errors.append(f"Line {idx}: {exc}")
    return specs, errors


def merged_specs(custom_specs: Sequence[ModelSpec]) -> List[ModelSpec]:
    base = list(MODEL_CATALOG)
    used = {spec.label for spec in base}
    for spec in custom_specs:
        current = spec
        if current.label in used:
            current = ModelSpec(
                label=f"{spec.label} [custom]",
                provider=spec.provider,
                model_id=spec.model_id,
                role_hints=spec.role_hints,
            )
        base.append(current)
        used.add(current.label)
    return base


def role_options(specs: Sequence[ModelSpec], role: str) -> List[str]:
    return [spec.label for spec in specs if role in spec.role_hints]


def consensus_score(texts: Sequence[str]) -> float:
    token_sets = [set(re.findall(r"[a-zA-Z]{4,}", text.lower())[:120]) for text in texts if text]
    if len(token_sets) < 2:
        return 0.0
    scores: List[float] = []
    for left, right in combinations(token_sets, 2):
        union = left | right
        if union:
            scores.append(len(left & right) / len(union))
    return float(sum(scores) / len(scores)) if scores else 0.0


def trim_text(value: str, limit: int = 650) -> str:
    text = (value or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " ..."


def fill_prompt(template: str, replacements: Dict[str, object]) -> str:
    """Safely replace only known placeholders and keep all other braces untouched."""
    output = template
    for key, value in replacements.items():
        output = output.replace("{" + key + "}", str(value))
    return output


# ── SAM-AI UI Helpers ───────────────────────────────────────────────────────

def _truth_badge(score: float, rating: str) -> str:
    """Return an HTML truth-level badge."""
    pct = f"{score * 100:.0f}%"
    if rating in ("HIGH",):
        cls = "truth-gauge truth-high"
        icon = "🟢"
    elif rating in ("MODERATE",):
        cls = "truth-gauge truth-mod"
        icon = "🟡"
    else:
        cls = "truth-gauge truth-low"
        icon = "🔴"
    return f'<span class="{cls}">{icon} {pct} Truth · {rating}</span>'


def _score_bar(value: float, color: str = "#818cf8") -> str:
    pct = max(0, min(100, value * 100))
    return (
        f'<div class="score-bar-bg">'
        f'<div class="score-bar-fg" style="width:{pct:.1f}%;background:{color};"></div>'
        f'</div>'
    )


def render_individual_postulations(run: Dict) -> None:
    """Phase 1: Show each model's initial individual response with truth level."""
    st.markdown('<div class="phase-header">🧪 Phase 1 — Individual Postulations & Truth Levels</div>', unsafe_allow_html=True)
    if not SAM_AI_AVAILABLE:
        st.warning("SAM-AI integration unavailable. Truth levels cannot be computed.")
        return

    first_round = (run.get("rounds") or [{}])[0] if run.get("rounds") else {}
    responses = first_round.get("responses", [])
    if not responses:
        st.info("No individual responses recorded.")
        return

    debater_responses = [r for r in responses if r.get("role") == "debater"]
    cols = st.columns(max(1, len(debater_responses)))
    for i, resp in enumerate(debater_responses):
        with cols[i % len(cols)]:
            truth = compute_truth_level(
                str(resp.get("content", "")),
                _safe_float(resp.get("confidence", 0.5), 0.5),
            )
            badge = _truth_badge(truth["truth_score"], truth["reliability_rating"])
            st.markdown(
                f"<div class='analysis-card'>"
                f"<strong>{resp.get('agent', '?')}</strong> "
                f"<span class='mono'>({resp.get('provider','?')} · {resp.get('model','?')})</span><br>"
                f"{badge}"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"**Calibrated Confidence:** {truth['calibrated_confidence']:.2%}  \n"
                f"**Entropy:** {truth['entropy']:.4f}  \n"
                f"**Category:** `{truth['category']}`"
            )
            with st.expander("Response", expanded=False):
                st.markdown(str(resp.get("content", "")))


def render_debate_believability(run: Dict) -> None:
    """Phase 2 & 3: Show debate rounds with per-model believability on the debated output."""
    st.markdown('<div class="phase-header">💬 Phase 2 — Debate Arena</div>', unsafe_allow_html=True)
    rounds_data = run.get("rounds", [])
    if len(rounds_data) <= 1:
        st.info("Only one round — debate not triggered.")
        return

    for rnd in rounds_data[1:]:  # Skip first round (already shown in Phase 1)
        with st.expander(
            f"Round {rnd['round']} | cost ${rnd.get('round_cost',0):.5f} | consensus {rnd.get('consensus',0):.0%}",
            expanded=False,
        ):
            for resp in rnd.get("responses", []):
                st.markdown(f"**{resp.get('agent','')}** ({resp.get('role','')})")
                if SAM_AI_AVAILABLE and resp.get("role") == "debater":
                    truth = compute_truth_level(
                        str(resp.get("content", "")),
                        _safe_float(resp.get("confidence", 0.5), 0.5),
                    )
                    st.markdown(_truth_badge(truth["truth_score"], truth["reliability_rating"]), unsafe_allow_html=True)
                st.markdown(trim_text(str(resp.get("content", "")), 400))
                st.markdown("---")

    # Phase 3: Synthesized output
    st.markdown('<div class="phase-header">🔮 Phase 3 — Consensus Synthesis</div>', unsafe_allow_html=True)
    judge = run.get("judge")
    if judge:
        st.markdown(
            f"<div class='panel'><strong>Synthesizer</strong> "
            f"<span class='mono'>({judge.get('provider','?')} · {judge.get('model','?')})</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='answer'>", unsafe_allow_html=True)
        st.markdown(str(judge.get("content", "")))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No judge synthesis available.")


def render_sam_analysis(run: Dict) -> None:
    """Phase 4: Full SAM-AI formal analysis on the synthesized output."""
    st.markdown('<div class="phase-header">🧠 Phase 4 — SAM-AI Formal Analysis</div>', unsafe_allow_html=True)
    if not SAM_AI_AVAILABLE:
        st.error(f"SAM-AI module not loaded: {_SAM_AI_IMPORT_ERROR}")
        return

    final_text = str(run.get("final_answer", ""))
    if not final_text.strip():
        st.info("No synthesis to analyse.")
        return

    with st.spinner("Running SAM-AI neuro-symbolic analysis…"):
        report = run_full_analysis(final_text)

    if not report.get("success"):
        st.warning(f"Analysis error: {report.get('error', 'unknown')}")
        return

    meta = report["meta_evaluation"]
    unc = report["uncertainty"]
    corr = report["correction"]

    # Row 1: Core scores
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Overall Quality", f"{meta['overall_quality']:.2%}")
        q_color = "#34d399" if meta['overall_quality'] >= 0.75 else "#fbbf24" if meta['overall_quality'] >= 0.5 else "#f87171"
        st.markdown(_score_bar(meta['overall_quality'], q_color), unsafe_allow_html=True)
    with c2:
        valid_html = "<span class='badge-pass'>VALID</span>" if meta['is_valid'] else "<span class='badge-fail'>INVALID</span>"
        st.markdown(f"**Structural:** {valid_html}", unsafe_allow_html=True)
        st.markdown(_score_bar(meta['structural_score'], "#22c55e"), unsafe_allow_html=True)
    with c3:
        st.metric("Calibrated Conf.", f"{unc['calibrated_confidence']:.2%}")
        rating = unc['reliability_rating']
        icon = {"HIGH":"🟢","MODERATE":"🟡","LOW":"🟠","VERY_LOW":"🔴"}.get(rating,"⚪")
        st.caption(f"Reliability: {icon} {rating}")
    with c4:
        st.metric("Entropy", f"{unc['entropy']:.4f}")
        st.markdown(_score_bar(meta['consistency_score'], "#3b82f6"), unsafe_allow_html=True)
        st.caption(f"Consistency: {meta['consistency_score']:.2%}")

    # Row 2: Issues & Warnings
    issues = meta.get("issues", [])
    warnings_list = meta.get("warnings", [])
    if issues:
        st.markdown("**🚨 Issues Detected:**")
        for iss in issues:
            st.markdown(f"<span class='badge-fail'>✖ {iss}</span>", unsafe_allow_html=True)
    if warnings_list:
        st.markdown("**⚠ Warnings:**")
        for w in warnings_list:
            st.markdown(f"<span class='badge-warn'>⚡ {w}</span>", unsafe_allow_html=True)
    if not issues and not warnings_list:
        st.success("✅ No logical fallacies or inconsistencies detected.")

    # Row 3: Self-Correction status
    if corr.get("was_corrected"):
        st.markdown(
            f"**🔄 Self-Correction:** <span class='badge-warn'>TRIGGERED</span> "
            f"({corr['correction_rounds']} rounds) — "
            f"Quality improved from {corr['quality_before']:.2%} → {corr['quality_after']:.2%}",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**🔄 Self-Correction:** <span class='badge-pass'>NOT NEEDED</span>", unsafe_allow_html=True)


def selected_provider_keys(picked: Dict[str, object]) -> set:
    providers = {spec.provider for spec in picked.get("debaters", [])}
    for role in ["judge", "fact_checker", "adversarial"]:
        spec = picked.get(role)
        if spec:
            providers.add(spec.provider)
    return providers


def provider_mix_labels(picked: Dict[str, object]) -> str:
    providers = selected_provider_keys(picked)
    if not providers:
        return "none"
    return ", ".join(PROVIDER_LABELS.get(provider, provider) for provider in sorted(providers))


def button_full_width(label: str, **kwargs) -> bool:
    try:
        return st.button(label, width="stretch", **kwargs)
    except TypeError:
        return st.button(label, use_container_width=True, **kwargs)


def plotly_full_width(fig) -> None:
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_run_payload(run: Optional[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not isinstance(run, dict):
        return None

    run.setdefault("query", "")
    run.setdefault("rounds_requested", 0)
    run.setdefault("rounds_completed", 0)
    run.setdefault("rounds", [])
    run.setdefault("judge", None)
    run.setdefault("total_cost", 0.0)
    run.setdefault("stopped_reason", "No status available.")
    run.setdefault("final_answer", "")
    run.setdefault("warnings", [])

    sanitized_rounds: List[Dict[str, object]] = []
    for round_item in run.get("rounds", []) or []:
        if not isinstance(round_item, dict):
            continue
        responses = round_item.get("responses", []) or []
        sanitized_responses: List[Dict[str, object]] = []
        for response in responses:
            if not isinstance(response, dict):
                continue
            sanitized_responses.append(
                {
                    "round": _safe_int(response.get("round", round_item.get("round", 0))),
                    "agent": str(response.get("agent", "Unknown Agent")),
                    "role": str(response.get("role", "unknown")),
                    "provider": str(response.get("provider", "Unknown")),
                    "model": str(response.get("model", "unknown")),
                    "confidence": _safe_float(response.get("confidence", 0.0), 0.0),
                    "cost": _safe_float(response.get("cost", 0.0), 0.0),
                    "tokens_input": _safe_int(response.get("tokens_input", 0), 0),
                    "tokens_output": _safe_int(response.get("tokens_output", 0), 0),
                    "tokens_total": _safe_int(response.get("tokens_total", 0), 0),
                    "content": str(response.get("content", "")),
                    "is_error": bool(response.get("is_error", False)),
                }
            )
        sanitized_rounds.append(
            {
                "round": _safe_int(round_item.get("round", 0), 0),
                "responses": sanitized_responses,
                "round_cost": _safe_float(round_item.get("round_cost", 0.0), 0.0),
                "consensus": _safe_float(round_item.get("consensus", 0.0), 0.0),
            }
        )

    run["rounds"] = sanitized_rounds
    run["rounds_completed"] = _safe_int(run.get("rounds_completed", len(sanitized_rounds)), len(sanitized_rounds))
    run["rounds_requested"] = _safe_int(run.get("rounds_requested", run["rounds_completed"]), run["rounds_completed"])
    run["total_cost"] = _safe_float(run.get("total_cost", 0.0), 0.0)
    run["warnings"] = [str(item) for item in (run.get("warnings", []) or [])]

    judge_payload = run.get("judge")
    if isinstance(judge_payload, dict):
        run["judge"] = {
            "agent": str(judge_payload.get("agent", "Synthesizer")),
            "role": str(judge_payload.get("role", "judge")),
            "provider": str(judge_payload.get("provider", "Unknown")),
            "model": str(judge_payload.get("model", "unknown")),
            "confidence": _safe_float(judge_payload.get("confidence", 0.0), 0.0),
            "cost": _safe_float(judge_payload.get("cost", 0.0), 0.0),
            "tokens_input": _safe_int(judge_payload.get("tokens_input", 0), 0),
            "tokens_output": _safe_int(judge_payload.get("tokens_output", 0), 0),
            "tokens_total": _safe_int(judge_payload.get("tokens_total", 0), 0),
            "content": str(judge_payload.get("content", "")),
            "is_error": bool(judge_payload.get("is_error", False)),
        }
    else:
        run["judge"] = None

    return run


def sanitize_state(opts: Dict[str, List[str]]) -> None:
    base_debaters = [m for m in PRESETS["Balanced"]["debaters"] if m in opts["debater"]]
    if not base_debaters and opts["debater"]:
        base_debaters = opts["debater"][:2]

    current_debaters = [m for m in st.session_state.get("debaters", []) if m in opts["debater"]]
    st.session_state["debaters"] = current_debaters or base_debaters

    if st.session_state.get("judge") not in opts["judge"] and opts["judge"]:
        st.session_state["judge"] = opts["judge"][0]

    for key, role in [("fact_checker", "fact_checker"), ("adversarial", "adversarial")]:
        valid = ["None"] + opts[role]
        if st.session_state.get(key) not in valid:
            st.session_state[key] = "None"


def apply_preset(name: str, opts: Dict[str, List[str]]) -> None:
    preset = PRESETS[name]
    st.session_state["debaters"] = [m for m in preset["debaters"] if m in opts["debater"]]
    st.session_state["judge"] = preset["judge"] if preset["judge"] in opts["judge"] else opts["judge"][0]
    st.session_state["fact_checker"] = (
        preset["fact_checker"] if preset["fact_checker"] in opts["fact_checker"] else "None"
    )
    st.session_state["adversarial"] = (
        preset["adversarial"] if preset["adversarial"] in opts["adversarial"] else "None"
    )


def selected_specs(spec_lookup: Dict[str, ModelSpec]) -> Dict[str, object]:
    debaters = [spec_lookup[m] for m in st.session_state["debaters"] if m in spec_lookup]
    judge = spec_lookup.get(st.session_state["judge"])
    fact = spec_lookup.get(st.session_state["fact_checker"]) if st.session_state["fact_checker"] != "None" else None
    adversarial = spec_lookup.get(st.session_state["adversarial"]) if st.session_state["adversarial"] != "None" else None
    return {"debaters": debaters, "judge": judge, "fact_checker": fact, "adversarial": adversarial}


def render_record(record: Dict[str, object], compact: bool) -> None:
    agent_name = str(record.get("agent", "Unknown Agent"))
    role_name = str(record.get("role", "unknown"))
    provider_name = str(record.get("provider", "Unknown"))
    model_name = str(record.get("model", "unknown"))
    confidence = _safe_float(record.get("confidence", 0.0), 0.0)
    cost = _safe_float(record.get("cost", 0.0), 0.0)
    tokens_input = _safe_int(record.get("tokens_input", 0), 0)
    tokens_output = _safe_int(record.get("tokens_output", 0), 0)
    content = str(record.get("content", ""))

    st.markdown(
        (
            f"<div class='panel'><strong>{agent_name}</strong><br>"
            f"Role: {role_name} | Provider: {provider_name} | Model: {model_name}</div>"
        ),
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    cols[0].metric("Confidence", f"{confidence * 100:.0f}%")
    cols[1].metric("Cost", f"${cost:.5f}")
    cols[2].metric("Input", str(tokens_input))
    cols[3].metric("Output", str(tokens_output))
    body = trim_text(content) if compact else content
    st.markdown(body)
    if compact and len(content) > len(body):
        with st.popover("Full response"):
            st.markdown(content)


def run_debate(
    query: str,
    specs: Dict[str, object],
    keys: Dict[str, str],
    rounds: int,
    budget: float,
    temp: float,
    consensus_threshold: float,
    delay_seconds: float,
) -> Dict[str, object]:
    roster: List[Tuple[str, ModelSpec, str, object]] = []
    warnings: List[str] = []
    for i, spec in enumerate(specs["debaters"], start=1):
        roster.append(
            (
                "debater",
                spec,
                f"Contributor {i}",
                build_agent_from_spec(spec, DEBATER_SYSTEM_PROMPT, keys, f"Contributor {i}", temp),
            )
        )

    if specs.get("fact_checker"):
        spec = specs["fact_checker"]
        roster.append(
            (
                "fact_checker",
                spec,
                "Verifier",
                build_agent_from_spec(
                    spec,
                    fill_prompt(
                        FACT_CHECKER_SYSTEM_PROMPT,
                        {"round_number": "{round}", "agent_name": "multiple agents"},
                    ),
                    keys,
                    "Verifier",
                    temp,
                ),
            )
        )

    if specs.get("adversarial"):
        spec = specs["adversarial"]
        roster.append(
            (
                "adversarial",
                spec,
                "Stress Tester",
                build_agent_from_spec(
                    spec,
                    fill_prompt(
                        ADVERSARIAL_SYSTEM_PROMPT,
                        {"round_number": "{round}", "agent_name": "consensus", "topic": query},
                    ),
                    keys,
                    "Stress Tester",
                    temp,
                ),
            )
        )

    judge_spec = specs["judge"]
    judge = build_agent_from_spec(
        judge_spec,
        fill_prompt(JUDGE_SYSTEM_PROMPT, {"original_question": query, "n": rounds}),
        keys,
        "Synthesizer",
        max(temp - 0.05, 0.0),
    )

    progress = st.progress(0.0)
    status = st.empty()
    round_view = st.container()

    logs: List[Dict[str, object]] = []
    context = ""
    total_cost = 0.0
    stop_reason = "Configured rounds completed."
    fatal_failure = False

    for round_number in range(1, rounds + 1):
        if total_cost >= budget:
            stop_reason = f"Stopped before round {round_number}: budget reached."
            break

        progress.progress((round_number - 1) / rounds)
        status.markdown(f"Running collaborative round {round_number} of {rounds} ...")

        responses: List[Dict[str, object]] = []
        for role, spec, name, agent in roster:
            if total_cost >= budget:
                stop_reason = f"Budget reached in round {round_number}."
                break
            result = agent.generate_response(query=query, context=context)
            is_error = str(result.content).strip().lower().startswith("error:")
            record = {
                "round": round_number,
                "agent": name,
                "role": role,
                "provider": PROVIDER_LABELS.get(spec.provider, spec.provider),
                "model": spec.model_id,
                "confidence": result.confidence,
                "cost": result.cost,
                "tokens_input": result.token_usage.get("input", 0),
                "tokens_output": result.token_usage.get("output", 0),
                "tokens_total": result.token_usage.get("total", 0),
                "content": result.content,
                "is_error": is_error,
            }
            responses.append(record)
            total_cost += result.cost
            if is_error:
                warnings.append(f"{name} failed in round {round_number}: {trim_text(str(result.content), 180)}")
            if delay_seconds > 0:
                time.sleep(delay_seconds)

        if not responses:
            break

        round_cost = float(sum(r["cost"] for r in responses))

        if all(item["is_error"] for item in responses):
            stop_reason = f"Stopped at round {round_number}: all agents returned errors."
            logs.append({"round": round_number, "responses": responses, "round_cost": round_cost, "consensus": 0.0})
            fatal_failure = True
            break

        debater_texts = [r["content"] for r in responses if r["role"] == "debater"]
        round_consensus = consensus_score(debater_texts)
        logs.append({"round": round_number, "responses": responses, "round_cost": round_cost, "consensus": round_consensus})

        context_block = "\n".join(f"{r['agent']} ({r['role']}): {r['content']}" for r in responses)
        context = (context + f"\n\nRound {round_number}\n" + context_block).strip()
        if len(context) > 18000:
            context = context[-18000:]

        with round_view.expander(
            f"Round {round_number} | cost ${round_cost:.5f} | consensus {round_consensus:.0%}",
            expanded=True,
        ):
            for record in responses:
                render_record(record, compact=True)

        if round_number >= 2 and round_consensus >= consensus_threshold:
            stop_reason = f"Stopped early at round {round_number}: consensus {round_consensus:.0%}."
            break

    judge_record: Optional[Dict[str, object]] = None
    final_answer = "No final synthesis generated."

    if total_cost < budget and not fatal_failure:
        status.markdown("Synthesizer is generating final answer ...")
        judge_query = (
            f"Original question: {query}\n\nCollaborative transcript:\n{context}\n\n"
            "Deliver one final answer with rationale, uncertainties, and practical next actions."
        )
        verdict = judge.generate_response(query=judge_query, context="")
        judge_is_error = str(verdict.content).strip().lower().startswith("error:")
        total_cost += verdict.cost
        judge_record = {
            "agent": "Synthesizer",
            "role": "judge",
            "provider": PROVIDER_LABELS.get(judge_spec.provider, judge_spec.provider),
            "model": judge_spec.model_id,
            "confidence": verdict.confidence,
            "cost": verdict.cost,
            "tokens_input": verdict.token_usage.get("input", 0),
            "tokens_output": verdict.token_usage.get("output", 0),
            "tokens_total": verdict.token_usage.get("total", 0),
            "content": verdict.content,
            "is_error": judge_is_error,
        }
        final_answer = verdict.content
        if judge_is_error:
            warnings.append(f"Synthesizer failed: {trim_text(str(verdict.content), 180)}")
    else:
        if fatal_failure:
            final_answer = "Synthesis stopped because all active agents returned errors. Check provider keys, model ids, or network access."
        else:
            stop_reason = f"Stopped after rounds: budget cap ${budget:.2f} exhausted."

    progress.progress(1.0)
    status.markdown("Collaboration run complete.")

    return {
        "query": query,
        "rounds_requested": rounds,
        "rounds_completed": len(logs),
        "rounds": logs,
        "judge": judge_record,
        "total_cost": round(total_cost, 6),
        "stopped_reason": stop_reason,
        "final_answer": final_answer,
        "warnings": warnings,
    }


def metrics_frame(run: Dict[str, object]) -> pd.DataFrame:
    if pd is None:
        return None
    rows: List[Dict[str, object]] = []
    for round_log in run.get("rounds", []):
        rows.extend(round_log.get("responses", []))
    if run.get("judge"):
        judge_row = dict(run["judge"])
        judge_row["round"] = run.get("rounds_completed", 0) + 1
        rows.append(judge_row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    required_defaults = {
        "round": 0,
        "agent": "Unknown Agent",
        "role": "unknown",
        "provider": "Unknown",
        "model": "unknown",
        "confidence": 0.0,
        "cost": 0.0,
        "tokens_input": 0,
        "tokens_output": 0,
        "tokens_total": 0,
        "content": "",
        "is_error": False,
    }
    for column_name, default_value in required_defaults.items():
        if column_name not in df.columns:
            df[column_name] = default_value
    return df


def provider_sidebar() -> None:
    st.markdown("### Provider Access")
    keys = st.session_state["keys"]
    openai_key = st.text_input("OpenAI API key", type="password", value=keys.get("openai", ""))
    google_key = st.text_input("Google API key", type="password", value=keys.get("google", ""))
    anthropic_key = st.text_input("Anthropic API key", type="password", value=keys.get("anthropic", ""))
    st.session_state["keys"] = {
        "openai": openai_key.strip(),
        "google": google_key.strip(),
        "anthropic": anthropic_key.strip(),
    }

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("**Key Health**")
    for provider in ["openai", "google", "anthropic"]:
        ready = provider_has_key(provider, st.session_state["keys"])
        css = "status-good" if ready else "status-bad"
        status = "ready" if ready else "missing"
        st.markdown(
            f"{PROVIDER_LABELS[provider]} (`{PROVIDER_ENV_KEYS[provider]}`): <span class='{css}'>{status}</span>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    inject_css()
    init_state()

    st.markdown(
        """
        <div class="hero">
            <h1>⚡ SynapseForge Studio · V2</h1>
            <p>Collaborative multi-model intelligence engine — now powered by SAM-AI neuro-symbolic analysis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        provider_sidebar()
        st.markdown("### Run Controls")
        st.session_state["max_rounds"] = st.slider("Collaboration rounds", 1, 8, int(st.session_state["max_rounds"]))
        st.session_state["budget"] = st.slider("Budget cap (USD)", 0.05, 10.0, float(st.session_state["budget"]), 0.05)
        st.session_state["temp"] = st.slider("Temperature", 0.0, 1.0, float(st.session_state["temp"]), 0.05)
        st.session_state["consensus_threshold"] = st.slider(
            "Early-stop consensus", 0.2, 0.9, float(st.session_state["consensus_threshold"]), 0.05
        )
        st.session_state["delay_ms"] = st.slider("Visual response delay (ms)", 0, 1200, int(st.session_state["delay_ms"]), 100)

        st.markdown("### Custom Models")
        st.session_state["custom_models"] = st.text_area(
            "provider:model_id|Optional Label",
            value=st.session_state["custom_models"],
            height=130,
            help="Example: openai:gpt-4.1-mini|OpenAI GPT 4.1 Mini",
        )
        st.markdown("<div class='mono'>One model per line. Leave empty for built-in catalog.</div>", unsafe_allow_html=True)

    custom_specs, custom_errors = parse_custom_models(st.session_state["custom_models"])
    specs = merged_specs(custom_specs)
    lookup = {spec.label: spec for spec in specs}

    opts = {
        "debater": role_options(specs, "debater"),
        "judge": role_options(specs, "judge"),
        "fact_checker": role_options(specs, "fact_checker"),
        "adversarial": role_options(specs, "adversarial"),
    }
    sanitize_state(opts)

    if custom_errors:
        st.warning("Custom model issues:\n- " + "\n- ".join(custom_errors))

    tab_studio, tab_feed, tab_analysis, tab_metrics = st.tabs(["Studio", "Synthesis Feed", "🧠 SAM-AI Analysis", "Analytics"])

    with tab_studio:
        left, right = st.columns([1.3, 1.0], gap="large")
        with left:
            st.markdown("### Research Brief")
            st.session_state["query"] = st.text_area(
                "Question to analyze",
                value=st.session_state["query"],
                height=180,
                placeholder="Example: What are the most promising approaches to achieving AGI safety, and how should research priorities be allocated over the next 5 years?",
            )
            preset_options = list(PRESETS.keys())
            preset_index = (
                preset_options.index(st.session_state["preset"])
                if st.session_state["preset"] in preset_options
                else 0
            )
            preset_name = st.selectbox("Lineup preset", preset_options, index=preset_index)
            st.session_state["preset"] = preset_name
            if button_full_width("Apply preset"):
                apply_preset(preset_name, opts)
                st.rerun()

        with right:
            st.markdown("### Agent Roles")
            st.multiselect("Core Contributors", opts["debater"], key="debaters")
            st.selectbox("Synthesizer / Judge", opts["judge"], key="judge")
            st.selectbox("Verifier (Fact Checker)", ["None"] + opts["fact_checker"], key="fact_checker")
            st.selectbox("Stress Tester (Adversarial)", ["None"] + opts["adversarial"], key="adversarial")

        picked = selected_specs(lookup)
        lineup_agents = len(picked["debaters"]) + 1 + int(bool(picked.get("fact_checker"))) + int(bool(picked.get("adversarial")))
        preview_cols = st.columns(3)
        preview_cols[0].metric("Lineup Size", lineup_agents)
        preview_cols[1].metric("Contributors", len(picked["debaters"]))
        provider_mix = provider_mix_labels(picked)
        provider_count = len(provider_mix.split(", ")) if provider_mix != "none" else 0
        preview_cols[2].metric("Providers", provider_count)
        st.caption(f"Provider mix: {provider_mix}")

        missing = sorted(
            provider
            for provider in selected_provider_keys(picked)
            if provider != "mock" and not provider_has_key(provider, st.session_state["keys"])
        )

        if missing:
            st.error("Missing API keys for: " + ", ".join(PROVIDER_LABELS[p] for p in missing))

        disabled = bool(missing) or not st.session_state["query"].strip() or not picked["debaters"] or not picked["judge"]
        action_cols = st.columns([3, 1])
        with action_cols[0]:
            run_clicked = button_full_width(
                "Run Collaborative Synthesis",
                type="primary",
                disabled=disabled,
            )
        with action_cols[1]:
            clear_clicked = button_full_width("Clear")
        if clear_clicked:
            st.session_state["run"] = None
            st.rerun()

        if run_clicked:
            st.session_state["run"] = run_debate(
                query=st.session_state["query"].strip(),
                specs=picked,
                keys=st.session_state["keys"],
                rounds=int(st.session_state["max_rounds"]),
                budget=float(st.session_state["budget"]),
                temp=float(st.session_state["temp"]),
                consensus_threshold=float(st.session_state["consensus_threshold"]),
                delay_seconds=float(st.session_state["delay_ms"]) / 1000.0,
            )

        run = normalize_run_payload(st.session_state.get("run"))
        st.session_state["run"] = run
        if run:
            st.markdown("### Final Synthesis")
            st.markdown(
                (
                    "<div class='panel'>"
                    f"<strong>Rounds:</strong> {run.get('rounds_completed', 0)} / {run.get('rounds_requested', 0)}<br>"
                    f"<strong>Total Cost:</strong> ${_safe_float(run.get('total_cost', 0.0), 0.0):.6f}<br>"
                    f"<strong>Status:</strong> {run.get('stopped_reason', 'No status available.')}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            st.markdown("<div class='answer'>", unsafe_allow_html=True)
            st.markdown(str(run.get("final_answer", "")))
            st.markdown("</div>", unsafe_allow_html=True)
            for warning in run.get("warnings", []):
                st.warning(warning)
            st.download_button(
                "Download Run JSON",
                data=json.dumps(run, indent=2),
                file_name="synapse_run.json",
                mime="application/json",
            )

    with tab_feed:
        run = normalize_run_payload(st.session_state.get("run"))
        st.session_state["run"] = run
        if not run:
            st.info("Run a synthesis from Studio to view transcript.")
        else:
            st.markdown("### Round Transcript")
            for round_log in run.get("rounds", []):
                with st.expander(
                    f"Round {round_log['round']} | cost ${round_log['round_cost']:.5f} | consensus {round_log['consensus']:.0%}",
                    expanded=False,
                ):
                    for record in round_log.get("responses", []):
                        render_record(record, compact=False)
            if run.get("judge"):
                st.markdown("### Synthesizer Output")
                render_record(run["judge"], compact=False)

    with tab_analysis:
        run = normalize_run_payload(st.session_state.get("run"))
        st.session_state["run"] = run
        if not run:
            st.info("Run a synthesis from Studio to unlock the 4-phase SAM-AI analysis.")
        else:
            # Phase 1: Individual Postulations + Truth Levels
            render_individual_postulations(run)
            st.markdown("---")
            # Phase 2 & 3: Debate + Consensus
            render_debate_believability(run)
            st.markdown("---")
            # Phase 4: SAM-AI Formal Analysis
            render_sam_analysis(run)

    with tab_metrics:
        run = normalize_run_payload(st.session_state.get("run"))
        st.session_state["run"] = run
        if not run:
            st.info("Run a synthesis to unlock analytics.")
            return

        if pd is None or px is None:
            if pd is None:
                st.error(f"Analytics unavailable: pandas import failed ({_PANDAS_IMPORT_ERROR}).")
            if px is None:
                st.error(f"Analytics unavailable: plotly import failed ({_PLOTLY_IMPORT_ERROR}).")
            return

        df = metrics_frame(run)
        if df is None or df.empty:
            st.warning("No metrics to display.")
            return

        df["confidence_pct"] = (df["confidence"].fillna(0.0) * 100).round(1)
        total_tokens = int(df["tokens_total"].fillna(0).sum())
        avg_conf = float(df["confidence"].fillna(0.0).mean())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Cost", f"${run['total_cost']:.6f}")
        m2.metric("Total Tokens", f"{total_tokens:,}")
        m3.metric("Avg Confidence", f"{avg_conf * 100:.1f}%")
        m4.metric("Agents", str(df["agent"].nunique()))

        round_cost = pd.DataFrame([
            {"round": r["round"], "cost": r["round_cost"]}
            for r in run.get("rounds", [])
        ])

        c1, c2 = st.columns(2)
        with c1:
            if not round_cost.empty:
                fig_cost = px.line(round_cost, x="round", y="cost", markers=True, title="Cost by Round")
                fig_cost.update_layout(height=320)
                plotly_full_width(fig_cost)
            fig_tokens = px.bar(df, x="agent", y="tokens_total", color="role", title="Token Usage by Agent")
            fig_tokens.update_layout(height=360)
            plotly_full_width(fig_tokens)

        with c2:
            fig_conf = px.scatter(
                df,
                x="round",
                y="confidence_pct",
                color="role",
                size="tokens_total",
                hover_data=["agent", "provider", "model"],
                title="Confidence Trajectory",
            )
            fig_conf.update_layout(height=320)
            plotly_full_width(fig_conf)

            provider_cost = df.groupby("provider", as_index=False)["cost"].sum().sort_values("cost", ascending=False)
            if provider_cost.empty:
                st.info("No provider cost data available yet.")
            else:
                fig_share = px.pie(provider_cost, values="cost", names="provider", title="Cost Share by Provider")
                fig_share.update_layout(height=360)
                plotly_full_width(fig_share)


if __name__ == "__main__":
    main()
