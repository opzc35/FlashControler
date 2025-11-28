#!/usr/bin/env python3
"""
ANSI转义序列过滤测试脚本
验证客户端能否正确过滤终端控制码
"""
import re

# 与客户端相同的正则表达式
ANSI_ESCAPE_PATTERN = re.compile(
    r'\x1b\[[0-9;]*[a-zA-Z]|'  # 标准CSI序列
    r'\x1b\][0-9;]*;[^\x07]*\x07|'  # OSC序列
    r'\x1b\][^\x07]*\x07|'  # OSC序列简化版
    r'\x1b\[\?[0-9;]*[a-zA-Z]|'  # 私有模式
    r'\x1b[=>]|'  # 应用/普通键盘模式
    r'\r'  # 回车符
)

def strip_ansi_codes(text):
    """移除ANSI转义序列"""
    return ANSI_ESCAPE_PATTERN.sub('', text)

# 测试用例
test_cases = [
    # (输入, 期望输出, 描述)
    ("\x1b[?2004hubuntu@VM:~$ ", "ubuntu@VM:~$ ", "Bracketed paste mode"),
    ("\x1b[31m红色文本\x1b[0m", "红色文本", "颜色控制码"),
    ("\x1b[1;32m绿色加粗\x1b[0m", "绿色加粗", "多属性颜色"),
    ("普通文本", "普通文本", "无控制码"),
    ("\x1b[2J\x1b[H清屏", "清屏", "清屏+光标移动"),
    ("ubuntu@VM-12-14-ubuntu:~/program/FlashControler$ ls\r\n",
     "ubuntu@VM-12-14-ubuntu:~/program/FlashControler$ ls\n",
     "回车符过滤"),
    ("\x1b[?2004h\x1b[?2004l测试", "测试", "Bracketed paste开关"),
]

print("=" * 60)
print("ANSI转义序列过滤测试")
print("=" * 60)

passed = 0
failed = 0

for i, (input_text, expected, description) in enumerate(test_cases, 1):
    result = strip_ansi_codes(input_text)
    status = "✓ PASS" if result == expected else "✗ FAIL"

    if result == expected:
        passed += 1
    else:
        failed += 1

    print(f"\n测试 {i}: {description}")
    print(f"  输入:   {repr(input_text)}")
    print(f"  期望:   {repr(expected)}")
    print(f"  实际:   {repr(result)}")
    print(f"  结果:   {status}")

print("\n" + "=" * 60)
print(f"测试结果: {passed} 通过, {failed} 失败")
print("=" * 60)

if failed == 0:
    print("\n✓ 所有测试通过！ANSI过滤功能正常。")
else:
    print(f"\n✗ {failed} 个测试失败，请检查正则表达式。")
