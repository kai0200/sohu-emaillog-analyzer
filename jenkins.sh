email_address=$1
email_other=$2
email_date=$3

cd /opt/sohu-emaillog-analyzer/

echo $email_address  
echo $email_other
echo $email_date

./remote_mail_grep.sh  $email_address $email_other $email_date > /tmp/a.log

# 分析qid
./analyze_qid.sh $email_address $email_other /tmp/a.log >> /tmp/a.log

#grep $email_other /tmp/b.log > /tmp/c.log

# 分析日志，这里还要修改sent_250.py脚本， 如果没有检索到发件人from=<>收件人to=<> 的记录，则认为没有成功发送。
/usr/bin/python3 analyze_logs.py -l /tmp/c.log  -s $email_address -r $email_other
