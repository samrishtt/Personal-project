# DebateMind: Consensus Multi-Agent System

This project allows multiple AI agents (LLMs) to debate answers to complex questions, leading to a more robust and accurate final answer through consensus and peer review.

## Features
-   **Multi-Agent Debate**: Several agents debate each other's answers.
-   **Peer Review**: Agents critique and refine answers.
-   **Consensus Synthesis**: A final agent synthesizes the best parts of the debate.
-   **Modular Backend**: Supports OpenAI (GPT), Google Gemini, Anthropic Claude, and Local LLMs (Ollama).

## Setup
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **API Keys**:
    -   Create a `.env` file and add your API keys:
        -   `OPENAI_API_KEY=sk-...`
        -   `GOOGLE_API_KEY=AIza...`
        -   `ANTHROPIC_API_KEY=sk-ant...` (Optional)

3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## Usage
1.  Open the web interface.
2.  Enter your question.
3.  Select the desired model backend.
4.  Watch the agents debate and refine the answer!

## Future Roadmap
-   Add more sophisticated agent personalization (roles: Critic, Optimist, Fact-Checker).
-   Implement retrieval-augmented generation (RAG) for better factual accuracy.
-   Support for local open-source models (Llama 3, Mistral) via Ollama.
