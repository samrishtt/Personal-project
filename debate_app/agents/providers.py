import os
import random
from typing import Optional, Dict
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from ..core.base import Agent, AgentResponse
from ..core.pricing import estimate_cost

class OpenAIAgent(Agent):
    def __init__(self, name: str = "GPT-4o", model_name: str = "gpt-4o", api_key: str = None, system_prompt: str = ""):
        if not system_prompt:
             # Default system prompt
             pass # Will be handled by base if needed, or overridden by caller
        
        super().__init__(name=name, description="OpenAI GPT Model", system_prompt=system_prompt, model=None)
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.model = ChatOpenAI(model=model_name, api_key=self.api_key)
        else:
            self.model = None

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        if not self.model:
            return AgentResponse(content="Error: OpenAI API Key not provided.", confidence=0.0)
            
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Original Question: {query}\n\nContext from previous debate rounds:\n{context or 'No previous context.'}\n\nPlease provide your answer, critiquing previous answers if they exist.")
        ]
        
        try:
            full_response = self.model.invoke(messages)
            content = full_response.content
            
            # Extract usage
            usage = full_response.response_metadata.get("token_usage", {})
            input_tokens = usage.get("prompt_tokens", len(str(messages))/4) # Fallback
            output_tokens = usage.get("completion_tokens", len(content)/4) # Fallback
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
            
            cost = estimate_cost(self.model_name, input_tokens, output_tokens)
            
            return AgentResponse(
                content=content,
                confidence=0.9, # Placeholder, could parse from content if structured output used
                token_usage={"input": input_tokens, "output": output_tokens, "total": total_tokens},
                cost=cost,
                model_name=self.model_name
            )
        except Exception as e:
            return AgentResponse(content=f"Error: {str(e)}", confidence=0.0)

class GeminiAgent(Agent):
    def __init__(self, name: str = "Gemini Pro", model_name: str = "gemini-1.5-pro", api_key: str = None, system_prompt: str = ""):
        super().__init__(name=name, description="Google Gemini Model", system_prompt=system_prompt, model=None)
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.model = ChatGoogleGenerativeAI(model=model_name, google_api_key=self.api_key)
        else:
            self.model = None

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        if not self.model:
            return AgentResponse(content="Error: Google API Key not provided.", confidence=0.0)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Original Question: {query}\n\nContext from previous debate rounds:\n{context or 'No previous context.'}\n\nPlease provide your answer, critiquing previous answers if they exist.")
        ]
        
        try:
            full_response = self.model.invoke(messages)
            content = full_response.content
            
            # Gemini usage metadata might vary
            usage = full_response.response_metadata.get("usage_metadata", {})
            input_tokens = usage.get("prompt_token_count", len(str(messages))/4)
            output_tokens = usage.get("candidates_token_count", len(content)/4)
            total_tokens = usage.get("total_token_count", input_tokens + output_tokens)
            
            cost = estimate_cost(self.model_name, input_tokens, output_tokens)
            
            return AgentResponse(
                content=content,
                confidence=0.85, 
                token_usage={"input": input_tokens, "output": output_tokens, "total": total_tokens},
                cost=cost,
                model_name=self.model_name
            )
        except Exception as e:
            return AgentResponse(content=f"Error: {str(e)}", confidence=0.0)


class AnthropicAgent(Agent):
    def __init__(self, name: str = "Claude Opus", model_name: str = "claude-3-opus-20240229", api_key: str = None, system_prompt: str = ""):
        super().__init__(name=name, description="Anthropic Claude Model", system_prompt=system_prompt, model=None)
        self.model_name = model_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.model = ChatAnthropic(model=model_name, anthropic_api_key=self.api_key)
        else:
            self.model = None

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        if not self.model:
            return AgentResponse(content="Error: Anthropic API Key not provided.", confidence=0.0)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Original Question: {query}\n\nContext from previous debate rounds:\n{context or 'No previous context.'}\n\nPlease provide your answer, critiquing previous answers if they exist.")
        ]
        
        try:
            full_response = self.model.invoke(messages)
            content = full_response.content
            
            usage = full_response.response_metadata.get("usage", {})
            input_tokens = usage.get("input_tokens", len(str(messages))/4)
            output_tokens = usage.get("output_tokens", len(content)/4)
            
            cost = estimate_cost(self.model_name, input_tokens, output_tokens)

            return AgentResponse(
                content=content,
                confidence=0.95,
                token_usage={"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens},
                cost=cost,
                model_name=self.model_name
            )
        except Exception as e:
             return AgentResponse(content=f"Error: {str(e)}", confidence=0.0)


class MockAgent(Agent):
    """Simulates an agent for testing/demo purposes without costing tokens."""
    def __init__(self, name: str, behavior: str):
        system_prompt = f"You are a mock agent named {name}. You always respond in a {behavior} way."
        super().__init__(name=name, description="Mock Agent", system_prompt=system_prompt, model=None)
        self.behavior = behavior

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        content = f"[{self.name} ({self.behavior})]: I think the answer to '{query}' is X because of my {self.behavior} nature. (Mock response)"
        return AgentResponse(
            content=content,
            confidence=0.5,
            token_usage={"input": 100, "output": 50, "total": 150},
            cost=0.0,
            model_name="mock-agent"
        )
