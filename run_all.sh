echo ================================================================================================
echo SPF错误：
python3 analyze_logs.py --log samples/case3.txt --sender gulw@ydamc.com --recipient 18655335713@sohu.com 
echo
echo ================================================================================================
echo HELO错误：
python3 analyze_logs.py --log samples/case4.txt --sender puxiaolu@foton.com.cn --recipient lu_184@sohu.com 
echo
echo ================================================================================================
echo 无相关日志:
python3 analyze_logs.py -l samples/case5.txt -s seller-notification@amazon.co.uk -r yangcaiyunyun@sohu.com 
python3 analyze_logs.py --log samples/case1.txt --sender '@twitter.com' --recipient 'tianjiazhou@sohu.com' 
echo
echo ================================================================================================
echo 250送达：
python3 analyze_logs.py --log samples/case2.txt --sender acxzy@sohu.com --recipient Ylinda@vtb.ru      
python3 analyze_logs.py --log samples/case6.txt --sender lu_184@sohu.com --recipient gscc@substack.com 
echo
echo ================================================================================================
echo 测试log无250，但是有过滤日志，认为邮件发送可能成功
python3 analyze_logs.py -l samples/case6.txt -s benyzy@sohu.com  -r yanzhiyong@yadingdata.com
echo
echo ================================================================================================
