from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm_client = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)


def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm_client.invoke(messages)
    return {"messages": [response]}


checkpointer = MemorySaver()

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    thread_id = "1"

    while True:
        user_message = input("Type here : ")
        print("You:", user_message)
        if user_message.strip().lower() in ["exit", "quit", "bye"]:
            break
        config = {"configurable": {"thread_id": thread_id}}
        response = chatbot.invoke(
            {"messages": [HumanMessage(content=user_message)]}, config=config
        )
        print(response["messages"][-1].content)
