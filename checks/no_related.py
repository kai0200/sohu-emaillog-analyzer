def contains(text: str, needle: str) -> bool:
    nl = needle.lower().strip()
    for ln in text.splitlines():
        ll = ln.lower()
        if ll.startswith("[info]") and ("文件中未找到邮件地址" in ll):
            continue
        if ll.startswith("[error]"):
            continue
        if nl and (nl in ll):
            return True
    return False

def run(text: str, sender: str, recipient: str) -> bool:
    s = sender.strip()
    r = recipient.strip()
    if not (contains(text, s) and contains(text, r)):
        print("无相关日志，联系发件人确认")
        return True
    return False