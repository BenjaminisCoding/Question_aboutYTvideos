"""YouTube transcript loading and formatting helpers."""

from __future__ import annotations

from dataclasses import dataclass
import html
import re
from typing import Iterable, Sequence
from urllib.parse import parse_qs, urlparse


YOUTUBE_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


class TranscriptFetchError(RuntimeError):
    """Raised when subtitles cannot be fetched for a YouTube video."""


@dataclass(frozen=True)
class TranscriptSnippet:
    text: str
    start: float
    duration: float | None = None


def extract_video_id(value: str) -> str:
    """Extract an 11-character YouTube video ID from common URL formats."""

    candidate = value.strip()
    if YOUTUBE_VIDEO_ID_RE.fullmatch(candidate):
        return candidate

    if not candidate:
        raise ValueError("Enter a YouTube URL or video ID.")

    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    host = parsed.netloc.lower()
    path_parts = [part for part in parsed.path.split("/") if part]

    if _is_host(host, "youtu.be") and path_parts:
        return _validate_video_id(path_parts[0])

    if _is_host(host, "youtube.com"):
        query_video_id = parse_qs(parsed.query).get("v", [""])[0]
        if query_video_id:
            return _validate_video_id(query_video_id)

        if len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts", "live"}:
            return _validate_video_id(path_parts[1])

    raise ValueError("Could not find a valid YouTube video ID in that input.")


def fetch_transcript(
    video_id: str,
    languages: Sequence[str] = ("en",),
) -> list[TranscriptSnippet]:
    """Fetch subtitles for a YouTube video and normalize them."""

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ModuleNotFoundError as exc:
        raise TranscriptFetchError(
            "youtube-transcript-api is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=list(languages))
    except Exception as exc:
        raise TranscriptFetchError(
            "Could not fetch subtitles for this video. The video may not have "
            "subtitles in the selected language, or YouTube may have blocked the request."
        ) from exc

    snippets = normalize_transcript(transcript)
    if not snippets:
        raise TranscriptFetchError("The subtitle response was empty.")
    return snippets


def normalize_transcript(transcript: object) -> list[TranscriptSnippet]:
    """Normalize dicts, API snippet objects, or fetched transcript objects."""

    if hasattr(transcript, "to_raw_data"):
        items = transcript.to_raw_data()
    elif hasattr(transcript, "snippets"):
        items = getattr(transcript, "snippets")
    else:
        items = transcript

    snippets: list[TranscriptSnippet] = []
    for item in items:  # type: ignore[union-attr]
        text = _read_value(item, "text", "")
        start = _read_value(item, "start", 0.0)
        duration = _read_value(item, "duration", None)
        snippets.append(
            TranscriptSnippet(
                text=str(text),
                start=float(start or 0.0),
                duration=float(duration) if duration is not None else None,
            )
        )
    return snippets


def format_transcript(snippets: Iterable[TranscriptSnippet | dict[str, object]]) -> str:
    """Format subtitle snippets as timestamped plain text for the LLM prompt."""

    lines: list[str] = []
    for snippet in snippets:
        text = str(_read_value(snippet, "text", ""))
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue

        start = float(_read_value(snippet, "start", 0.0) or 0.0)
        lines.append(f"[{format_timestamp(start)}] {text}")

    return "\n".join(lines)


def format_timestamp(seconds: float) -> str:
    """Format a number of seconds as MM:SS or HH:MM:SS."""

    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def parse_language_codes(value: str) -> tuple[str, ...]:
    """Parse comma-separated YouTube transcript language codes."""

    languages = tuple(code.strip() for code in value.split(",") if code.strip())
    return languages or ("en",)


def _validate_video_id(value: str) -> str:
    if not YOUTUBE_VIDEO_ID_RE.fullmatch(value):
        raise ValueError("Could not find a valid YouTube video ID in that input.")
    return value


def _is_host(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")


def _read_value(item: object, key: str, default: object) -> object:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)
