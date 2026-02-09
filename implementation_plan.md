# DebateMind: Research-Grade Multi-Agent Consensus System

## Overview
DebateMind is a high-level multi-agent system designed to produce accurate, nuanced answers through structured debate, peer review, and consensus synthesis. It emphasizes cost-efficiency, reproducibility, and measurable improvements over single-agent responses.

## Core Features
1.  **Cost & Token Management**:
    -   Global budget caps (e.g., $0.10 per query).
    -   Per-agent token limits.
    -   Real-time cost tracking using model specific pricing.
2.  **Efficiency & Control**:
    -   **Early Stopping**: Detect consensus to stop debates early.
    -   **Context Pruning**: Use rolling summaries instead of full history to save context window.
3.  **Specialized Agents**:
    -   **Debaters**: Cheaper models (GPT-4o-mini, Gemini Flash) for generating arguments.
    -   **Fact-Checker**: dedicated agent to verify claims.
    -   **Judge**: Stronger model (GPT-4o, Claude 3.5 Sonnet) for final synthesis and scoring.
4.  **Structured Evaluation**:
    -   Rubric-based judging (Accuracy, Nuance, Completeness).
    -   Confidence scores.
    -   Side-by-side comparison (Single Agent vs. Debate Consensus).

## Architecture Update
-   **`TokenMonitor`**: centralized tracking of tokens and cost.
-   **`DebateManager`**: Enhanced with "rounds" logic that checks for convergence.
-   **`JudgeAgent`**: A specialized agent that outputs structured JSON evaluations.

## Roadmap
1.  **Infrastructure**: Implement `TokenMonitor` and update `Agent` to report usage.
2.  **Orchestration**: Implement "Cheap Debate / Expensive Judge" workflow.
3.  **Specialists**: Create Fact-Checker and Devil's Advocate roles.
4.  **UI Upgrade**: Show cost widgets, confidence meters, and definitive "Winner" logic.
