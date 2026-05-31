from agent.agent import InfereValAgent


def main():
    try:
        agent = InfereValAgent()
    except ValueError as e:
        print(f"错误: {e}")
        print("请设置环境变量: export DEEPSEEK_API_KEY=你的key")
        return

    print("InfereVal Agent 已启动（输入 quit 退出，reset 重置对话）")
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
        if user_input.lower() == "reset":
            agent.reset()
            print("对话已重置。\n")
            continue

        try:
            response = agent.chat(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\n出错了: {e}\n")


if __name__ == "__main__":
    main()
