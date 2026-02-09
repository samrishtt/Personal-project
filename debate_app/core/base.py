from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time
import random

@dataclass
class AgentResponse:
    content: str
    confidence: float = 0.0 # 0.0 to 1.0
    token_usage: Dict[str, int] = field(default_factory=lambda: {"input": 0, "output": 0, "total": 0})
    cost: float = 0.0
    model_name: str = "unknown"

class Agent:
    def __init__(self, name: str, description: str, system_prompt: str, model: Any):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.model = model
        self.total_cost = 0.0
        self.total_tokens = 0
        
    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        """
        Generates a response from the agent.
        Must return an AgentResponse object with content, confidence, and usage stats.
        """
        raise NotImplementedError("Subclasses must implement generate_response")

class DebateManager:
    def __init__(self, agents: List[Agent], judge_agent: Agent = None, rounds: int = 3, cost_limit: float = 0.5):
        self.agents = agents
        self.judge_agent = judge_agent # Specialized agent for synthesis/evaluation
        self.rounds = rounds
        self.cost_limit = cost_limit
        self.history = []
        self.conversation_cost = 0.0
        self.stopped_early = False

    def start_debate(self, query: str) -> Dict[str, Any]:
        """
        Orchestrates the debate, checking for convergence and cost limits.
        Returns a dictionary with the final synthesis, full history, and metrics.
        """
        self.history = [] # Reset history
        self.conversation_cost = 0.0
        self.stopped_early = False
        
        current_context = ""
        final_consensus = ""
        
        # 1. Rounds
        for round_num in range(self.rounds):
            # Check Cost Limit
            if self.conversation_cost >= self.cost_limit:
                self.stopped_early = True
                break
            
            round_responses_text = []
            round_data = {"round": round_num + 1, "responses": []}
            
            for agent in self.agents:
                try:
                    # Provide recent context (last round only to save tokens/cost if needed, or full context)
                    # For simplicity, passing full rolling context
                    response_obj = agent.generate_response(query, current_context)
                    
                    # Update metrics
                    self.conversation_cost += response_obj.cost
                    agent.total_cost += response_obj.cost
                    agent.total_tokens += response_obj.token_usage.get("total", 0)
                    
                    # Store response
                    round_responses_text.append(f"{agent.name}: {response_obj.content}")
                    round_data["responses"].append({
                        "agent": agent.name,
                        "content": response_obj.content,
                        "cost": response_obj.cost
                    })
                    
                except Exception as e:
                    print(f"Agent {agent.name} failed: {e}")
            
            # Update Context
            current_context += f"\nRound {round_num + 1}:\n" + "\n".join(round_responses_text) + "\n"
            self.history.append(round_data)

        # 2. Final Synthesis by Judge
        if self.judge_agent:
            try:
                synthesis_prompt = f"Review the following debate on '{query}':\n{current_context}\n\nProvide a final, authoritative answer. Cite the strongest arguments. Point out any consensus or remaining disagreements."
                final_resp = self.judge_agent.generate_response(synthesis_prompt, context="")
                final_consensus = final_resp.content
                self.conversation_cost += final_resp.cost
            except Exception as e:
                final_consensus = f"Error synthesizing final answer: {e}"
        else:
            final_consensus = "No judge agent configured. Debate ended."

        return {
            "final_answer": final_consensus,
            "history": self.history,
            "total_cost": self.conversation_cost,
            "rounds_completed": round_num + 1
        }
