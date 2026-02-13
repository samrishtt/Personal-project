"""
SynapseForge v3 — Research-Grade Collaborative AI Engine
Advanced features: Query classification, credence propagation, context pruning, benchmarking.
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class QueryType(Enum):
    """Query classification types."""
    FACTUAL = "factual"
    CAUSAL = "causal"
    ETHICAL = "ethical"
    CREATIVE = "creative"


@dataclass
class Claim:
    """A single claim with credence tracking."""
    agent_id: str
    claim: str
    credence: float = 0.8  # 0.0-1.0
    conflicts_with: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_id,
            "claim": self.claim,
            "credence": round(self.credence, 2),
            "conflicts_with": self.conflicts_with,
        }


@dataclass
class CredenceUpdate:
    """Tracks credence changes during debate."""
    claim: Claim
    original_credence: float
    new_credence: float
    reason: str  # e.g., "Verifier flagged", "Consensus boost", "Rebuttal penalty"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_summary": self.claim.claim[:100],
            "original": round(self.original_credence, 2),
            "updated": round(self.new_credence, 2),
            "reason": self.reason,
        }


class QueryClassifier:
    """Classifies queries to determine optimal agent roles."""
    
    KEYWORDS = {
        QueryType.FACTUAL: ["what", "who", "when", "where", "how many", "fact", "true", "false"],
        QueryType.CAUSAL: ["why", "cause", "effect", "because", "result", "lead to", "cause"],
        QueryType.ETHICAL: ["should", "moral", "right", "wrong", "ethical", "value", "good", "bad"],
        QueryType.CREATIVE: ["create", "imagine", "design", "novel", "idea", "story", "generate"],
    }
    
    @staticmethod
    def classify(query: str) -> QueryType:
        """Classify query type based on keywords."""
        query_lower = query.lower()
        
        # Count keyword matches
        scores = {}
        for qtype, keywords in QueryClassifier.KEYWORDS.items():
            scores[qtype] = sum(1 for kw in keywords if kw in query_lower)
        
        # Return type with highest score, default to factual
        if max(scores.values()) == 0:
            return QueryType.FACTUAL
        return max(scores, key=scores.get)
    
    @staticmethod
    def get_roles_for_type(query_type: QueryType) -> Dict[str, int]:
        """Get recommended agent roles for query type."""
        return {
            QueryType.FACTUAL: {"contributors": 2, "verifiers": 2, "stress_testers": 0},
            QueryType.CAUSAL: {"contributors": 2, "verifiers": 1, "stress_testers": 1},
            QueryType.ETHICAL: {"contributors": 3, "verifiers": 0, "stress_testers": 1},
            QueryType.CREATIVE: {"contributors": 3, "verifiers": 0, "stress_testers": 0},
        }[query_type]


class CredencePropagation:
    """Manages credence updates based on agent feedback."""
    
    VERIFIER_PENALTY = 0.5       # Claim flagged by verifier
    CONSENSUS_BOOST = 1.3        # Multiple agents agree
    REBUTTAL_PENALTY = 0.6       # Contradicted by stress-tester
    MAX_CREDENCE = 0.99
    
    @staticmethod
    def update_credence(
        claim: Claim,
        verifier_flagged: bool = False,
        consensus_agreement: int = 0,
        stress_test_rebuttal: bool = False,
    ) -> Tuple[float, str]:
        """
        Update claim credence based on feedback.
        Returns: (new_credence, reason)
        """
        new_credence = claim.credence
        reasons = []
        
        if verifier_flagged:
            new_credence *= CredencePropagation.VERIFIER_PENALTY
            reasons.append("Verifier flagged")
        
        if consensus_agreement >= 2:
            new_credence *= CredencePropagation.CONSENSUS_BOOST
            reasons.append(f"{consensus_agreement} agents agree")
        
        if stress_test_rebuttal:
            new_credence *= CredencePropagation.REBUTTAL_PENALTY
            reasons.append("Stress-tested and rebuted")
        
        # Cap at MAX_CREDENCE
        new_credence = min(new_credence, CredencePropagation.MAX_CREDENCE)
        
        reason = " + ".join(reasons) if reasons else "No changes"
        return new_credence, reason


class ContextPruning:
    """Manages context compression between rounds."""
    
    CREDENCE_THRESHOLD = 0.6
    MAX_TOKENS = 400
    
    @staticmethod
    def prune_context(claims: List[Claim], token_budget: int = 400) -> str:
        """
        Extract high-credence claims and conflicts, drop filler.
        Returns: Pruned context string (≤token_budget tokens)
        """
        # Filter claims above credence threshold
        high_credence = [c for c in claims if c.credence > ContextPruning.CREDENCE_THRESHOLD]
        
        pruned_lines = []
        for claim in high_credence:
            line = f"[{claim.agent_id}, {claim.credence:.0%}] {claim.claim}"
            if len(" ".join(pruned_lines) + " " + line) <= token_budget * 4:  # Rough token estimate
                pruned_lines.append(line)
        
        # Add conflicts if space remains
        conflicts = set()
        for claim in high_credence:
            if claim.conflicts_with:
                conflicts.update(claim.conflicts_with)
        
        if conflicts:
            pruned_lines.append("\nUnresolved conflicts: " + ", ".join(conflicts))
        
        return "\n".join(pruned_lines)


@dataclass
class BenchmarkResult:
    """Tracks performance metrics for evaluation."""
    query: str
    query_type: QueryType
    single_agent_answer: str = ""
    synapse_answer: str = ""
    factual_match: Optional[bool] = None
    hallucination_flags: int = 0
    consensus_round: int = 0
    final_credence: float = 0.0
    cost_usd: float = 0.0
    performance_vs_single: str = "equal"  # better|equal|worse
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "query_type": self.query_type.value,
            "single_agent_answer": self.single_agent_answer[:200],
            "synapse_answer": self.synapse_answer[:200],
            "factual_match": self.factual_match,
            "hallucination_flags": self.hallucination_flags,
            "consensus_round": self.consensus_round,
            "final_credence": round(self.final_credence, 2),
            "cost_usd": round(self.cost_usd, 6),
            "performance_vs_single": self.performance_vs_single,
        }


@dataclass
class SynthesizerOutput:
    """Final output from v3 synthesizer."""
    query_type: str
    answer: str
    confidence: float  # 0.0-1.0
    consensus_round: int
    credence_trace: List[Dict[str, Any]]
    conflicts_resolved: List[str]
    hallucination_flags: int
    vs_single_agent: str
    cost_usd: float
    
    def to_json(self) -> str:
        return json.dumps({
            "query_type": self.query_type,
            "answer": self.answer,
            "confidence": round(self.confidence, 2),
            "consensus_round": self.consensus_round,
            "credence_trace": self.credence_trace,
            "conflicts_resolved": self.conflicts_resolved,
            "hallucination_flags": self.hallucination_flags,
            "vs_single_agent": self.vs_single_agent,
            "cost_usd": round(self.cost_usd, 6),
        }, indent=2)
