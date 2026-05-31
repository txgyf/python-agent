import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

ROUTING_PROMPT = """你是一个意图分类器。根据用户的输入，判断应该由哪个 Agent 处理。

可选路由：
- infereval：与 GPU 芯片、LLM 模型、推理性能实验相关的问题（查询、对比、分析）
- general：一般的问候、闲聊、或与 InfereVal 无关的问题

只回复路由名称（infereval 或 general），不要回复其他内容。"""


def get_supervisor_llm():
    return ChatOpenAI(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        base_url="https://api.deepseek.com",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        temperature=0,
    )


def supervisor_node(state: dict) -> dict:
    messages = state.get("messages", [])
    user_message = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break
    if not user_message:
        return {"messages": [], "route": "general"}

    llm = get_supervisor_llm()
    response = llm.invoke([
        SystemMessage(content=ROUTING_PROMPT),
        HumanMessage(content=user_message),
    ])
    route = response.content.strip().lower()
    if route not in ("infereval",):
        route = "general"
    return {"route": route}
