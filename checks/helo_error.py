import re

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
    for ln in text.splitlines():
        ll = ln.lower()
        if ("helo command rejected: host not found" in ll) and contains(ll, sender):
            m = re.search(r"helo=<([^>]+)>", ln)
            helo = m.group(1) if m else ""
            if helo:
                print(f"helo=<{helo}>")
            print(f"发件人：{sender}")
            print("处理建议：请联系运维工程师增加helo白名单")
            return True
    return False