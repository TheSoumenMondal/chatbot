import streamlit as st
from main import chatbot
from langchain_core.messages import HumanMessage

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

message_history = []
thread_id = '1'
config = {"configurable": {"thread_id": thread_id}}

for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

user_input = st.chat_input("Type here")

if user_input:
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
                config={"configurable": {"thread_id": "thread_1"}},
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

    st.session_state['message_history'].append({
        'role' : 'assistant',
        'content' : ai_response
    })
    