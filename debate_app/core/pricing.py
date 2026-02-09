PRICING_REGISTRY = {
    # OpenAI
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-2024-05-13": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    
    # Anthropic
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    
    # Google
    "gemini-1.5-pro": {"input": 3.50, "output": 10.50}, # Approx per million tokens
    "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
    "gemini-pro": {"input": 0.50, "output": 1.50}, # Legacy pricing approx
}

def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """
    Returns estimated cost in USD based on model pricing per 1M tokens.
    """
    pricing = PRICING_REGISTRY.get(model_name)
    if not pricing:
        return 0.0
        
    cost_in = (input_tokens / 1_000_000) * pricing["input"]
    cost_out = (output_tokens / 1_000_000) * pricing["output"]
    return round(cost_in + cost_out, 6)
