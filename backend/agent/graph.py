import os
from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from agent.supervisor import supervisor_node
from agent.infereval_agent import create_infereval_agent


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str


GENERAL_PROMPT = "你是一个友好的助手。用中文简短回答用户的问题。"


def infereval_node(state: dict) -> dict:
    agent = create_infereval_agent()
    result = agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}


def general_node(state: dict) -> dict:
    llm = ChatOpenAI(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        base_url="https://api.deepseek.com",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
    )
    messages = [SystemMessage(content=GENERAL_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def route_decision(state: dict) -> str:
    return state.get("route", "general")


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("infereval", infereval_node)
    graph.add_node("general", general_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", route_decision, {
        "infereval": "infereval",
        "general": "general",
    })
    graph.add_edge("infereval", END)
    graph.add_edge("general", END)

    return graph.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_graph(message: str) -> str:
    graph = get_graph()
    result = graph.invoke({"messages": [HumanMessage(content=message)]})
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    return ""
