#!/usr/bin/env python3
import argparse
from pathlib import Path
from checks.no_related import run as check_no_related
from checks.sent_250 import run as check_250_success
from checks.spf_error import run as check_spf_error
from checks.helo_error import run as check_helo_error

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-l", "--log", default="/tmp/a.log")
    ap.add_argument("-s", "--sender")
    ap.add_argument("-r", "--recipient")
    ap.add_argument("positional", nargs="*")
    args = ap.parse_args()
    if len(args.positional) == 3:
        log, sender, recipient = args.positional
    else:
        log = args.log
        sender = args.sender
        recipient = args.recipient
    if not (log and sender and recipient):
        print("用法: python3 analyze_logs.py <LOG_FILE> <SENDER> <RECIPIENT> 或使用 --log --sender --recipient")
        return
    p = Path(log)
    txt = read_text(p)
    if not txt:
        print("[ERROR] 无法读取日志文件")
        return
    if check_250_success(txt, sender, recipient):
        return
    if check_spf_error(txt, sender, recipient):
        return
    if check_helo_error(txt, sender, recipient):
        return
    if check_no_related(txt, sender, recipient):
        return
    print("[INFO] 未匹配到已知检查")

if __name__ == "__main__":
    main()