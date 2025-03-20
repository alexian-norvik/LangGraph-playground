import io
import random
from typing import Literal

from PIL import Image as PILImage
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict):
    graph_state: str


def node_1(state):
    return {"graph_state": f"{state['graph_state']} I am"}


def node_2(state):
    return {"graph_state": f"{state['graph_state']} Happy!"}


def node_3(state):
    return {"graph_state": f"{state['graph_state']} sad"}


def decide_mode(state) -> Literal["node_2", "node_3"]:
    state["graph_state"]

    if random.random() < 0.5:
        return "node_2"

    return "node_3"


# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mode)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

# visualize
png_data = graph.get_graph().draw_mermaid_png()
image = PILImage.open(io.BytesIO(png_data))
# image.show()

# Save the graph as png file
with open("graph.png", mode="wb") as image_file:
    image_file.write(png_data)

response = graph.invoke({"graph_state": "Hi, this is Lance."})

print(response)
