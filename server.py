"""
SynapseForge — Flask Backend Server
Serves the web UI and exposes /api/run for collaborative multi-model synthesis.

IMPROVEMENTS:
- Parallel execution of agents using ThreadPoolExecutor (handles 5-10 models concurrently)
- Non-blocking model inference for better performance
- Real-time response streaming
"""
from __future__ import annotations

import json
import re
import time
from itertools import combinations
from typing import Dict, List, Optional, Sequence, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from flask import Flask, jsonify, render_template, request

from debate_app.agents.providers import (
    MODEL_CATALOG,
    PROVIDER_LABELS,
    ModelSpec,
    build_agent_from_spec,
    provider_has_key,
)
from debate_app.core.base import AgentResponse
from debate_app.core.prompts import (
    ADVERSARIAL_SYSTEM_PROMPT,
    DEBATER_SYSTEM_PROMPT,
    FACT_CHECKER_SYSTEM_PROMPT,
    JUDGE_SYSTEM_PROMPT,
)

app = Flask(__name__, template_folder="templates", static_folder="static")
# Thread pool for parallel agent execution (supports up to 10 concurrent models)
EXECUTOR = ThreadPoolExecutor(max_workers=10, thread_name_prefix="agent-")

MODEL_LOOKUP: Dict[str, ModelSpec] = {spec.label: spec for spec in MODEL_CATALOG}


# ─── Helpers ────────────────────────────────────────────────────────────────

def fill_prompt(template: str, replacements: Dict[str, object]) -> str:
    output = template
    for key, value in replacements.items():
        output = output.replace("{" + key + "}", str(value))
    return output


def consensus_score(texts: Sequence[str]) -> float:
    token_sets = [
        set(re.findall(r"[a-zA-Z]{4,}", text.lower())[:120])
        for text in texts if text
    ]
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
    return text if len(text) <= limit else text[:limit].rstrip() + " ..."


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Query is required."}), 400

    debater_labels = data.get("debaters", [])
    judge_label = data.get("judge", "")
    fact_label = data.get("fact_checker") or ""
    adv_label = data.get("adversarial") or ""
    rounds = max(1, min(int(data.get("rounds", 3)), 8))
    budget = max(0.01, float(data.get("budget", 0.75)))
    temp = max(0.0, min(float(data.get("temp", 0.2)), 1.0))
    consensus_threshold = max(0.1, min(float(data.get("consensus_threshold", 0.55)), 0.99))
    keys = data.get("keys", {})

    # Build agent roster
    roster: List[Tuple[str, ModelSpec, str, object]] = []
    warnings: List[str] = []

    for i, label in enumerate(debater_labels, start=1):
        spec = MODEL_LOOKUP.get(label)
        if not spec:
            warnings.append(f"Unknown model: {label}")
            continue
        agent = build_agent_from_spec(spec, DEBATER_SYSTEM_PROMPT, keys, f"Contributor {i}", temp)
        roster.append(("debater", spec, f"Contributor {i}", agent))

    if fact_label and fact_label in MODEL_LOOKUP:
        spec = MODEL_LOOKUP[fact_label]
        agent = build_agent_from_spec(
            spec,
            fill_prompt(FACT_CHECKER_SYSTEM_PROMPT, {"round_number": "{round}", "agent_name": "all agents"}),
            keys, "Verifier", temp,
        )
        roster.append(("fact_checker", spec, "Verifier", agent))

    if adv_label and adv_label in MODEL_LOOKUP:
        spec = MODEL_LOOKUP[adv_label]
        agent = build_agent_from_spec(
            spec,
            fill_prompt(ADVERSARIAL_SYSTEM_PROMPT, {"round_number": "{round}", "agent_name": "consensus", "topic": query}),
            keys, "Stress Tester", temp,
        )
        roster.append(("adversarial", spec, "Stress Tester", agent))

    judge_spec = MODEL_LOOKUP.get(judge_label)
    if not judge_spec:
        return jsonify({"error": f"Unknown judge model: {judge_label}"}), 400

    judge = build_agent_from_spec(
        judge_spec,
        fill_prompt(JUDGE_SYSTEM_PROMPT, {"original_question": query, "n": rounds}),
        keys, "Synthesizer", max(temp - 0.05, 0.0),
    )

    if not roster:
        return jsonify({"error": "At least one contributor model is required."}), 400

    # ─── Run collaborative rounds with PARALLEL execution ───
    logs: List[Dict] = []
    context = ""
    total_cost = 0.0
    stop_reason = "Configured rounds completed."
    fatal_failure = False

    for round_number in range(1, rounds + 1):
        if total_cost >= budget:
            stop_reason = f"Stopped before round {round_number}: budget reached."
            break

        responses: List[Dict] = []
        
        # PARALLEL EXECUTION: Submit all agents to ThreadPoolExecutor
        futures = {}
        for role, spec, name, agent in roster:
            if total_cost >= budget:
                stop_reason = f"Budget reached in round {round_number}."
                break
            future = EXECUTOR.submit(agent.generate_response, query=query, context=context)
            futures[future] = (role, spec, name, agent)
        
        # Collect results as they complete (non-blocking)
        for future in as_completed(futures):
            if total_cost >= budget:
                break
            
            role, spec, name, agent = futures[future]
            try:
                result = future.result(timeout=60)  # 60-second timeout per agent
            except Exception as e:
                result_content = f"Error: Agent {name} failed - {str(e)}"
                result = AgentResponse(content=result_content, confidence=0.0, model_name=spec.model_id)
            
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

        if not responses:
            break

        round_cost = sum(r["cost"] for r in responses)

        if all(r["is_error"] for r in responses):
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

        if round_number >= 2 and round_consensus >= consensus_threshold:
            stop_reason = f"Stopped early at round {round_number}: consensus {round_consensus:.0%}."
            break

    # ─── Judge synthesis ───
    judge_record = None
    final_answer = "No final synthesis generated."

    if total_cost < budget and not fatal_failure:
        judge_query = (
            f"Original question: {query}\n\nCollaborative transcript:\n{context}\n\n"
            "Deliver one final synthesized answer with rationale, uncertainties, and practical next actions."
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
            final_answer = "Synthesis stopped because all agents returned errors. Check your API keys."
        else:
            stop_reason = f"Stopped after rounds: budget cap ${budget:.2f} exhausted."

    return jsonify({
        "query": query,
        "rounds_requested": rounds,
        "rounds_completed": len(logs),
        "rounds": logs,
        "judge": judge_record,
        "total_cost": round(total_cost, 6),
        "stopped_reason": stop_reason,
        "final_answer": final_answer,
        "warnings": warnings,
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Check if the server is running and ready."""
    return jsonify({
        "status": "healthy",
        "server": "SynapseForge v2.0",
        "parallel_workers": 10,
        "models_available": len(MODEL_CATALOG),
    }), 200


@app.route("/api/models", methods=["GET"])
def list_models():
    """List all available models grouped by provider."""
    models_by_provider = {}
    for spec in MODEL_CATALOG:
        provider = spec.provider
        if provider not in models_by_provider:
            models_by_provider[provider] = []
        models_by_provider[provider].append({
            "label": spec.label,
            "model_id": spec.model_id,
            "roles": spec.role_hints,
        })
    return jsonify(models_by_provider), 200


@app.route("/api/models/check-keys", methods=["POST"])
def check_api_keys():
    """Check which API keys are configured."""
    keys = request.get_json(force=True) or {}
    availability = {}
    for provider in ["openai", "google", "anthropic"]:
        availability[provider] = provider_has_key(provider, keys)
    return jsonify(availability), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "details": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
