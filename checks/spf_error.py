def run(text: str, sender: str, recipient: str) -> bool:
    for ln in text.splitlines():
        # 使用原始文本检查，但确保能匹配到各种大小写变体
        if "SPF Error" in ln or "spf error" in ln.lower():
            print(f"发件人：{sender}")
            print("结果：SPF错误")
            return True
    return False