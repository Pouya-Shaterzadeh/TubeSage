from groq import Groq
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from typing import Any, List, Mapping, Optional


class GroqLLM(LLM):
    """LangChain-compatible Groq LLM wrapper using OpenAI-compatible API."""

    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.3
    max_tokens: int = 1024
    api_key: str = ""

    @property
    def _llm_type(self) -> str:
        return "groq"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, "temperature": self.temperature}

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stop=stop,
        )
        return response.choices[0].message.content or ""


def get_llm() -> GroqLLM:
    from src.config import LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, get_groq_api_key

    return GroqLLM(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        api_key=get_groq_api_key(),
    )
