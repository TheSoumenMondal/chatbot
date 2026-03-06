# Chatbot using langchain

A multi-session conversational chatbot built with Streamlit, LangGraph, and Google Gemini.

![Image](https://github.com/user-attachments/assets/813a368a-7d8c-4d59-9ad2-6df6794f8f2a)

## Stack

- **Streamlit** — UI and session management
- **LangGraph** — conversation graph with persistent memory
- **Google Gemini** (`gemini-2.5-flash`) — language model
- **LangChain Google GenAI** — LLM integration

## How it works

![Image](https://github.com/user-attachments/assets/882206ed-70bf-4d87-a792-78e4c6fcdc20)

### Graph (main.py)

A `StateGraph` is defined with a single `ChatState` holding the message list. The graph has one node (`chat_node`) that calls the Gemini LLM with the current message history and appends the response. The graph is compiled with a `MemorySaver` checkpointer, which persists the full message history per `thread_id` in memory.

### App (app.py)

Each conversation is identified by a UUID `thread_id` stored in Streamlit session state. When the user sends a message, it is passed to `chatbot.stream()` with `stream_mode="messages"`, which streams `(chunk, metadata)` tuples. The UI shows a spinner until the first chunk arrives, then streams the response token by token.

After the first exchange in a new thread, the LLM is called separately to generate a short 4-6 word title for the sidebar. Switching threads reloads the message history from the LangGraph checkpointer via `get_state()`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

Run:

```bash
streamlit run app.py
```
