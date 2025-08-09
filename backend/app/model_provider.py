from __future__ import annotations

import os
from typing import Optional


class ModelProvider:
    def __init__(self, provider: str, model_name: str, temperature: float = 0.0, top_p: float = 1.0, max_tokens: int = 512) -> None:
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

        self._pipeline = None
        self._litellm = None

        if provider in {"litellm", "openai"}:
            try:
                import litellm  # type: ignore

                self._litellm = litellm
            except Exception:
                self._litellm = None
        elif provider == "huggingface":
            # Lazy import; heavy deps may not be available. Only instantiate on first call.
            pass

    def generate(self, prompt: str) -> str:
        if self.provider in {"litellm", "openai"}:
            if self._litellm is None:
                raise RuntimeError("litellm is not installed. Please install to use hosted providers.")
            # Use chat.completions API shape for generality
            response = self._litellm.completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
            )
            # litellm normalizes choices[0].message["content"]
            content = response.choices[0].message["content"]  # type: ignore
            return content or ""

        if self.provider == "huggingface":
            if self._pipeline is None:
                from transformers import pipeline  # type: ignore

                self._pipeline = pipeline(
                    "text-generation",
                    model=self.model_name,
                    max_new_tokens=self.max_tokens,
                    do_sample=self.temperature > 0,
                    top_p=self.top_p,
                    temperature=max(self.temperature, 1e-5),
                )
            outputs = self._pipeline(prompt)
            if isinstance(outputs, list) and outputs and "generated_text" in outputs[0]:
                return str(outputs[0]["generated_text"])  # type: ignore
            return str(outputs)

        raise ValueError(f"Unknown provider: {self.provider}")