from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..core.base import Agent, AgentResponse
from ..core.pricing import estimate_cost

PROVIDER_LABELS = {
    "openai": "OpenAI",
    "google": "Google",
    "anthropic": "Anthropic",
    "openrouter": "OpenRouter",
    "grok": "xAI (Grok)",
    "mock": "Mock",
}

PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "grok": "XAI_API_KEY",
    "mock": "",
}


@dataclass(frozen=True)
class ModelSpec:
    label: str
    provider: str
    model_id: str
    role_hints: Tuple[str, ...] = ("debater",)


MODEL_CATALOG: List[ModelSpec] = [
    ModelSpec(
        label="OpenAI GPT-4o",
        provider="openai",
        model_id="gpt-4o",
        role_hints=("debater", "judge", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="OpenAI GPT-4o mini",
        provider="openai",
        model_id="gpt-4o-mini",
        role_hints=("debater", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="OpenAI GPT-3.5 Turbo",
        provider="openai",
        model_id="gpt-3.5-turbo",
        role_hints=("debater",),
    ),
    ModelSpec(
        label="Google Gemini 1.5 Pro",
        provider="google",
        model_id="gemini-1.5-pro-latest",
        role_hints=("debater", "judge", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="Google Gemini 1.5 Flash",
        provider="google",
        model_id="gemini-1.5-flash-latest",
        role_hints=("debater", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="Anthropic Claude 3 Opus",
        provider="anthropic",
        model_id="claude-3-opus-20240229",
        role_hints=("debater", "judge", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="Anthropic Claude 3 Haiku",
        provider="anthropic",
        model_id="claude-3-haiku-20240307",
        role_hints=("debater", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="xAI Grok 2",
        provider="grok",
        model_id="grok-2",
        role_hints=("debater", "judge", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="xAI Grok Beta",
        provider="grok",
        model_id="grok-beta",
        role_hints=("debater",),
    ),
    ModelSpec(
        label="OpenRouter Auto",
        provider="openrouter",
        model_id="openrouter/auto",
        role_hints=("debater", "judge", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="OpenRouter DeepSeek V3",
        provider="openrouter",
        model_id="deepseek/deepseek-chat",
        role_hints=("debater", "fact_checker", "adversarial"),
    ),
    ModelSpec(
        label="Mock Skeptic",
        provider="mock",
        model_id="mock-skeptic",
        role_hints=("debater",),
    ),
    ModelSpec(
        label="Mock Optimist",
        provider="mock",
        model_id="mock-optimist",
        role_hints=("debater",),
    ),
    ModelSpec(
        label="Mock Fact Checker",
        provider="mock",
        model_id="mock-fact-checker",
        role_hints=("fact_checker",),
    ),
    ModelSpec(
        label="Mock Challenger",
        provider="mock",
        model_id="mock-adversarial",
        role_hints=("adversarial",),
    ),
    ModelSpec(
        label="Mock Judge",
        provider="mock",
        model_id="mock-judge",
        role_hints=("judge",),
    ),
]

MODEL_LOOKUP = {spec.label: spec for spec in MODEL_CATALOG}


def normalize_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    aliases = {
        "gemini": "google",
        "claude": "anthropic",
        "openai": "openai",
        "google": "google",
        "anthropic": "anthropic",
        "openrouter": "openrouter",
        "grok": "grok",
        "xai": "grok",
        "mock": "mock",
    }
    return aliases.get(normalized, normalized)


def list_model_specs(provider: Optional[str] = None, role: Optional[str] = None) -> List[ModelSpec]:
    selected_provider = normalize_provider(provider) if provider else None
    selected_role = (role or "").strip().lower()

    specs = MODEL_CATALOG
    if selected_provider:
        specs = [spec for spec in specs if spec.provider == selected_provider]
    if selected_role:
        specs = [spec for spec in specs if selected_role in spec.role_hints]
    return specs


def get_model_spec_by_label(label: str) -> Optional[ModelSpec]:
    return MODEL_LOOKUP.get(label)


def build_custom_model_spec(
    provider: str,
    model_id: str,
    label: Optional[str] = None,
    role_hints: Optional[Sequence[str]] = None,
) -> ModelSpec:
    provider_name = normalize_provider(provider)
    if provider_name not in PROVIDER_LABELS:
        raise ValueError(f"Unsupported provider '{provider}'.")

    normalized_model_id = (model_id or "").strip()
    if not normalized_model_id:
        raise ValueError("Custom model id cannot be empty.")

    normalized_roles = tuple(r.strip().lower() for r in (role_hints or ("debater",)) if r.strip())
    display_label = label or f"{PROVIDER_LABELS[provider_name]} Custom ({normalized_model_id})"

    return ModelSpec(
        label=display_label,
        provider=provider_name,
        model_id=normalized_model_id,
        role_hints=normalized_roles or ("debater",),
    )


def resolve_provider_key(provider: str, explicit_keys: Optional[Dict[str, str]] = None) -> str:
    provider_name = normalize_provider(provider)
    key_candidates = explicit_keys or {}

    provided_key = (
        key_candidates.get(provider_name)
        or key_candidates.get(f"{provider_name}_key")
        or ""
    ).strip()
    if provided_key:
        return provided_key

    env_var = PROVIDER_ENV_KEYS.get(provider_name, "")
    return os.getenv(env_var, "").strip() if env_var else ""


def provider_has_key(provider: str, explicit_keys: Optional[Dict[str, str]] = None) -> bool:
    if normalize_provider(provider) == "mock":
        return True
    return bool(resolve_provider_key(provider, explicit_keys))


def _coerce_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        fragments: List[str] = []
        for part in content:
            if isinstance(part, str):
                fragments.append(part)
            elif isinstance(part, dict):
                text = part.get("text")
                if text:
                    fragments.append(str(text))
        return "\n".join(fragments)
    return str(content)


def _to_int(value: object, fallback: int = 0) -> int:
    try:
        if value is None:
            return fallback
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def _metadata_dict(response: Any) -> Dict[str, Any]:
    metadata = getattr(response, "response_metadata", {})
    if isinstance(metadata, dict):
        return metadata
    return {}


def _response_text(response: Any) -> str:
    content = getattr(response, "content", "")
    return _coerce_content(content)


def _build_messages(system_prompt: str, query: str, context: Optional[str]) -> List[object]:
    rolling_context = context.strip() if context else "No previous context."
    content = (
        f"Original Question: {query}\n\n"
        f"Context from previous debate rounds:\n{rolling_context}\n\n"
        "Respond with your best current answer. If context exists, critique and improve previous arguments."
    )
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        return [
            SystemMessage(content=system_prompt or "You are a helpful assistant."),
            HumanMessage(content=content),
        ]
    except Exception:
        return [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": content},
        ]


class OpenAIAgent(Agent):
    def __init__(
        self,
        name: str = "GPT-4o",
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        system_prompt: str = "",
        temperature: float = 0.2,
    ):
        super().__init__(name=name, description="OpenAI model", system_prompt=system_prompt, model=None)
        self.model_name = model_name
        self.api_key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        self.temperature = temperature
        self.init_error: Optional[str] = None
        if self.api_key:
            try:
                from langchain_openai import ChatOpenAI
                kwargs = {"model": model_name, "api_key": self.api_key, "temperature": temperature}
                if base_url:
                    kwargs["base_url"] = base_url
                self.model = ChatOpenAI(**kwargs)
            except Exception as exc:
                self.model = None
                self.init_error = str(exc)

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        if not self.model:
            if self.api_key and self.init_error:
                return AgentResponse(
                    content=f"Error: OpenAI client unavailable ({self.init_error}).",
                    confidence=0.0,
                    model_name=self.model_name,
                )
            return AgentResponse(content="Error: OpenAI API key is missing.", confidence=0.0, model_name=self.model_name)

        messages = _build_messages(self.system_prompt, query, context)
        try:
            full_response = self.model.invoke(messages)
            content = _response_text(full_response)

            usage = _metadata_dict(full_response).get("token_usage", {})
            input_tokens = _to_int(usage.get("prompt_tokens"), fallback=max(len(str(messages)) // 4, 1))
            output_tokens = _to_int(usage.get("completion_tokens"), fallback=max(len(content) // 4, 1))
            total_tokens = _to_int(usage.get("total_tokens"), fallback=input_tokens + output_tokens)

            return AgentResponse(
                content=content,
                confidence=0.88,
                token_usage={"input": input_tokens, "output": output_tokens, "total": total_tokens},
                cost=estimate_cost(self.model_name, input_tokens, output_tokens),
                model_name=self.model_name,
            )
        except Exception as exc:
            return AgentResponse(content=f"Error: {exc}", confidence=0.0, model_name=self.model_name)


class GeminiAgent(Agent):
    def __init__(
        self,
        name: str = "Gemini",
        model_name: str = "gemini-1.5-pro",
        api_key: Optional[str] = None,
        system_prompt: str = "",
        temperature: float = 0.2,
    ):
        super().__init__(name=name, description="Google Gemini model", system_prompt=system_prompt, model=None)
        self.model_name = model_name
        self.api_key = (api_key or os.getenv("GOOGLE_API_KEY", "")).strip()
        self.temperature = temperature
        self.init_error: Optional[str] = None
        if self.api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                self.model = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=self.api_key,
                    temperature=temperature,
                )
            except Exception as exc:
                self.model = None
                self.init_error = str(exc)

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        if not self.model:
            if self.api_key and self.init_error:
                return AgentResponse(
                    content=f"Error: Google client unavailable ({self.init_error}).",
                    confidence=0.0,
                    model_name=self.model_name,
                )
            return AgentResponse(content="Error: Google API key is missing.", confidence=0.0, model_name=self.model_name)

        messages = _build_messages(self.system_prompt, query, context)
        try:
            full_response = self.model.invoke(messages)
            content = _response_text(full_response)

            usage = _metadata_dict(full_response).get("usage_metadata", {})
            input_tokens = _to_int(usage.get("prompt_token_count"), fallback=max(len(str(messages)) // 4, 1))
            output_tokens = _to_int(usage.get("candidates_token_count"), fallback=max(len(content) // 4, 1))
            total_tokens = _to_int(usage.get("total_token_count"), fallback=input_tokens + output_tokens)

            return AgentResponse(
                content=content,
                confidence=0.84,
                token_usage={"input": input_tokens, "output": output_tokens, "total": total_tokens},
                cost=estimate_cost(self.model_name, input_tokens, output_tokens),
                model_name=self.model_name,
            )
        except Exception as exc:
            return AgentResponse(content=f"Error: {exc}", confidence=0.0, model_name=self.model_name)


class AnthropicAgent(Agent):
    def __init__(
        self,
        name: str = "Claude",
        model_name: str = "claude-3-opus-20240229",
        api_key: Optional[str] = None,
        system_prompt: str = "",
        temperature: float = 0.2,
    ):
        super().__init__(name=name, description="Anthropic Claude model", system_prompt=system_prompt, model=None)
        self.model_name = model_name
        self.api_key = (api_key or os.getenv("ANTHROPIC_API_KEY", "")).strip()
        self.temperature = temperature
        self.init_error: Optional[str] = None
        if self.api_key:
            try:
                from langchain_anthropic import ChatAnthropic

                self.model = ChatAnthropic(
                    model=model_name,
                    anthropic_api_key=self.api_key,
                    temperature=temperature,
                )
            except Exception as exc:
                self.model = None
                self.init_error = str(exc)

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        if not self.model:
            if self.api_key and self.init_error:
                return AgentResponse(
                    content=f"Error: Anthropic client unavailable ({self.init_error}).",
                    confidence=0.0,
                    model_name=self.model_name,
                )
            return AgentResponse(content="Error: Anthropic API key is missing.", confidence=0.0, model_name=self.model_name)

        messages = _build_messages(self.system_prompt, query, context)
        try:
            full_response = self.model.invoke(messages)
            content = _response_text(full_response)

            usage = _metadata_dict(full_response).get("usage", {})
            input_tokens = _to_int(usage.get("input_tokens"), fallback=max(len(str(messages)) // 4, 1))
            output_tokens = _to_int(usage.get("output_tokens"), fallback=max(len(content) // 4, 1))

            return AgentResponse(
                content=content,
                confidence=0.9,
                token_usage={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens,
                },
                cost=estimate_cost(self.model_name, input_tokens, output_tokens),
                model_name=self.model_name,
            )
        except Exception as exc:
            return AgentResponse(content=f"Error: {exc}", confidence=0.0, model_name=self.model_name)


class MockAgent(Agent):
    """Low-cost simulation agent for UI demos and local testing."""

    def __init__(self, name: str, behavior: str):
        system_prompt = (
            f"You are a mock agent named {name}. Keep replies concise and follow a {behavior} reasoning style."
        )
        super().__init__(name=name, description="Mock agent", system_prompt=system_prompt, model=None)
        self.behavior = behavior

    def generate_response(self, query: str, context: Optional[str] = None) -> AgentResponse:
        response_templates = {
            "skeptical": [
                "The strongest risk is hidden assumptions. The claim should be tested against edge cases before adoption.",
                "I do not accept the conclusion yet. We need stronger causal evidence and clearer constraints.",
            ],
            "optimistic": [
                "The opportunity is meaningful if execution is disciplined. Early pilots can de-risk rollout.",
                "Benefits are plausible, especially with phased implementation and measurable milestones.",
            ],
            "fact-checking": [
                "Key claims need citations with dates and methodology. Confidence should remain moderate until verified.",
                "Several statements are directionally right but under-sourced. Add references and confidence bounds.",
            ],
            "adversarial": [
                "Counterpoint: the consensus ignores failure modes under resource constraints.",
                "Alternative view: current reasoning may overfit best-case assumptions and ignore long-tail outcomes.",
            ],
            "judge": [
                "Synthesis: combine the cautious evidence filter with pragmatic implementation steps.",
                "Final verdict: balanced strategy wins - pursue upside while explicitly controlling downside risk.",
            ],
        }
        snippet = random.choice(response_templates.get(self.behavior, response_templates["skeptical"]))
        final_content = (
            f"[{self.name}] Assessment:\n"
            f"{snippet}\n"
        )
        return AgentResponse(
            content=final_content,
            confidence=0.62,
            token_usage={"input": 120, "output": 80, "total": 200},
            cost=0.0,
            model_name="mock-agent",
        )


def _mock_behavior_for_model_id(model_id: str) -> str:
    normalized = (model_id or "").lower()
    if "fact" in normalized:
        return "fact-checking"
    if "adversarial" in normalized or "challenger" in normalized:
        return "adversarial"
    if "judge" in normalized:
        return "judge"
    if "optim" in normalized:
        return "optimistic"
    return "skeptical"


def build_agent_from_spec(
    spec: ModelSpec,
    system_prompt: str,
    api_keys: Optional[Dict[str, str]] = None,
    name: Optional[str] = None,
    temperature: float = 0.2,
) -> Agent:
    agent_name = name or spec.label

    if spec.provider == "openai":
        return OpenAIAgent(
            name=agent_name,
            model_name=spec.model_id,
            api_key=resolve_provider_key("openai", api_keys),
            system_prompt=system_prompt,
            temperature=temperature,
        )

    if spec.provider == "google":
        return GeminiAgent(
            name=agent_name,
            model_name=spec.model_id,
            api_key=resolve_provider_key("google", api_keys),
            system_prompt=system_prompt,
            temperature=temperature,
        )

    if spec.provider == "anthropic":
        return AnthropicAgent(
            name=agent_name,
            model_name=spec.model_id,
            api_key=resolve_provider_key("anthropic", api_keys),
            system_prompt=system_prompt,
            temperature=temperature,
        )

    if spec.provider == "openrouter":
        return OpenAIAgent(
            name=agent_name,
            model_name=spec.model_id,
            api_key=resolve_provider_key("openrouter", api_keys),
            base_url="https://openrouter.ai/api/v1",
            system_prompt=system_prompt,
            temperature=temperature,
        )

    if spec.provider == "grok":
        return OpenAIAgent(
            name=agent_name,
            model_name=spec.model_id,
            api_key=resolve_provider_key("grok", api_keys),
            base_url="https://api.x.ai/v1",
            system_prompt=system_prompt,
            temperature=temperature,
        )

    if spec.provider == "mock":
        return MockAgent(name=agent_name, behavior=_mock_behavior_for_model_id(spec.model_id))

    raise ValueError(f"Unsupported provider: {spec.provider}")
