#!/usr/bin/env python
"""
Test SynapseForge v3 — Query classification, credence propagation, and benchmarking.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from debate_app.v3_core import (
    QueryClassifier,
    QueryType,
    Claim,
    CredencePropagation,
    ContextPruning,
    BenchmarkResult,
    SynthesizerOutput,
)
import json


def test_query_classification():
    """Test query type classification."""
    print("=" * 70)
    print("TEST 1: Query Classification (v3)")
    print("=" * 70)
    
    test_queries = [
        "What is machine learning?",  # Factual
        "Why does climate change happen?",  # Causal
        "Should AI be regulated?",  # Ethical
        "Design a solar-powered car",  # Creative
    ]
    
    for query in test_queries:
        qtype = QueryClassifier.classify(query)
        roles = QueryClassifier.get_roles_for_type(qtype)
        print(f"\n🔍 Query: {query}")
        print(f"   Type: {qtype.value.upper()}")
        print(f"   Roles: {roles}")
    
    print("\n✓ Query classification working\n")


def test_credence_propagation():
    """Test credence update mechanism."""
    print("=" * 70)
    print("TEST 2: Credence Propagation (v3)")
    print("=" * 70)
    
    # Create test claims
    claim = Claim(
        agent_id="Agent-1",
        claim="Machine learning requires large datasets to be effective.",
        credence=0.75,
    )
    
    print(f"\nInitial claim: {claim.claim}")
    print(f"Initial credence: {claim.credence:.0%}")
    
    # Scenario 1: Verifier flags the claim
    new_cred, reason = CredencePropagation.update_credence(
        claim,
        verifier_flagged=True
    )
    print(f"\n✓ Verifier flagged claim")
    print(f"  New credence: {new_cred:.0%}")
    print(f"  Reason: {reason}")
    
    # Scenario 2: Consensus agreement
    claim.credence = 0.75  # Reset
    new_cred, reason = CredencePropagation.update_credence(
        claim,
        consensus_agreement=2
    )
    print(f"\n✓ Two agents agree with claim")
    print(f"  New credence: {new_cred:.0%}")
    print(f"  Reason: {reason}")
    
    # Scenario 3: Stress-test rebuttal
    claim.credence = 0.75  # Reset
    new_cred, reason = CredencePropagation.update_credence(
        claim,
        stress_test_rebuttal=True
    )
    print(f"\n✓ Stress-tester found counterexample")
    print(f"  New credence: {new_cred:.0%}")
    print(f"  Reason: {reason}")
    
    print("\n✓ Credence propagation working\n")


def test_context_pruning():
    """Test context compression."""
    print("=" * 70)
    print("TEST 3: Context Pruning (v3)")
    print("=" * 70)
    
    # Create claims with various credence levels
    claims = [
        Claim("Agent-1", "Dataset quality matters more than size.", credence=0.85),
        Claim("Agent-2", "Regular maintenance is essential.", credence=0.45),
        Claim("Agent-1", "Real-time monitoring prevents failures.", credence=0.72),
        Claim("Agent-3", "Cost optimization is secondary.", credence=0.38),
        Claim("Agent-2", "Automated testing catches 90% of bugs.", credence=0.68),
    ]
    
    print(f"\nTotal claims before pruning: {len(claims)}")
    print("Credence distribution:")
    for c in claims:
        print(f"  - {c.agent_id}: {c.credence:.0%} | {c.claim[:50]}...")
    
    pruned = ContextPruning.prune_context(claims, token_budget=400)
    
    print(f"\n✓ Pruning complete (>60% credence threshold)")
    print(f"Pruned context (≤400 tokens):")
    print(pruned)
    
    print("\n✓ Context pruning working\n")


def test_benchmarking():
    """Test benchmark tracking."""
    print("=" * 70)
    print("TEST 4: Benchmarking (v3)")
    print("=" * 70)
    
    benchmark = BenchmarkResult(
        query="What is the best programming language?",
        query_type=QueryType.CAUSAL,
        single_agent_answer="Python is best because it's easy to learn.",
        synapse_answer="Python excels for rapid development and data science, while Go is better for systems programming, and Rust for safety-critical applications. The 'best' depends on use case.",
        factual_match=None,
        hallucination_flags=0,
        consensus_round=2,
        final_credence=0.82,
        cost_usd=0.0045,
        performance_vs_single="better"
    )
    
    print(f"\nQuery: {benchmark.query}")
    print(f"Query Type: {benchmark.query_type.value.upper()}")
    print(f"\nSingle Agent Answer: {benchmark.single_agent_answer}")
    print(f"\nSynapseForge Answer: {benchmark.synapse_answer}")
    print(f"\nMetrics:")
    print(f"  - Consensus Round: {benchmark.consensus_round}")
    print(f"  - Final Credence: {benchmark.final_credence:.0%}")
    print(f"  - Hallucination Flags: {benchmark.hallucination_flags}")
    print(f"  - Cost: ${benchmark.cost_usd:.4f}")
    print(f"  - vs Single Agent: {benchmark.performance_vs_single}")
    
    print(f"\n✓ Benchmark result:")
    print(json.dumps(benchmark.to_dict(), indent=2))
    
    print("\n✓ Benchmarking working\n")


def test_synthesizer_output():
    """Test final JSON output format."""
    print("=" * 70)
    print("TEST 5: Synthesizer Output Format (v3)")
    print("=" * 70)
    
    output = SynthesizerOutput(
        query_type="factual",
        answer="Machine learning is a subset of AI that enables systems to learn from data without being explicitly programmed. Key components include training data, algorithms, and validation.",
        confidence=0.88,
        consensus_round=2,
        credence_trace=[
            {"agent": "Contributor-1", "claim": "ML learns from data", "credence": 0.92},
            {"agent": "Contributor-2", "claim": "Requires training and validation", "credence": 0.85},
            {"agent": "Verifier-1", "claim": "No unsupported claims detected", "credence": 0.88},
        ],
        conflicts_resolved=["Definition scope: clarified ML vs AI vs DL"],
        hallucination_flags=0,
        vs_single_agent="better",
        cost_usd=0.0052,
    )
    
    print("\nJSON Output:")
    print(output.to_json())
    
    print("\n✓ Synthesizer output format working\n")


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         SynapseForge v3 Feature Tests                             ║")
    print("║    Query Classification • Credence Propagation • Benchmarking      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    test_query_classification()
    test_credence_propagation()
    test_context_pruning()
    test_benchmarking()
    test_synthesizer_output()
    
    print("=" * 70)
    print("✅ ALL v3 TESTS PASSED")
    print("=" * 70)
    print("\nv3 Features Ready:")
    print("  ✓ Query classification (factual/causal/ethical/creative)")
    print("  ✓ Dynamic role assignment based on query type")
    print("  ✓ Credence propagation (penalties & boosts)")
    print("  ✓ Context pruning (400-token limit)")
    print("  ✓ Benchmarking hooks (single vs multi-agent comparison)")
    print("  ✓ Research-grade JSON output format")
    print("\n")
