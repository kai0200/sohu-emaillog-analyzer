#!/usr/bin/env python3
"""
Entrypoint for running log checks on a combined log file.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Tuple

from checks import run_checks

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def main():
    ap = argparse.ArgumentParser(description="分析指定日志文件中的收发记录。")
    ap.add_argument("-l", "--log", dest="log_opt", help="日志文件路径", default="/tmp/a.log")
    ap.add_argument("-s", "--sender", dest="sender_opt", help="发件人邮箱或域名")
    ap.add_argument("-r", "--recipient", dest="recipient_opt", help="收件人邮箱")
    ap.add_argument("log", nargs="?", help="日志文件路径")
    ap.add_argument("sender", nargs="?", help="发件人邮箱或域名")
    ap.add_argument("recipient", nargs="?", help="收件人邮箱")
    args = ap.parse_args()

    log, sender, recipient = resolve_inputs(args.log, args.sender, args.recipient, args.log_opt, args.sender_opt, args.recipient_opt)
    if not (log and sender and recipient):
        ap.print_usage()
        print("示例：python3 analyze_logs.py <LOG_FILE> <SENDER> <RECIPIENT>")
        return

    txt = read_text(Path(log))
    if not txt:
        print("[ERROR] 没有相关日志文件")
        return

    matched = run_checks(txt, sender, recipient)
    if not matched:
        print("[INFO] 未匹配到已知检查")


def resolve_inputs(
    log_pos: Optional[str],
    sender_pos: Optional[str],
    recipient_pos: Optional[str],
    log_opt: Optional[str],
    sender_opt: Optional[str],
    recipient_opt: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Resolve CLI positional/optional parameters into a final triple.
    """
    log = log_pos or log_opt
    sender = sender_pos or sender_opt
    recipient = recipient_pos or recipient_opt
    return log, sender, recipient

if __name__ == "__main__":
    main()