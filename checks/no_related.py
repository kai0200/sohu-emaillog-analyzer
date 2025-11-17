def contains(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()

def run(text: str, sender: str, recipient: str) -> bool:
    s = sender.strip()
    r = recipient.strip()
    if not (contains(text, s) and contains(text, r)):
        print("无相关日志，联系发件人确认")
        return True
    return False