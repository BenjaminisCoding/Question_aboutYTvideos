from yt_video_qa.transcript import (
    TranscriptSnippet,
    extract_video_id,
    format_timestamp,
    format_transcript,
    parse_language_codes,
)


def test_extract_video_id_from_common_inputs():
    expected = "dQw4w9WgXcQ"
    cases = [
        expected,
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
        "https://youtu.be/dQw4w9WgXcQ?si=abc",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "www.youtube.com/live/dQw4w9WgXcQ",
    ]

    for value in cases:
        assert extract_video_id(value) == expected


def test_extract_video_id_rejects_invalid_input():
    invalid_inputs = [
        "https://example.com/not-youtube",
        "https://notyoutube.com/watch?v=dQw4w9WgXcQ",
    ]
    for value in invalid_inputs:
        try:
            extract_video_id(value)
        except ValueError as exc:
            assert "valid YouTube video ID" in str(exc)
        else:
            raise AssertionError("Expected ValueError")


def test_format_transcript_cleans_text_and_adds_timestamps():
    snippets = [
        {"start": 0, "duration": 1.2, "text": "Hello\nworld &amp; friends"},
        TranscriptSnippet(start=65.8, duration=2.0, text="Next   line"),
    ]

    formatted = format_transcript(snippets)

    assert "[00:00] Hello world & friends" in formatted
    assert "[01:05] Next line" in formatted


def test_format_timestamp_uses_hours_when_needed():
    assert format_timestamp(5) == "00:05"
    assert format_timestamp(3661) == "01:01:01"


def test_parse_language_codes_defaults_to_english():
    assert parse_language_codes("") == ("en",)
    assert parse_language_codes("fr, en,es") == ("fr", "en", "es")
