import os
from typing import Annotated

from dotenv import load_dotenv
from langgraph.graph import START, StateGraph
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def multiply(a: int, b: int) -> int:
    """
    multiply provided two digits together
    :param a: first digit
    :param b: second digit
    :return: result of the multiplication
    """
    return a * b


tools = [multiply]
config = {"configurable": {"thread_id": "1"}}
memory = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)
llm_with_tools = llm.bind_tools(tools=tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# build graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools))

# Logic
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
# graph_builder.add_edge("chatbot", END)

# compile
graph = graph_builder.compile(checkpointer=memory)

# png_data = graph.get_graph().draw_mermaid_png()
# image = PILImage.open(io.BytesIO(png_data))
# image.show()


def stream_graph_updates(query: str):
    for event in graph.stream({"messages": [{"role": "user", "content": query}]}, config=config):
        for value in event.values():
            if type(value["messages"][0]) is AIMessage and value["messages"][-1].content:
                print("> Assistant: ", value["messages"][-1].content)


while True:
    user_input = input("> user: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye")
        break

    stream_graph_updates(user_input)
