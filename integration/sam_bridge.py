"""
SynapseForge + SAM-AI  ·  V2 Integration Bridge
==================================================
Connects SynapseForge's multi-agent LLM debate engine with SAM-AI's
neuro-symbolic reasoning analysis pipeline.

This module provides:
- `analyse_text_response`:  Run SAM-AI analysis on any LLM text output
- `compute_truth_level`:    Compute a truth-level / believability score
- `build_analysis_report`:  Generate a full analysis report dict for the UI
"""

from __future__ import annotations

import os
import sys
import math
from typing import Any, Dict, List, Optional

# ── Ensure SAM-AI is importable ─────────────────────────────────────────────
_SAM_AI_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "V1")
)
if _SAM_AI_ROOT not in sys.path:
    sys.path.insert(0, _SAM_AI_ROOT)

from sam_ai.nlp_parser import NLPParser
from sam_ai.reasoning_engine import ReasoningEngine
from sam_ai.meta_evaluator import MetaEvaluator, MetaEvaluation
from sam_ai.uncertainty_model import UncertaintyModel, UncertaintyEstimate
from sam_ai.self_corrector import SelfCorrector, CorrectionResult


# ── Singleton instances (heavy objects, create once) ────────────────────────
_parser = NLPParser()
_engine = ReasoningEngine()
_evaluator = MetaEvaluator()
_uncertainty = UncertaintyModel()
_corrector = SelfCorrector(
    reasoning_engine=_engine,
    meta_evaluator=_evaluator,
    uncertainty_model=_uncertainty,
)


# ═══════════════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════════════

def compute_truth_level(
    text: str,
    llm_confidence: float = 0.5,
) -> Dict[str, Any]:
    """
    Compute a 'truth level' / believability score for an LLM response.

    This runs a lightweight SAM-AI analysis:
    1. Parse the text with the NLP parser
    2. Run the Reasoning Engine
    3. Compute the Uncertainty Estimate (calibrated confidence)
    4. Return a compact dict with truth metrics

    Parameters
    ----------
    text : str
        The LLM response text to evaluate.
    llm_confidence : float
        The LLM's self-reported confidence (0-1).

    Returns
    -------
    dict with keys:
        truth_score, reliability_rating, calibrated_confidence,
        entropy, llm_confidence, category
    """
    try:
        task = _parser.parse(text)
        result = _engine.solve(task)
        trace_dict = result.trace.to_dict()
        category = task.get("category", "unknown")

        ue = _uncertainty.estimate(trace_dict, category)

        # Blend SAM-AI calibrated confidence with LLM self-reported confidence
        sam_conf = ue.calibrated_confidence
        blended = 0.6 * sam_conf + 0.4 * llm_confidence

        return {
            "truth_score": round(blended, 4),
            "reliability_rating": ue.reliability_rating,
            "calibrated_confidence": round(sam_conf, 4),
            "entropy": round(ue.entropy, 4),
            "llm_confidence": round(llm_confidence, 4),
            "category": category,
            "sam_answer": result.answer,
        }
    except Exception as e:
        return {
            "truth_score": round(llm_confidence * 0.7, 4),
            "reliability_rating": "UNKNOWN",
            "calibrated_confidence": 0.0,
            "entropy": 0.0,
            "llm_confidence": round(llm_confidence, 4),
            "category": "unknown",
            "sam_answer": None,
            "error": str(e),
        }


def run_full_analysis(
    text: str,
    enable_correction: bool = True,
) -> Dict[str, Any]:
    """
    Run the full SAM-AI pipeline on text and return a comprehensive report.

    Pipeline:
    1. NLP Parse → structured task
    2. Reasoning Engine → structured trace
    3. Meta-Evaluator → quality scores + fallacy detection
    4. Uncertainty Model → calibrated confidence
    5. Self-Corrector (optional) → refined answer

    Parameters
    ----------
    text : str
        The final synthesised answer text to analyse.
    enable_correction : bool
        Whether to run the self-correction loop.

    Returns
    -------
    dict with full analysis results for UI rendering.
    """
    try:
        # 1. Parse
        task = _parser.parse(text)
        category = task.get("category", "unknown")

        # 2. Reasoning
        result = _engine.solve(task)
        trace_dict = result.trace.to_dict()

        # 3. Meta-evaluation
        meta_eval = _evaluator.evaluate(trace_dict)

        # 4. Uncertainty
        ue = _uncertainty.estimate(trace_dict, category)

        # 5. Self-correction
        if enable_correction:
            cr = _corrector.correct(task, result, meta_eval)
            if cr.was_corrected and cr.final_result is not None:
                trace_dict = cr.final_result.trace.to_dict()
                meta_eval = _evaluator.evaluate(trace_dict)
                ue = _uncertainty.estimate(trace_dict, category)
        else:
            cr = CorrectionResult()
            cr.original_answer = result.answer
            cr.corrected_answer = result.answer
            cr.quality_before = meta_eval.overall_quality
            cr.quality_after = meta_eval.overall_quality
            cr.final_result = result

        return {
            "success": True,
            "category": category,
            "task": task,
            "reasoning": {
                "answer": cr.corrected_answer,
                "trace": trace_dict,
                "overall_confidence": result.overall_confidence,
            },
            "meta_evaluation": meta_eval.to_dict(),
            "uncertainty": ue.to_dict(),
            "correction": cr.to_dict(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "category": "unknown",
            "task": {},
            "reasoning": {"answer": None, "trace": {}, "overall_confidence": 0.0},
            "meta_evaluation": MetaEvaluation().to_dict(),
            "uncertainty": UncertaintyEstimate().to_dict(),
            "correction": CorrectionResult().to_dict(),
        }


def analyse_debate_transcript(
    individual_responses: List[Dict[str, Any]],
    final_synthesis: str,
    original_query: str,
) -> Dict[str, Any]:
    """
    Analyse the full debate output.

    Parameters
    ----------
    individual_responses : list of dict
        Each dict has keys: agent, content, confidence
    final_synthesis : str
        The judge's final synthesised answer.
    original_query : str
        The user's original question.

    Returns
    -------
    dict with:
        individual_truth_levels, synthesis_analysis
    """
    # 1. Truth levels for each individual response
    individual_truth = []
    for resp in individual_responses:
        truth = compute_truth_level(
            resp.get("content", ""),
            resp.get("confidence", 0.5),
        )
        truth["agent"] = resp.get("agent", "Unknown")
        truth["model"] = resp.get("model", "unknown")
        individual_truth.append(truth)

    # 2. Full analysis on the final synthesis
    synthesis_analysis = run_full_analysis(final_synthesis)

    return {
        "original_query": original_query,
        "individual_truth_levels": individual_truth,
        "synthesis_analysis": synthesis_analysis,
    }
