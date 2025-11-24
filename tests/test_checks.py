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
            "FreeMailMilterSmtp INFO msgsender:gscc@substack.com rcpt:['lu_184@sohu.com']\n"
            "other line without 250 status\n"
        )
        self.assertFalse(run_250(text, "gscc@substack.com", "lu_184@sohu.com"))

class TestSpfError(unittest.TestCase):
    def test_spf_error_positive(self):
        text = (
            "FreeMxMilter ERROR SPF Error: client-ip=1.2.3.4; envelope-from=gulw@ydamc.com\n"
        )
        self.assertTrue(run_spf(text, "gulw@ydamc.com", "any@sohu.com"))

    def test_spf_error_sohu_domain_ignored(self):
        text = (
            "FreeMxMilter ERROR SPF Error: client-ip=1.2.3.4; envelope-from=user@vip.sohu.com\n"
        )
        self.assertFalse(run_spf(text, "user@vip.sohu.com", "x@sohu.com"))

    def test_spf_error_not_same_line(self):
        text = (
            "FreeMxMilter ERROR SPF Error: client-ip=1.2.3.4\n"
            "envelope-from=gulw@ydamc.com\n"
        )
        self.assertFalse(run_spf(text, "gulw@ydamc.com", "x@sohu.com"))

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