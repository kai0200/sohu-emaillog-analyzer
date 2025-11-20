import re
import json

# 预编译正则表达式
TIME_PATTERN = re.compile(r"^[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}")
STATUS_PATTERN = re.compile(r"\(([^)]*)\)")
MSGSENDER_PATTERN = re.compile(r"msgsender:([^|]+)")
RCPT_PATTERN = re.compile(r"rcpt:(\[[^\]]*\])")

def extract_time(line: str) -> str:
    m = TIME_PATTERN.match(line)
    return m.group(0) if m else ""

def extract_status(line: str) -> str:
    m = STATUS_PATTERN.search(line)
    return m.group(1).strip() if m else ""

def extract_msgsender(line: str) -> str:
    m = MSGSENDER_PATTERN.search(line)
    return m.group(1).strip() if m else ""

def extract_rcpt_list(line: str) -> list:
    m = RCPT_PATTERN.search(line)
    if m:
        try:
            # 尝试解析JSON格式的收件人列表
            rcpt_list = json.loads(m.group(1))
            return rcpt_list if isinstance(rcpt_list, list) else []
        except json.JSONDecodeError:
            # 如果不是标准JSON，尝试其他解析方式
            rcpt_str = m.group(1).strip("[]'\"")
            return [email.strip() for email in rcpt_str.split(",") if email.strip()]
    return []

def run(text: str, sender: str, recipient: str) -> bool:
    lines = text.splitlines()
    
    # 检查是否包含250状态码
    has_250 = any("(250" in line for line in lines)
    if not has_250:
        return False
    
    # 查找包含msgsender和rcpt信息的行
    msgsender_line = None
    rcpt_line = None
    
    for line in lines:
        if "msgsender:" in line:
            msgsender_line = line
        if "rcpt:[" in line:
            rcpt_line = line
    
    if not msgsender_line or not rcpt_line:
        return False
    
    # 提取发件人和收件人信息
    extracted_msgsender = extract_msgsender(msgsender_line)
    extracted_rcpt_list = extract_rcpt_list(rcpt_line)
    
    # 查找包含250状态码的发送成功行
    for line in lines:
        if ("postfix/smtp" in line.lower() and 
            "status=sent" in line.lower() and 
            "(250" in line):
            time = extract_time(line)
            status = extract_status(line)
            
            print(f"发信时间：{time}")
            print(f"发件人(msgsender)：{extracted_msgsender}")
            print(f"收件人列表(rcpt)：{extracted_rcpt_list}")
            print(f"状态码：{status}")
            
            # 检查是否匹配传入的收件人
            if recipient in extracted_rcpt_list:
                print(f"匹配到目标收件人：{recipient}")
                return True
            else:
                print(f"警告：目标收件人 {recipient} 不在收件人列表中")
                return True
    
    return False