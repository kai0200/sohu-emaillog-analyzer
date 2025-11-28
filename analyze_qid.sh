#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -ne 3 ]; then
    echo "用法: $0 <SENDER_EMAIL> <RECIPIENT_EMAIL> <LOG_FILE>"
    echo "示例: $0 webmaster@vip.sohu.com xdlyb@qq.com /tmp/a.log"
    exit 1
fi

SENDER_EMAIL="$1"
RECIPIENT_EMAIL="$2"
LOG_FILE="$3"

if [ ! -f "$LOG_FILE" ]; then
    echo "错误：未找到日志文件 ${LOG_FILE}" >&2
    exit 1
fi

awk -v sender="$SENDER_EMAIL" -v recipient="$RECIPIENT_EMAIL" '
BEGIN {
    sender_pattern = "from=<" sender ">"
    recipient_pattern = "to=<" recipient ">"
}
/--- 发信过滤日志 ---/ { exit }
{
    if (match($0, / ([0-9A-Za-z]+): /, m) == 0) {
        next
    }
    qid = m[1]

    if (index($0, sender_pattern) > 0) {
        if (!(qid in idx)) {
            idx[qid] = ++count
            order[count] = qid
        }
        from_line[qid] = $0
    }

    if (index($0, recipient_pattern) > 0) {
        if (!(qid in idx)) {
            idx[qid] = ++count
            order[count] = qid
        }
        to_line[qid] = $0
    }
}
END {
    printed = 0
    for (i = 1; i <= count; i++) {
        qid = order[i]
        if (!(qid in from_line) || !(qid in to_line)) {
            continue
        }
        output = qid
        output = output "\tFROM: " from_line[qid]
        output = output "\tTO: " to_line[qid]
        print output
        printed++
    }
    if (printed == 0) {
        print "未找到匹配的发/收件记录。" > "/dev/stderr"
        exit 1
    }
}
' "$LOG_FILE"

