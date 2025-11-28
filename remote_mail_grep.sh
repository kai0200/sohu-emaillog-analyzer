#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# 脚本名称: remote_mail_grep.sh
# 功能: 通过 SSH 连接到远程主机，在指定文件中查找一个邮件地址。
# 使用方法: ./remote_mail_grep.sh <USERNAME> <HOSTNAME_OR_IP> <FILE_PATH>

if [ "$#" -ne 3 ]; then
    echo "使用错误：需要三个参数。"
    echo "用法: $0 <SENDER_EMAIL> <RECIPIENT_EMAIL> <LOG_DATE>"
    echo "示例: $0 sender@sohu.com other@domain.com 20251013"
    exit 1
fi

REMOTE_USER="${REMOTE_USER:-root}"
SENDER_EMAIL="$1"
RECIPIENT_EMAIL="$2"
SYSLOG_DATE="$3"
HOST_FREE="10.18.88.48"
HOST_CORP="10.18.88.19"
FILE_FREE_MX="/maildata/syslog/free_mx/${SYSLOG_DATE}.log"
FILE_FREE_SMTP="/maildata/syslog/free_smtp/${SYSLOG_DATE}.log"
FILE_CORP_MX="/maildata/syslog/FreeMxMilter/${SYSLOG_DATE}.log"
FILE_CORP_SMTP="/maildata/syslog/FreeMailMilter/${SYSLOG_DATE}.log"

if [ -z "$SENDER_EMAIL" ] || [ -z "$RECIPIENT_EMAIL" ]; then
    echo "错误：发件人和收件人邮件地址均不能为空。"
    exit 1
fi

validate_date() {
    local s="$1"
    if [[ ! "$s" =~ ^[0-9]{8}$ ]]; then
        echo "❌ 错误：日期格式不正确，应为YYYYMMDD（例如：20251112）"
        exit 1
    fi
    local year=${s:0:4}
    local month=${s:4:2}
    local day=${s:6:2}
    if ((10#$year < 1970 || 10#$year > 2100)); then
        echo "❌ 错误：年份($year)不合法"
        exit 1
    fi
    if ((10#$month < 1 || 10#$month > 12)); then
        echo "❌ 错误：月份($month)不合法"
        exit 1
    fi
    if ! date -d "${year}-${month}-${day}" "+%Y%m%d" >/dev/null 2>&1; then
        echo "❌ 错误：日期($s)不合法"
        exit 1
    fi
    echo "✅ 日期格式正确：$s"
}

is_sohu_email() {
    local email="$1"
    # 检查邮件地址是否包含 sohu.com 或 vip.sohu.com
    if [[ "$email" == *"@sohu.com"* ]] || [[ "$email" == *"@vip.sohu.com"* ]]; then
        return 0  # true
    else
        return 1  # false
    fi
}

escape_regex() {
    local value="$1"
    # 转义正则元字符，避免误匹配
    printf '%s' "$value" | sed -e 's/[].[\*^$(){}+?|\\]/\\&/g'
}

SENDER_REGEX="$(escape_regex "$SENDER_EMAIL")"
RECIPIENT_REGEX="$(escape_regex "$RECIPIENT_EMAIL")"
SEARCH_PATTERN="${SENDER_REGEX}|${RECIPIENT_REGEX}"

execute_remote_grep() {
    local REMOTE_HOST="$1"
    local REMOTE_FILE="$2"
    if [ -z "$REMOTE_USER" ] || [ -z "$SEARCH_PATTERN" ]; then
        echo "[FATAL] 内部错误：函数所需的全局变量 (REMOTE_USER 或 SEARCH_PATTERN) 未定义。" >&2
        return 1
    fi
    local SSH_COMMAND="
if [ -f \"${REMOTE_FILE}\" ]; then
  echo \"--- 搜索结果 (主机: ${REMOTE_HOST}, 文件: ${REMOTE_FILE}) ---\"
  grep -i -E \"${SEARCH_PATTERN}\" \"${REMOTE_FILE}\"
  if [ \$? -ne 0 ]; then
    echo \"[INFO]无相关记录，检查发件人/收件人: ${SENDER_EMAIL} 或 ${RECIPIENT_EMAIL}\"
  fi
else
  echo \"[ERROR] 日志文件不存在，检查日期是否写错: ${REMOTE_FILE}\"
  exit 1
fi
"
    echo ""
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "${SSH_COMMAND}"
}

validate_date "$SYSLOG_DATE"

STATUS=0

# 根据邮件地址域名决定查询哪些日志
if is_sohu_email "$SENDER_EMAIL"; then
    # 如果发件人属于 sohu.com 域，只查询发信相关日志
    echo "--- 发信日志 ---"
    execute_remote_grep  "${HOST_FREE}" "${FILE_FREE_SMTP}" || STATUS=1
    echo "--- 发信过滤日志 ---"
    execute_remote_grep  "${HOST_CORP}" "${FILE_CORP_SMTP}" || STATUS=1
elif is_sohu_email "$RECIPIENT_EMAIL"; then
    # 如果收件人属于 sohu.com 域，只查询收信相关日志
    echo "--- 收信日志 ---"
    execute_remote_grep  "${HOST_FREE}" "${FILE_FREE_MX}" || STATUS=1
    echo "--- 收信过滤日志 ---"
    execute_remote_grep  "${HOST_CORP}" "${FILE_CORP_MX}" || STATUS=1
fi

exit $STATUS
