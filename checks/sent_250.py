import re

def extract_status(line: str) -> str:
    m = re.search(r"\(([^)]*)\)", line)
    return m.group(1).strip() if m else ""

def extract_time(line: str) -> str:
    m = re.match(r"^[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}", line)
    return m.group(0) if m else ""

def run(text: str, sender: str, recipient: str) -> bool:
    lines = text.splitlines()
    s = sender.lower()
    r = recipient.lower()
    has_cmdfrom = any("cmdfrom:" + s in ln.lower() for ln in lines)
    has_rcpt = any("rcpt:['" + r + "']" in ln.lower() for ln in lines)
    if not (has_cmdfrom and has_rcpt):
        return False
    for ln in lines:
        ll = ln.lower()
        if ("postfix/smtp" in ll and f"to=<{r}>" in ll and "status=sent" in ll and "(250" in ln):
            t = extract_time(ln)
            status = extract_status(ln)
            print(f"发信时间：{t}")
            print(f"发件人：{sender}")
            print(f"收件人：{recipient}")
            print(f"status：{status}")
            return True
    return False