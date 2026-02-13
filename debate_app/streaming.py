"""
Real-time streaming and websocket support for SynapseForge.
Enables real-time updates of agent responses during collaborative synthesis.
"""
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, field
import time


@dataclass
class StreamEvent:
    """Event streamed to client during synthesis."""
    event_type: str  # "round_start", "agent_response", "round_complete", "synthesis_start", "synthesis_complete"
    round_number: int = 0
    agent_name: str = ""
    agent_role: str = ""
    content: str = ""
    cost: float = 0.0
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "round_number": self.round_number,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "content": self.content,
            "cost": self.cost,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {},
        }


class StreamingDebateManager:
    """
    Manages real-time streaming of debate progress.
    Notifies listeners of agent responses, rounds completion, and synthesis progress.
    """
    
    def __init__(self, callback: Optional[Callable[[StreamEvent], None]] = None):
        """
        Initialize streaming manager.
        
        Args:
            callback: Function to call when an event occurs (e.g., websocket emit)
        """
        self.callback = callback
        self.events: list[StreamEvent] = []
    
    def emit(self, event: StreamEvent) -> None:
        """Emit a streaming event."""
        event.timestamp = time.time()
        self.events.append(event)
        if self.callback:
            self.callback(event)
    
    def emit_round_start(self, round_number: int) -> None:
        """Notify that a round is starting."""
        self.emit(StreamEvent(
            event_type="round_start",
            round_number=round_number,
        ))
    
    def emit_agent_response(
        self,
        round_number: int,
        agent_name: str,
        agent_role: str,
        content: str,
        cost: float,
        confidence: float,
    ) -> None:
        """Notify that an agent has responded."""
        self.emit(StreamEvent(
            event_type="agent_response",
            round_number=round_number,
            agent_name=agent_name,
            agent_role=agent_role,
            content=content,
            cost=cost,
            metadata={"confidence": confidence},
        ))
    
    def emit_round_complete(self, round_number: int, consensus: float, round_cost: float) -> None:
        """Notify that a round is complete."""
        self.emit(StreamEvent(
            event_type="round_complete",
            round_number=round_number,
            metadata={"consensus": consensus, "round_cost": round_cost},
        ))
    
    def emit_synthesis_start(self) -> None:
        """Notify that synthesis is starting."""
        self.emit(StreamEvent(event_type="synthesis_start"))
    
    def emit_synthesis_complete(self, final_answer: str, total_cost: float) -> None:
        """Notify that synthesis is complete."""
        self.emit(StreamEvent(
            event_type="synthesis_complete",
            content=final_answer,
            cost=total_cost,
        ))
    
    def get_all_events(self) -> list[Dict[str, Any]]:
        """Return all recorded events."""
        return [event.to_dict() for event in self.events]
