#!/usr/bin/env python3
"""
命令历史功能测试脚本
模拟命令历史的添加和浏览功能
"""


class CommandHistory:
    """命令历史管理器（模拟客户端实现）"""

    def __init__(self, max_history=100):
        self.command_history = []
        self.history_index = -1
        self.current_input = ""
        self.max_history = max_history

    def add_to_history(self, command):
        """添加命令到历史"""
        command = command.strip()
        if not command:
            return

        # 避免重复连续命令
        if self.command_history and self.command_history[-1] == command:
            return

        # 如果命令已存在，先移除旧的
        if command in self.command_history:
            self.command_history.remove(command)

        # 添加到历史末尾
        self.command_history.append(command)

        # 限制历史记录数量
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

        # 重置索引
        self.history_index = -1

    def navigate_up(self):
        """向前浏览历史（上箭头）"""
        if not self.command_history:
            return None

        # 第一次按上箭头，保存当前输入
        if self.history_index == -1:
            self.history_index = len(self.command_history) - 1
        elif self.history_index > 0:
            self.history_index -= 1

        return self.command_history[self.history_index]

    def navigate_down(self):
        """向后浏览历史（下箭头）"""
        if self.history_index == -1:
            return None

        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            return self.command_history[self.history_index]
        else:
            # 到达末尾，恢复空输入
            self.history_index = -1
            return ""

    def reset(self):
        """重置历史浏览状态"""
        self.history_index = -1


def test_command_history():
    """测试命令历史功能"""
    print("=" * 60)
    print("命令历史功能测试")
    print("=" * 60)

    history = CommandHistory(max_history=5)

    # 测试1: 添加命令
    print("\n测试 1: 添加命令到历史")
    commands = ["ls", "pwd", "cd /tmp", "ls -la", "echo hello"]
    for cmd in commands:
        history.add_to_history(cmd)
        print(f"  添加: {cmd}")
    print(f"  历史列表: {history.command_history}")
    assert len(history.command_history) == 5, "历史列表长度应为5"
    print("  ✓ 测试通过")

    # 测试2: 避免重复连续命令
    print("\n测试 2: 避免重复连续命令")
    history.add_to_history("ls")
    history.add_to_history("ls")
    print(f"  连续添加两次 'ls'")
    print(f"  历史列表: {history.command_history}")
    assert history.command_history.count("ls") == 1, "不应有重复连续命令"
    print("  ✓ 测试通过")

    # 测试3: 向前浏览（上箭头）
    print("\n测试 3: 向前浏览历史（上箭头）")
    history.reset()
    result1 = history.navigate_up()
    result2 = history.navigate_up()
    result3 = history.navigate_up()
    print(f"  第1次上箭头: {result1}")
    print(f"  第2次上箭头: {result2}")
    print(f"  第3次上箭头: {result3}")
    assert result1 == history.command_history[-1], "应返回最新命令"
    assert result2 == history.command_history[-2], "应返回倒数第二个命令"
    print("  ✓ 测试通过")

    # 测试4: 向后浏览（下箭头）
    print("\n测试 4: 向后浏览历史（下箭头）")
    result4 = history.navigate_down()
    result5 = history.navigate_down()
    result6 = history.navigate_down()  # 需要再按一次才到末尾
    print(f"  第1次下箭头: {result4}")
    print(f"  第2次下箭头: {result5}")
    print(f"  第3次下箭头: {result6}")
    assert result6 == "", "到达末尾应返回空字符串"
    print("  ✓ 测试通过")

    # 测试5: 命令去重
    print("\n测试 5: 命令去重（移除旧的相同命令）")
    history2 = CommandHistory(max_history=5)
    history2.add_to_history("ls")
    history2.add_to_history("pwd")
    history2.add_to_history("cd")
    history2.add_to_history("ls")  # 再次添加ls
    print(f"  历史列表: {history2.command_history}")
    assert history2.command_history == ["pwd", "cd", "ls"], "ls应该移到末尾"
    print("  ✓ 测试通过")

    # 测试6: 最大历史记录限制
    print("\n测试 6: 最大历史记录限制")
    history3 = CommandHistory(max_history=3)
    for i in range(5):
        history3.add_to_history(f"cmd{i}")
    print(f"  添加5个命令，最大限制3个")
    print(f"  历史列表: {history3.command_history}")
    assert len(history3.command_history) == 3, "历史列表长度应限制为3"
    assert history3.command_history == ["cmd2", "cmd3", "cmd4"], "应保留最新的3个"
    print("  ✓ 测试通过")

    # 测试7: 空命令不添加
    print("\n测试 7: 空命令不添加到历史")
    history4 = CommandHistory()
    history4.add_to_history("ls")
    history4.add_to_history("")
    history4.add_to_history("   ")
    print(f"  添加空命令和空格")
    print(f"  历史列表: {history4.command_history}")
    assert len(history4.command_history) == 1, "空命令不应添加"
    print("  ✓ 测试通过")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！命令历史功能正常。")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_command_history()
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
