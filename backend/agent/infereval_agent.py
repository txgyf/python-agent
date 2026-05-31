import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from agent.tools import LANGCHAIN_TOOLS

SYSTEM_PROMPT = """你是 InfereVal 平台的数据查询和性能分析助手。用户会问你关于 GPU 芯片、LLM 模型和推理性能实验的问题。

规则：
- 用中文回答，简洁准确
- 基于工具返回的实际数据回答，不要编造数据
- 如果数据为空或没有匹配结果，直接告诉用户没有找到
- 涉及性能对比时，用表格或列表清晰展示关键指标

工具使用策略：
- 用户查询数据时：使用 search_* 工具
- 用户要求对比/比较不同实验或芯片性能时：先用 search_experiments 找到实验，再用 compare_experiments 生成对比
- 用户要求总结/分析时：使用 generate_summary 生成文字化总结
- 多轮对话中，记住之前提到的实验 ID 和数据，不要重复查询"""


def get_llm():
    return ChatOpenAI(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        base_url="https://api.deepseek.com",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
    )


def create_infereval_agent():
    llm = get_llm()
    return create_react_agent(
        model=llm,
        tools=LANGCHAIN_TOOLS,
        prompt=SYSTEM_PROMPT,
    )
