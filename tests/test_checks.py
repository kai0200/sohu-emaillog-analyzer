import unittest
from checks.sent_250 import run as run_250
from checks.spf_error import run as run_spf
from checks.helo_error import run as run_helo
from checks.no_related import run as run_no_related

class TestSent250(unittest.TestCase):
    def test_sent_250_success(self):
        text = (
            "Nov 12 16:51:12 smtp19 postfix/smtp[9011]: to=<lu_184@sohu.com>, dsn=2.0.0, status=sent (250 2.0.0 OK)\n"
            "FreeMailMilterSmtp INFO msgsender:gscc@substack.com rcpt:['lu_184@sohu.com']\n"
        )
        self.assertTrue(run_250(text, "gscc@substack.com", "lu_184@sohu.com"))

    def test_sent_250_missing_250_line(self):
        text = (
            #"FreeMailMilterSmtp INFO msgsender:gscc@substack.com rcpt:['lu_184@sohu.com']\n"
            "Nov 13 10:36:53 proxy_18_88_91 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 35baeee4964f409da49dc0d1a746eb80|8080|OnEndHeaders|qid:4d6PYK5LnFzHnZQ|cmdfrom:webmaster@vip.sohu.com|msgfrom:webmaster <webmaster@vip.sohu.com>|rcpt:['tianjiazhou@sohu.com']|vps_ip:10.18.88.38|subject:搜狐邮箱售后服务中心|vps_port:35358|msgsender:webmaster@vip.sohu.com"
            "other line without 250 status\n"
        )
        # 修改：现在只要有过滤日志信息就返回 True
        self.assertTrue(run_250(text, "webmaster@vip.sohu.com", "tianjiazhou@sohu.com"))

class TestSpfError(unittest.TestCase):
    def test_spf_error_positive(self):
        text = (
            "Nov  3 09:31:58 proxy_18_88_83 free_milter_server.py[line: 227] FreeMxMilter ERROR e2a2ccc5a1cf4bb0853127b64da55ed8|8080|OnMailFrom|8.653879|Cache SPF Error: client-ip=114.251.93.36; helo=mailgw.ydamc.com; envelope-from=gulw@ydamc.com; res=none; key=114.251.93.36ydamc.com;"
        )
        self.assertTrue(run_spf(text, "gulw@ydamc.com", "any@sohu.com"))

class TestHeloError(unittest.TestCase):
    def test_helo_error_positive(self):
        text = (
            "Sep 25 19:40:49 postfix/smtpd: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> helo=<mailgwin.foton.com.cn>\n"
        )
        self.assertTrue(run_helo(text, "puxiaolu@foton.com.cn", "lu_184@sohu.com"))

    def test_helo_error_sohu_domain_ignored(self):
        text = (
            "reject: 450 4.7.1 <host>: Helo command rejected: Host not found; from=<user@sohu.com> helo=<host>\n"
        )
        self.assertFalse(run_helo(text, "user@sohu.com", "r@sohu.com"))

class TestNoRelated(unittest.TestCase):
    def test_no_related_true_when_only_info_lines(self):
        text = (
            "[INFO] 文件中未找到邮件地址: sender@example.com\n"
            "[INFO] 文件中未找到邮件地址: recipient@example.com\n"
        )
        self.assertTrue(run_no_related(text, "sender@example.com", "recipient@example.com"))

    def test_no_related_false_when_both_present(self):
        text = (
            "cmdfrom:sender@example.com\n"
            "rcpt:['recipient@example.com']\n"
        )
        self.assertFalse(run_no_related(text, "sender@example.com", "recipient@example.com"))

if __name__ == "__main__":
    unittest.main()
