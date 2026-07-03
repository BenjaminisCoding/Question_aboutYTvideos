# YouTube Video Q&A

Quick Streamlit app to ask questions about a YouTube video transcript.

The app:

- loads subtitles from a YouTube URL with `youtube-transcript-api`
- formats the complete transcript with timestamps
- sends the transcript, chat history, and your question to Azure OpenAI
- shows the conversation in a Streamlit chat interface

## Requirements

- Python 3.12 recommended
- An Azure OpenAI resource with a chat model deployment
- A local `.env` file with your Azure OpenAI credentials

Python libraries are listed in `requirements.txt`:

```text
streamlit
openai
python-dotenv
youtube-transcript-api
pytest
```

## Setup

If you are starting from scratch, create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

This repo currently also has an existing virtual environment named `ytvideosum`.
You can activate it instead:

```bash
source ytvideosum/bin/activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Configure Azure OpenAI

Create a local `.env` file from the example file:

```bash
cp .env.example .env
```

Then fill in these values in `.env`:

```text
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

Optional setting:

```text
AZURE_OPENAI_MAX_TRANSCRIPT_CHARS=120000
```

The app sends the full transcript in the prompt. If the transcript or chat history is too large for your model context window, the app shows an error instead of using a mock response.

## Run

With an activated virtual environment:

```bash
streamlit run streamlit_app.py
```

Or, using the existing `ytvideosum` environment directly:

```bash
./ytvideosum/bin/streamlit run streamlit_app.py
```

Open the local URL that Streamlit prints, usually:

```text
http://localhost:8501
```

## How To Use

1. Paste a YouTube URL or video ID.
2. Keep `Subtitle languages` as `en`, or enter comma-separated language codes like `fr,en`.
3. Click `Load subtitles`.
4. Review the transcript preview if needed.
5. Ask questions in the chat input at the bottom of the page.

Each answer is generated from the full timestamped transcript plus the current chat history.

## Behavior

- If subtitles cannot be loaded, the UI shows an error.
- If Azure OpenAI credentials are missing or invalid, the UI shows an error.
- If the answer is not in the transcript, the prompt tells the LLM to say so.
- No mock LLM response is used.

## Tests

With an activated virtual environment:

```bash
pytest
```

Or, using the existing `ytvideosum` environment directly:

```bash
./ytvideosum/bin/python -m pytest
```
