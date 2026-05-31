import os

from agent.graph import run_graph, get_graph


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误: DEEPSEEK_API_KEY 环境变量未设置")
        print("请设置环境变量: export DEEPSEEK_API_KEY=你的key")
        return

    try:
        get_graph()
    except Exception as e:
        print(f"初始化失败: {e}")
        return

    print("InfereVal Agent 已启动（输入 quit 退出）")
    print()

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("再见！")
            break

        try:
            response = run_graph(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\n出错了: {e}\n")


if __name__ == "__main__":
    main()
