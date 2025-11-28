import re
from collections import defaultdict
from typing import Dict, List, Optional

def extract_time(line: str) -> str:
    m = re.match(r"^[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}", line)
    return m.group(0) if m else ""

def extract_postfix_qid(line: str) -> str:
    m = re.search(r"\b([0-9A-Za-z]{8,}):", line)
    return m.group(1) if m else ""

def extract_filter_qid(line: str) -> str:
    m = re.search(r"qid:([0-9A-Za-z]+)", line, flags=re.IGNORECASE)
    return m.group(1) if m else ""

def extract_status_segment(line: str) -> str:
    idx = line.lower().find("status=")
    return line[idx:].strip() if idx >= 0 else ""

def extract_addr(line: str, key: str) -> str:
    pattern = rf"{key}=<([^>]+)>"
    m = re.search(pattern, line, flags=re.IGNORECASE)
    return f"{key}=<{m.group(1)}>" if m else ""

def sender_matches(address: str, sender: str) -> bool:
    addr_l = address.lower()
    s_l = sender.lower()
    if not s_l:
        return False
    if s_l.startswith("@"):
        dom = s_l[1:]
        return addr_l.endswith("@" + dom)
    return addr_l == s_l

def extract_sender_from_filter(line: str) -> str:
    m = re.search(r"cmdfrom:([^|\s]+)", line, flags=re.IGNORECASE)
    if not m:
        m = re.search(r"msgsender:([^|\s]+)", line, flags=re.IGNORECASE)
    if m:
        addr = m.group(1).strip()
        return f"from=<{addr}>"
    m2 = re.search(r"msgfrom:.*<([^>]+)>", line, flags=re.IGNORECASE)
    if m2:
        addr = m2.group(1).strip()
        return f"from=<{addr}>"
    return ""

def extract_status_value(segment: str) -> str:
    m = re.search(r"status=([A-Za-z0-9._-]+)", segment, flags=re.IGNORECASE)
    return m.group(1) if m else ""

def extract_said(segment: str) -> str:
    m = re.search(r"said:\s*(.*)", segment, flags=re.IGNORECASE)
    if not m:
        return ""
    value = m.group(1).strip()
    value = re.sub(r"\)+$", "", value).strip()
    return value

def extract_status_message(segment: str) -> str:
    if not segment:
        return ""
    m = re.search(r"status=[A-Za-z0-9._-]+\s*(.*)", segment, flags=re.IGNORECASE)
    if not m:
        return ""
    value = m.group(1).strip()
    # strip surrounding parentheses or trailing punctuation
    value = re.sub(r"^[():-]+", "", value).strip()
    value = re.sub(r"\)+$", "", value).strip()
    return value

def determine_delivery_state(messages) -> str:
    for msg in messages:
        if msg and "250" in msg:
            return "成功"
    return "失败"

MONTH_MAP = {
    "Jan": "1",
    "Feb": "2",
    "Mar": "3",
    "Apr": "4",
    "May": "5",
    "Jun": "6",
    "Jul": "7",
    "Aug": "8",
    "Sep": "9",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}


def convert_to_chinese_time(time_str: str) -> str:
    if not time_str:
        return ""
    parts = time_str.split()
    if len(parts) < 3:
        return time_str
    month_en, day, time_part = parts[0], parts[1], parts[2]
    month_cn = MONTH_MAP.get(month_en, month_en)
    return f"{month_cn}月{day}日 {time_part}"


def extract_msgsender_field(line: str) -> str:
    m = re.search(r"msgsender:([^|]+)", line, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_rcpt_field(line: str) -> str:
    m = re.search(r"rcpt:(\[[^\]]+\])", line, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_subject_field(line: str) -> str:
    m = re.search(r"subject:([^|]+)", line, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def rcpt_contains(rcpt_raw: str, recipient: str) -> bool:
    if not rcpt_raw or not recipient:
        return False
    rcpt_lower = rcpt_raw.lower()
    recipient_lower = recipient.lower()
    return recipient_lower in rcpt_lower


def print_filter_table(rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    print("\n邮件信息表格:")
    print("时间 | QID | 发件人信息 | 收件人信息 | 主题")
    print("-" * 100)
    for row in rows:
        print(f"{row['time_cn']} | {row['qid']} | {row['msgsender']} | {row['rcpt']} | {row['subject']}")


def print_filter_summary(info: Dict[str, str], recipient: str) -> None:
    status_hint = "成功（基于过滤日志判断）查看用户目录，或联系收件人确认"
    print(f"发信时间：{info.get('time_en', '')}")
    print(f"发件人：{info.get('msgsender', '')}")
    print(f"收件人：{recipient}")
    print(f"status：{status_hint}")

def run(text: str, sender: str, recipient: str) -> bool:
    lines = text.splitlines()
    s = sender.lower()
    r = recipient.lower()
    if not s or not r:
        return False

    qid_data: Dict[str, Dict[str, object]] = defaultdict(lambda: {"from": None, "to": None, "status": "", "filters": []})
    global_has_sender = False
    global_has_recipient = False
    global_status_segment = ""
    first_relevant_line = ""
    filter_rows: List[Dict[str, str]] = []
    filter_summary_info: Optional[Dict[str, str]] = None

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        postfix_qid = extract_postfix_qid(stripped)
        if postfix_qid:
            data = qid_data[postfix_qid]
            m_from = re.search(r"from=<([^>]+)>", stripped, flags=re.IGNORECASE)
            if m_from:
                addr = m_from.group(1)
                if sender_matches(addr, s):
                    data["from"] = stripped
                    global_has_sender = True
                    if not first_relevant_line:
                        first_relevant_line = stripped
            if f"to=<{r}>" in lower:
                data["to"] = stripped
                status_segment = extract_status_segment(stripped)
                if status_segment:
                    data["status"] = status_segment
                    global_status_segment = status_segment
                global_has_recipient = True
                if not first_relevant_line:
                    first_relevant_line = stripped

        filter_qid = extract_filter_qid(stripped)
        if filter_qid:
            data_f = qid_data[filter_qid]
            data_f["filters"].append(stripped)
            if data_f["from"] is None:
                synthetic_from = extract_sender_from_filter(stripped)
                if synthetic_from:
                    m = re.search(r"from=<([^>]+)>", synthetic_from, flags=re.IGNORECASE)
                    if m and sender_matches(m.group(1), s):
                        data_f["from"] = synthetic_from
                        global_has_sender = True
                        if not first_relevant_line:
                            first_relevant_line = stripped
            # recipient presence in filter logs
            if not data_f.get("to"):
                m_rcpt = re.search(r"rcpt:\s*\['([^']+)'\]", stripped, flags=re.IGNORECASE)
                if m_rcpt and m_rcpt.group(1).lower() == r:
                    data_f["to"] = f"to=<{m_rcpt.group(1)}>"
                    global_has_recipient = True
                    if not first_relevant_line:
                        first_relevant_line = stripped
            if "free_milter_server.py" in lower and "onendheaders" in lower:
                time_en = extract_time(stripped)
                time_cn = convert_to_chinese_time(time_en)
                msgsender = extract_msgsender_field(stripped)
                rcpt_field = extract_rcpt_field(stripped)
                subject = extract_subject_field(stripped) or "(空)"
                if time_cn and filter_qid and msgsender and rcpt_field:
                    if sender_matches(msgsender, sender) and rcpt_contains(rcpt_field, recipient):
                        filter_row = {
                            "time_cn": time_cn,
                            "time_en": time_en,
                            "qid": filter_qid,
                            "msgsender": msgsender,
                            "rcpt": rcpt_field,
                            "subject": subject,
                        }
                        filter_rows.append(filter_row)
                        filter_summary_info = filter_row
            # continue to next line after handling filter qid case
            continue

        # Non-QID fallback detection on arbitrary lines
        m_sender_inline = re.search(r"from=<([^>]+)>", stripped, flags=re.IGNORECASE)
        if m_sender_inline and sender_matches(m_sender_inline.group(1), s):
            global_has_sender = True
            if not first_relevant_line:
                first_relevant_line = stripped
        if f"to=<{r}>" in lower:
            global_has_recipient = True
            status_segment = extract_status_segment(stripped)
            if status_segment:
                global_status_segment = status_segment
            if not first_relevant_line:
                first_relevant_line = stripped
        m_sender_filter = re.search(r"(cmdfrom|msgsender):([^|\s]+)", stripped, flags=re.IGNORECASE)
        if m_sender_filter and sender_matches(m_sender_filter.group(2), s):
            global_has_sender = True
            if not first_relevant_line:
                first_relevant_line = stripped
        m_rcpt_filter = re.search(r"rcpt:\s*\['([^']+)'\]", stripped, flags=re.IGNORECASE)
        if m_rcpt_filter and m_rcpt_filter.group(1).lower() == r:
            global_has_recipient = True
            if not first_relevant_line:
                first_relevant_line = stripped

    printed = False
    for qid, data in qid_data.items():
        if data["from"] and data["to"]:
            from_line = data["from"]
            to_line = data["to"]
            status_segment = data["status"]
            time_value = extract_time(to_line) or extract_time(from_line)
            from_addr = extract_addr(from_line, "from") or from_line
            to_addr = extract_addr(to_line, "to") or to_line
            status_value = extract_status_value(status_segment)
            status_message = extract_status_message(status_segment)
            said_value = extract_said(status_segment)
            delivery_state = determine_delivery_state([status_message, said_value])

            print(f"队列ID：{qid}")
            if time_value:
                print(f"时间： {time_value}")
            print(f"发件人： {from_addr}")
            print(f"收件人： {to_addr}")
            if status_value:
                print(f"状态： {status_value}")
            if status_message:
                print(f"说明： {status_message}")
            if said_value:
                print(f"说明： {said_value}")
            print(f"收发状态：{delivery_state}")
            if data["filters"]:
                print("过滤日志：")
                for fl in data["filters"]:
                    print(f"  {fl}")
            print("")
            printed = True
    if printed:
        print_filter_table(filter_rows)
        return True

    if filter_summary_info:
        print_filter_summary(filter_summary_info, recipient)
        print_filter_table(filter_rows)
        return True

    # Fallback: if sender and recipient are both observed in logs (even without QID/status)
    if global_has_sender and global_has_recipient:
        time_value = extract_time(first_relevant_line)
        from_addr = re.search(r"from=<([^>]+)>", first_relevant_line, flags=re.IGNORECASE)
        to_addr = re.search(r"to=<([^>]+)>", first_relevant_line, flags=re.IGNORECASE)
        if time_value:
            print(f"时间： {time_value}")
        if from_addr:
            print(f"发件人: from=<{from_addr.group(1)}>")
        if to_addr:
            print(f"收件人: to=<{to_addr.group(1)}>")
        status_value = extract_status_value(global_status_segment)
        status_message = extract_status_message(global_status_segment)
        delivery_state = determine_delivery_state([status_message])
        if status_value:
            print(f"Status: {status_value}")
        if status_message:
            print(f"说明： {status_message}")
        print(f"收发状态：{delivery_state}")
        print_filter_table(filter_rows)
        return True

    if filter_rows:
        print_filter_table(filter_rows)
        return True

    return False
