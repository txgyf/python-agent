import json
import os

from openai import OpenAI

from agent.tools import TOOL_FUNCTIONS, TOOLS_SCHEMA

SYSTEM_PROMPT = """你是 InfereVal 平台的数据查询助手。用户会问你关于 GPU 芯片、LLM 模型和推理性能实验的问题。

规则：
- 用中文回答，简洁准确
- 基于工具返回的实际数据回答，不要编造数据
- 如果数据为空或没有匹配结果，直接告诉用户没有找到
- 涉及性能对比时，用表格或列表清晰展示关键指标
- 可以主动对比不同芯片或模型的表现"""


class InfereValAgent:
    def __init__(self):
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
        model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = model
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def chat(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )
            choice = response.choices[0]
            if choice.finish_reason == "tool_calls":
                for tool_call in choice.message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = {}
                    if tool_call.function.arguments:
                        fn_args = json.loads(tool_call.function.arguments)
                    fn = TOOL_FUNCTIONS[fn_name]
                    result = fn(**fn_args)
                    self.messages.append(choice.message)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                continue
            else:
                self.messages.append(choice.message)
                return choice.message.content

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
