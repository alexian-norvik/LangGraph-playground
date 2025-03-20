import os
from typing import Annotated

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

# Logic
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# compile
graph = graph_builder.compile()

# png_data = graph.get_graph().draw_mermaid_png()
# image = PILImage.open(io.BytesIO(png_data))
# image.show()


def stream_graph_updates(query: str):
    for event in graph.stream({"messages": [{"role": "user", "content": query}]}):
        for value in event.values():
            print("> Assistant: ", value["messages"][-1].content)


while True:
    user_input = input("> user: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye")
        break

    stream_graph_updates(user_input)
