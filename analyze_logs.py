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
    ap.add_argument("--log", default="user_log.txt")
    ap.add_argument("--sender", required=True)
    ap.add_argument("--recipient", required=True)
    args = ap.parse_args()
    p = Path(args.log)
    txt = read_text(p)
    if not txt:
        print("[ERROR] 无法读取日志文件")
        return
    if check_250_success(txt, args.sender, args.recipient):
        return
    if check_spf_error(txt, args.sender, args.recipient):
        return
    if check_helo_error(txt, args.sender, args.recipient):
        return
    if check_no_related(txt, args.sender, args.recipient):
        return
    print("[INFO] 未匹配到已知检查")

if __name__ == "__main__":
    main()