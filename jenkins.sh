email_address=$1
email_other=$2
email_date=$3

cd /opt/sohu-emaillog-analyzer/

echo $email_address  
echo $email_other
echo $email_date

./remote_mail_grep.sh  $email_address $email_date > /tmp/b.log

grep $email_other /tmp/b.log > /tmp/c.log


/usr/bin/python3 analyze_logs.py -l /tmp/c.log  -s $email_address -r $email_other
