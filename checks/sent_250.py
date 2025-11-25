import re

def extract_status(line: str) -> str:
    m = re.search(r"\(([^)]*)\)", line)
    return m.group(1).strip() if m else ""

def extract_time(line: str) -> str:
    m = re.match(r"^[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}", line)
    return m.group(0) if m else ""

def extract_qid(line: str) -> str:
    m = re.search(r"qid:([^|]+)", line)
    return m.group(1).strip() if m else ""

def extract_msgsender(line: str) -> str:
    m = re.search(r"msgsender:([^|]+)", line)
    return m.group(1).strip() if m else ""

def extract_rcpt(line: str) -> str:
    m = re.search(r"rcpt:(\[[^\]]+\])", line)
    return m.group(1).strip() if m else ""

def extract_subject(line: str) -> str:
    m = re.search(r"subject:([^|]+)", line)
    return m.group(1).strip() if m else ""

def convert_to_chinese_time(time_str: str) -> str:
    """将英文时间格式转换为中文格式，如 'Nov 13 10:36:53' -> '11月13日 10:36:53'"""
    if not time_str:
        return ""
    
    # 月份映射表
    month_map = {
        'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4',
        'May': '5', 'Jun': '6', 'Jul': '7', 'Aug': '8',
        'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }
    
    parts = time_str.split()
    if len(parts) >= 3:
        month_en = parts[0]
        day = parts[1]
        time_part = parts[2]
        
        month_cn = month_map.get(month_en, month_en)
        return f"{month_cn}月{day}日 {time_part}"
    
    return time_str

def run(text: str, sender: str, recipient: str) -> bool:
    lines = text.splitlines()
    tl = text.lower()
    s = sender.lower()
    r = recipient.lower()
    
    # 收集表格数据
    table_data = []
    sent_found = False
    
    # 首先检查收件人是否在文本中
    if not (s in tl and r in tl):
        print("无相关日志，联系发件人确认")
        return False
    
    for ln in lines:
        ll = ln.lower()
        
        # 检查是否包含过滤日志信息
        if "free_milter_server.py" in ll and "onendheaders" in ll:
            # 提取时间（从行首提取）并转换为中文格式
            time_en = extract_time(ln)
            time_cn = convert_to_chinese_time(time_en)
            qid = extract_qid(ln)
            msgsender = extract_msgsender(ln)
            rcpt = extract_rcpt(ln)
            subject = extract_subject(ln)
            
            # 修改条件：允许空主题，但其他字段必须存在，并且要同时匹配用户输入的发件人和收件人
            if time_cn and qid and msgsender and rcpt:
                # 精确匹配：发件人匹配并且收件人在rcpt列表中
                sender_match = sender.lower() == msgsender.lower()
                recipient_in_list = f"'{recipient.lower()}'" in rcpt.lower()
                
                if sender_match and recipient_in_list:
                    table_data.append({
                        "时间": time_cn,
                        "QID": qid,
                        "发件人信息": msgsender,
                        "收件人信息": rcpt,
                        "主题": subject or "(空)"
                    })
        
        # 检查是否同时包含 msgsender:发件人 和 rcpt列表中包含收件人，认为邮件发送可能成功
        if f"msgsender:{sender}" in ln and f"'{recipient}'" in ln and "rcpt:[" in ln:
            t = extract_time(ln)
            status = "成功（基于过滤日志判断）查看用户目录，或联系收件人确认"
            print(f"发信时间：{t}")
            print(f"发件人：{sender}")
            print(f"收件人：{recipient}")
            print(f"status：{status}")
            sent_found = True
    
    # 如果有表格数据，生成表格输出（使用 | 间隔）
    if table_data:
        print("\n邮件信息表格:")
        print("时间 | QID | 发件人信息 | 收件人信息 | 主题")
        print("-" * 100)
        for row in table_data:
            print(f"{row['时间']} | {row['QID']} | {row['发件人信息']} | {row['收件人信息']} | {row['主题']}")
    
    return sent_found