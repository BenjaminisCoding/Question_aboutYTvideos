from yt_video_qa.prompting import build_chat_messages, ensure_transcript_fits, TranscriptTooLargeError


def test_build_chat_messages_includes_full_transcript_history_and_question():
    transcript = "[00:00] Full transcript line"
    history = [
        {"role": "user", "content": "What is introduced first?"},
        {"role": "assistant", "content": "The speaker introduces the project."},
    ]

    messages = build_chat_messages(
        transcript=transcript,
        history=history,
        question="What happens next?",
    )

    assert messages[0]["role"] == "system"
    assert transcript in messages[1]["content"]
    assert messages[2]["content"] == "What is introduced first?"
    assert messages[-1]["content"] == "What happens next?"


def test_ensure_transcript_fits_raises_clear_error():
    try:
        ensure_transcript_fits("abcdef", max_chars=5)
    except TranscriptTooLargeError as exc:
        assert "too large" in str(exc)
    else:
        raise AssertionError("Expected TranscriptTooLargeError")
