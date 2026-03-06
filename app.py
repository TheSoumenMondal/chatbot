import streamlit as st
from main import chatbot, llm_client
from langchain_core.messages import HumanMessage, SystemMessage
import uuid


def generate_chat_title(user_message: str, ai_response: str) -> str:
    prompt = [
        SystemMessage(content="Generate a concise 4-6 word title for a chat conversation. Reply with only the title, no punctuation or quotes."),
        HumanMessage(content=f"User: {user_message}\nAssistant: {ai_response}"),
    ]
    return llm_client.invoke(prompt).content.strip()


def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    st.session_state['chat_titles'][thread_id] = 'New Chat'

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        st.session_state['chat_titles'][thread_id] = 'New Chat'

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values.get('messages', [])

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

add_thread(st.session_state['thread_id'])

st.sidebar.title("Chatbot")

if st.sidebar.button("New Chat", use_container_width=True):
    reset_chat()

for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

st.sidebar.header("Conversation History")

for thread_id in st.session_state['chat_threads'][::-1]:
    label = st.session_state['chat_titles'].get(thread_id, 'New Chat')
    if st.sidebar.button(label, key=thread_id, use_container_width=True):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages_history = []
        for msg in messages:
            if isinstance(msg , HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages_history.append({
                'role' : role,
                'content' : msg.content
            })
        st.session_state['message_history'] = temp_messages_history
        

CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}

user_input = st.chat_input("Type here")

if user_input:
    current_thread = st.session_state['thread_id']
    is_first_message = st.session_state['chat_titles'].get(current_thread, 'New Chat') == 'New Chat'

    st.session_state['message_history'].append({
        'role' : 'user',
        'content' : user_input
    })
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            stream = chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            )
            
            first = next(
                (chunk for chunk, metadata in stream if hasattr(chunk, "content") and chunk.content),
                None,
            )

        def response_generator():
            if first is not None:
                yield first.content
            for chunk, metadata in stream:
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        ai_response = st.write_stream(response_generator())

    if is_first_message:
        st.session_state['chat_titles'][current_thread] = generate_chat_title(user_input, ai_response)

    st.session_state['message_history'].append({
        'role' : 'assistant',
        'content' : ai_response
    })
    