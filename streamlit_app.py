"""Streamlit interface for YouTube transcript question answering."""

from __future__ import annotations

import streamlit as st

from yt_video_qa.config import ConfigError, load_settings
from yt_video_qa.llm import LLMError, answer_question
from yt_video_qa.prompting import TranscriptTooLargeError
from yt_video_qa.transcript import (
    TranscriptFetchError,
    extract_video_id,
    fetch_transcript,
    format_transcript,
    parse_language_codes,
)


def main() -> None:
    st.set_page_config(page_title="YouTube Video Q&A", page_icon="▶", layout="wide")
    st.title("YouTube Video Q&A")

    _init_session_state()
    settings, settings_error = _load_settings_for_ui()

    with st.sidebar:
        st.header("Settings")
        if settings_error:
            st.error(settings_error)
        else:
            st.success("Azure OpenAI config loaded")
            st.caption(f"Deployment: `{settings.deployment}`")

        st.divider()
        languages_input = st.text_input("Subtitle languages", value="en")

    video_input = st.text_input("YouTube URL or video ID")
    if st.button("Load subtitles", type="primary"):
        _load_video(video_input, languages_input)

    if st.session_state.transcript_text:
        _render_transcript_panel()
        _render_chat(settings, settings_error)
    else:
        st.info("Load a YouTube transcript to start asking questions.")


def _init_session_state() -> None:
    defaults = {
        "video_id": "",
        "loaded_input": "",
        "transcript_text": "",
        "transcript_snippet_count": 0,
        "messages": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _load_settings_for_ui():
    try:
        return load_settings(), None
    except ConfigError as exc:
        return None, str(exc)


def _load_video(video_input: str, languages_input: str) -> None:
    try:
        video_id = extract_video_id(video_input)
        languages = parse_language_codes(languages_input)
        snippets = fetch_transcript(video_id, languages=languages)
        transcript_text = format_transcript(snippets)
    except ValueError as exc:
        st.error(str(exc))
        return
    except TranscriptFetchError as exc:
        st.error(str(exc))
        return

    st.session_state.video_id = video_id
    st.session_state.loaded_input = video_input
    st.session_state.transcript_text = transcript_text
    st.session_state.transcript_snippet_count = len(snippets)
    st.session_state.messages = []
    st.success("Subtitles loaded.")


def _render_transcript_panel() -> None:
    transcript = st.session_state.transcript_text
    st.success(
        f"Loaded video `{st.session_state.video_id}` with "
        f"{st.session_state.transcript_snippet_count:,} subtitle snippets "
        f"({len(transcript):,} characters)."
    )
    with st.expander("Transcript preview"):
        st.text_area(
            "Transcript",
            value=transcript,
            height=260,
            disabled=True,
            label_visibility="collapsed",
        )


def _render_chat(settings, settings_error: str | None) -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about the video")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    if settings_error or settings is None:
        st.error("Azure OpenAI is not configured. Create `.env` from `.env.example`.")
        return

    history = st.session_state.messages[:-1]
    with st.chat_message("assistant"):
        with st.spinner("Reading the transcript..."):
            try:
                answer = answer_question(
                    settings=settings,
                    transcript=st.session_state.transcript_text,
                    history=history,
                    question=question,
                )
            except TranscriptTooLargeError as exc:
                st.error(str(exc))
                return
            except LLMError as exc:
                st.error(str(exc))
                return

        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
