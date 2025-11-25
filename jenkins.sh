email_address=$1
email_other=$2
email_date=$3

#cd /opt/sohu-emaillog-analyzer-test
cd /opt/sohu-emaillog-analyzer/

echo "sender:$email_address rcptto:$email_other  Date:$email_date "

./remote_mail_grep.sh  $email_address $email_date | tee /tmp/a.log

#grep $email_other /tmp/b.log > /tmp/c.log

/usr/bin/python3 analyze_logs.py -l /tmp/a.log  -s $email_address -r $email_other
