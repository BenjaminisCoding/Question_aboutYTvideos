"""Prompt construction for transcript-grounded question answering."""

from __future__ import annotations

from typing import Iterable


SYSTEM_PROMPT = """You answer questions about a YouTube video using only its transcript.
If the transcript does not contain the answer, say that the answer is not present in the transcript.
When useful, cite approximate timestamps from the transcript. Do not invent details that are not supported by the transcript."""


def build_chat_messages(
    transcript: str,
    history: Iterable[dict[str, str]],
    question: str,
) -> list[dict[str, str]]:
    """Build chat-completions messages with the complete transcript included."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Here is the complete timestamped transcript for the video:\n\n"
                "<transcript>\n"
                f"{transcript}\n"
                "</transcript>"
            ),
        },
    ]

    for item in history:
        role = item.get("role")
        content = item.get("content", "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": question})
    return messages


def ensure_transcript_fits(transcript: str, max_chars: int) -> None:
    """Raise a clear error before sending transcripts beyond the configured guard."""

    if len(transcript) > max_chars:
        raise TranscriptTooLargeError(
            "The transcript is too large to send in one prompt "
            f"({len(transcript):,} characters, limit {max_chars:,}). "
            "Increase AZURE_OPENAI_MAX_TRANSCRIPT_CHARS for a larger deployment, "
            "or use a shorter video."
        )


class TranscriptTooLargeError(RuntimeError):
    """Raised when a transcript is too large for the full-prompt strategy."""
