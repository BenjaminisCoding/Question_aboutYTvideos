"""Azure OpenAI integration for transcript-grounded chat."""

from __future__ import annotations

from .config import AzureOpenAISettings
from .prompting import build_chat_messages, ensure_transcript_fits, TranscriptTooLargeError


class LLMError(RuntimeError):
    """Raised when Azure OpenAI cannot return an answer."""


def answer_question(
    settings: AzureOpenAISettings,
    transcript: str,
    history: list[dict[str, str]],
    question: str,
) -> str:
    """Ask Azure OpenAI a transcript-grounded question."""

    ensure_transcript_fits(transcript, settings.max_transcript_chars)
    messages = build_chat_messages(transcript=transcript, history=history, question=question)

    try:
        from openai import AzureOpenAI
    except ModuleNotFoundError as exc:
        raise LLMError("openai is not installed. Run `pip install -r requirements.txt`.") from exc

    client = AzureOpenAI(
        api_key=settings.api_key,
        api_version=settings.api_version,
        azure_endpoint=settings.endpoint,
    )

    try:
        response = client.chat.completions.create(
            model=settings.deployment,
            messages=messages,
        )
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        if any(
            marker in lowered
            for marker in ("context length", "maximum context", "too many tokens", "token limit")
        ):
            raise TranscriptTooLargeError(
                "Azure OpenAI rejected the request because the transcript and chat "
                "history are too large for the deployment context window."
            ) from exc
        raise LLMError(f"Azure OpenAI request failed: {message}") from exc

    answer = response.choices[0].message.content if response.choices else ""
    if not answer:
        raise LLMError("Azure OpenAI returned an empty answer.")
    return answer.strip()
