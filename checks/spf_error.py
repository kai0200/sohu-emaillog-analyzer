def sender_domain(sender: str) -> str:
    return sender.split("@")[-1].lower() if "@" in sender else ""

def is_sohu_domain(domain: str) -> bool:
    return domain.endswith("sohu.com") or domain.endswith("vip.sohu.com")

def contains(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()

def run(text: str, sender: str, recipient: str) -> bool:
    dom = sender_domain(sender)
    if is_sohu_domain(dom):
        return False
    if contains(text, sender) and ("spf error" in text.lower()):
        print(f"发件人：{sender}")
        print("结果：SPF错误")
        return True
    return False