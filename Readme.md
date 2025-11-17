# 需求说明

## 使用场景说明

1. 前期情况说明
客服人员在接到有些用户的投诉后，要找运维工程师查询日志，解决一些常见的退信没有
说明的问题。 这个时候需要运维工程师，通过grep 方式查询相关4台机器的日志，形成了
一个日志输出，如user_log.txt。 运维工程师在通过经验对关键字进行检索输出来判断问
题。 

## 解决方案简述
首先日志格式各有不同，每次都有不同的字段和说明。

这里每次提供一个相关的log文件，说明要搜索的关键字，如：“250”；“SPF error”；等。

给出一个单独的程序文件文件，对这个日志进行分析和处理，然后返回判断结果的文字信
息，输出到标准输出。


这个程序最后是被jenkins调用，让客服人员使用，给出明确的问题说明，如250，邮件成功
送达。SPF错误，邮件被拦截等等。 

结构要方便扩展，后期增加不同的格式分析程序，来分析相关的日志。

给出的user_log.txt 文件每次的内容可能不同，分析的脚步程序每次调用不同的分析脚步
多这个文件进行多次分析，如果符合程序分析的内容，就输出结果，如果没有相关的关键字
或不符合分析的方式，就跳过。

## 不同的check脚步，
需要针对给出的日志逐个调用进行查询，如果不匹配调用下一个检查。后期再根据同的情况追加。
所有函数接受到的就是两个参数：收件人、发件人。


### 1. 无相关日志
首先实现无相关日志查询的解决方案，客服人员给出
发件人：@twitter.com    
收件人：tianjiazhou@sohu.com，
检查如果日志里没有两个关键字，在输出总结信息里展示：“无相关日志，联系发件人确认”
如果全部都包含，跳到下一个检查。 
```
--- 收信日志 ---

Nov 13 10:27:31 mx_36_226 postfix/smtp[26167]: 4d6PLW2BQzzDqQP: to=<tianjiazhou@sohu.com>, relay=mx197.mail.sohu.com[10.18.88.75]:25, delay=0.37, delays=0.31/0.01/0/0.05, dsn=2.0.0, status=sent (250 2.0.0 Ok: queued as 8B58512009B)

--- 收信过滤日志 ---

Nov 13 10:27:31 proxy_18_88_85 free_milter_server.py[line: 221] FreeMxMilter INFO 8fa1aa594e984ba098c2245cfc68db82|8080|OnRcptTo|tianjiazhou@sohu.com
Nov 13 10:27:31 proxy_18_88_85 free_milter_server.py[line: 221] FreeMxMilter INFO 8fa1aa594e984ba098c2245cfc68db82|8080|OnEndHeaders|qid:4d6PLW2BQzzDqQP|cmdfrom:15864220066@139.com|msgfrom:=?GB2312?B?zO+809bc?= <15864220066@139.com>|rcpt:['tianjiazhou@sohu.com']|vps_ip:120.232.169.113|subject:111|vps_port:41392|msgsender:15864220066@139.com

--- 发信日志 ---

Nov 13 10:36:53 smtp19_36_251 postfix/smtp[18287]: 4d6PYK5LnFzHnZQ: to=<tianjiazhou@sohu.com>, relay=mx197.mail.sohu.com[10.18.88.75]:25, delay=0.2, delays=0.17/0.01/0/0.02, dsn=2.0.0, status=sent (250 2.0.0 Ok: queued as D063812009B)
Nov 13 10:37:27 smtp19_36_241 postfix/cleanup[17273]: 4d6PYz1vT8zPjxl: message-id=<1763001447.76daeca35a0b49c190bbf4d84f3a7677.tianjiazhou@sohu.com>
Nov 13 10:37:27 smtp19_36_241 postfix/qmgr[32594]: 4d6PYz1vT8zPjxl: from=<tianjiazhou@sohu.com>, size=4540, nrcpt=1 (queue active)
Nov 13 11:21:43 smtp19_36_252 postfix/smtp[29468]: 4d6QY35wrsz1y63: to=<tianjiazhou@sohu.com>, relay=mx197.mail.sohu.com[10.18.88.75]:25, delay=0.17, delays=0.1/0.01/0/0.05, dsn=2.0.0, status=sent (250 2.0.0 Ok: queued as E4C2112009B)

--- 发信过滤日志 ---

Nov 13 10:36:53 proxy_18_88_91 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 35baeee4964f409da49dc0d1a746eb80|8080|OnRcptTo|tianjiazhou@sohu.com
Nov 13 10:36:53 proxy_18_88_91 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 35baeee4964f409da49dc0d1a746eb80|8080|OnEndHeaders|qid:4d6PYK5LnFzHnZQ|cmdfrom:webmaster@vip.sohu.com|msgfrom:webmaster <webmaster@vip.sohu.com>|rcpt:['tianjiazhou@sohu.com']|vps_ip:10.18.88.38|subject:搜狐邮箱售后服务中心|vps_port:35358|msgsender:webmaster@vip.sohu.com
Nov 13 10:37:27 proxy_18_88_91 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 24cceab7a43348e2863d487abab0f93b|8080|OnMailFrom|NORMAL|tianjiazhou@sohu.com|10.18.88.75
Nov 13 10:37:27 proxy_18_88_91 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 24cceab7a43348e2863d487abab0f93b|8080|OnEndHeaders|qid:4d6PYz1vT8zPjxl|cmdfrom:tianjiazhou@sohu.com|msgfrom:tianjiazhou <tianjiazhou@sohu.com>|rcpt:['webmaster@vip.sohu.com']|vps_ip:10.18.88.75|subject:回复:搜狐邮箱售后服务中心|vps_port:56057|msgsender:tianjiazhou@sohu.com
Nov 13 10:37:27 proxy_18_88_91 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 24cceab7a43348e2863d487abab0f93b|8080|OnEndBody|4d6PYz1vT8zPjxl|10.18.88.75|tianjiazhou@sohu.com|回复:搜狐邮箱售后服务中心|tianjiazhou|0.010000|0.011273|
Nov 13 11:21:43 proxy_18_76_58 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 8aec33a2f65142f69c0f4fd392e7d59c|8080|OnRcptTo|tianjiazhou@sohu.com
Nov 13 11:21:43 proxy_18_76_58 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 8aec33a2f65142f69c0f4fd392e7d59c|8080|OnEndHeaders|qid:4d6QY35wrsz1y63|cmdfrom:webmaster@vip.sohu.com|msgfrom:webmaster <webmaster@vip.sohu.com>|rcpt:['tianjiazhou@sohu.com']|vps_ip:10.18.88.38|subject:搜狐邮箱售后服务中心|vps_port:47784|msgsender:webmaster@vip.sohu.com

```
    
### 2. 250收件成功的检查
问题说明：
发件人：acxzy@sohu.com     收件人：Ylinda@vtb.ru     发信时间：11-12     16：51：04    收件人未收到邮件
检查下面的日志，首先包含cmdfrom:acxzy@sohu.com关键字,其次包含rcpt:['ylinda@vtb.ru']关键字
包含250 2.0.0 关键字，基本可以确认信件已经送达。
总结相关信息输出
发信时间：
发件人：
收件人：
status：状态信息


```
✅ 日期格式正确：20251112
--- 收信日志 ---

[INFO] 文件中未找到邮件地址: Ylinda@vtb.ru

--- 收信过滤日志 ---

[INFO] 文件中未找到邮件地址: Ylinda@vtb.ru

--- 发信日志 ---

Nov 12 16:51:12 smtp19_36_252 postfix/smtp[9011]: 4d5xvX3PW7z1y67: to=<Ylinda@vtb.ru>, relay=mx2005.vtb.ru[195.242.83.147]:25, delay=8.2, delays=0.18/0/6.4/1.6, dsn=2.0.0, status=sent (250 2.0.0 OK)

--- 发信过滤日志 ---

Nov 12 16:51:04 proxy_18_76_58 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO f8c42a4130f142ffb637a842ff9bccd8|8080|OnRcptTo|ylinda@vtb.ru
Nov 12 16:51:04 proxy_18_76_58 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO f8c42a4130f142ffb637a842ff9bccd8|8080|OnEndHeaders|qid:4d5xvX3PW7z1y67|cmdfrom:acxzy@sohu.com|msgfrom:acxzy <acxzy@sohu.com>|rcpt:['ylinda@vtb.ru']|vps_ip:10.18.88.29|subject:回复:新用户首次无法登录网银行|vps_port:52532|msgsender:acxzy@sohu.com

```
### 3. spf错误
发件人：gulw@ydamc.com，收件人：18655335713@sohu.com，发信时间11月3日，发信失败，报错截图如下，请协助处理
检查以下的日志信息，如果发件人非sohu.com/vip.sohu.com。
日志里包含发件人地址，并且包含SPF Error。

输出：发件人地址 + SPF错误。

```
✅ 日期格式正确：20251103
--- 收信日志 ---

Nov  3 09:23:28 mx_36_217 postfix/smtpd[26231]: NOQUEUE: milter-reject: MAIL from unknown[114.251.93.36]:34032: 553 5.7.1 Sender ERROR:gulw@ydamc.com: http://mail.sohu.com/info/policy/10; from=<gulw@ydamc.com> proto=ESMTP helo=<mailgw.ydamc.com>
Nov  3 09:31:58 mx_36_214 postfix/smtpd[20026]: NOQUEUE: milter-reject: MAIL from unknown[114.251.93.36]:43358: 553 5.7.1 Sender ERROR C:gulw@ydamc.com: http://mail.sohu.com/info/policy/10; from=<gulw@ydamc.com> proto=ESMTP helo=<mailgw.ydamc.com>
Nov  3 10:47:10 mx_36_225 postfix/smtpd[6089]: NOQUEUE: milter-reject: MAIL from unknown[114.251.93.36]:59510: 553 5.7.1 Sender ERROR C:gulw@ydamc.com: http://mail.sohu.com/info/policy/10; from=<gulw@ydamc.com> proto=ESMTP helo=<mailgw.ydamc.com>
Nov  3 10:53:47 mx_36_223 postfix/smtpd[24962]: NOQUEUE: milter-reject: MAIL from unknown[114.251.93.36]:54684: 553 5.7.1 Sender ERROR C:gulw@ydamc.com: http://mail.sohu.com/info/policy/10; from=<gulw@ydamc.com> proto=ESMTP helo=<mailgw.ydamc.com>
Nov  3 16:05:16 mx_36_227 postfix/smtpd[17279]: NOQUEUE: milter-reject: MAIL from unknown[114.251.93.36]:50180: 553 5.7.1 Sender ERROR C:gulw@ydamc.com: http://mail.sohu.com/info/policy/10; from=<gulw@ydamc.com> proto=ESMTP helo=<mailgw.ydamc.com>

--- 收信过滤日志 ---

Nov  3 09:23:28 proxy_18_88_87 free_milter_server.py[line: 227] FreeMxMilter ERROR 68b16b8eb1bd415ea6e58bcb4416416e|8080|OnMailFrom|401.179075|SPF Error: client-ip=114.251.93.36; helo=mailgw.ydamc.com; envelope-from=gulw@ydamc.com; res=none;
Nov  3 09:31:58 proxy_18_88_83 free_milter_server.py[line: 227] FreeMxMilter ERROR e2a2ccc5a1cf4bb0853127b64da55ed8|8080|OnMailFrom|8.653879|Cache SPF Error: client-ip=114.251.93.36; helo=mailgw.ydamc.com; envelope-from=gulw@ydamc.com; res=none; key=114.251.93.36ydamc.com;
Nov  3 10:47:10 proxy_18_76_57 free_milter_server.py[line: 227] FreeMxMilter ERROR 727fe696a62445ab8e9465ff29e26d94|8080|OnMailFrom|8.509874|Cache SPF Error: client-ip=114.251.93.36; helo=mailgw.ydamc.com; envelope-from=gulw@ydamc.com; res=none; key=114.251.93.36ydamc.com;
Nov  3 10:53:47 proxy_18_88_85 free_milter_server.py[line: 227] FreeMxMilter ERROR 4c8a7f5e60254f50a0a6b1957dab56b7|8080|OnMailFrom|9.313107|Cache SPF Error: client-ip=114.251.93.36; helo=mailgw.ydamc.com; envelope-from=gulw@ydamc.com; res=none; key=114.251.93.36ydamc.com;
Nov  3 16:05:16 proxy_18_88_87 free_milter_server.py[line: 227] FreeMxMilter ERROR bce869246ad743a88305f81682060e5a|8080|OnMailFrom|8.905172|Cache SPF Error: client-ip=114.251.93.36; helo=mailgw.ydamc.com; envelope-from=gulw@ydamc.com; res=none; key=114.251.93.36ydamc.com;

--- 发信日志 ---

[INFO] 文件中未找到邮件地址: gulw@ydamc.com

--- 发信过滤日志 ---

[INFO] 文件中未找到邮件地址: gulw@ydamc.com

```

### 4. helo错误
问题说明:
发件人：puxiaolu@foton.com.cn，收件人：lu_184@sohu.com，发信时间9月25日，发信失败，截图如下，请协助处理
检索发件人并且要求域名非sohu.com

针对以下日志进行检查，如果包含发件人地址
检索发件人并且要求域名非sohu.com

针对以下日志进行检查，如果包含发件人地址，同事包含“Helo command rejected: Host not found”
请输出:helo=<mailgwin.foton.com.cn>
输出发件人
输出“请联系运维工程师增加helo白名单”


```
✅ 日期格式正确：20250925
--- 收信日志 ---

Sep 25 19:38:43 mx_36_215 postfix/smtpd[10161]: NOQUEUE: reject: RCPT from smtp.foton.co.in[123.124.208.100]:36129: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=SMTP helo=<mailgwin.foton.com.cn>
Sep 25 19:40:49 mx_36_228 postfix/smtpd[26925]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:44326: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=ESMTP helo=<mailgwin.foton.com.cn>
Sep 25 19:46:56 mx_36_217 postfix/smtpd[21043]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:53976: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=SMTP helo=<mailgwin.foton.com.cn>
Sep 25 19:51:40 mx_36_213 postfix/smtpd[17955]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:12044: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=SMTP helo=<mailgwin.foton.com.cn>
Sep 25 19:52:02 mx_36_228 postfix/smtpd[28017]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:49896: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=SMTP helo=<mailgwin.foton.com.cn>
Sep 25 19:53:46 mx_32_176 postfix/smtpd[45022]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:20705: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=ESMTP helo=<mailgwin.foton.com.cn>
Sep 25 19:54:12 mx_32_182 postfix/smtpd[42673]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:46967: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<oton.com.cn> to=<lu_184@sohu.com> proto=ESMTP helo=<mailgwin.foton.com.cn>
Sep 25 19:59:52 mx_36_226 postfix/smtpd[14956]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:44452: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=SMTP helo=<mailgwin.foton.com.cn>
Sep 25 20:00:12 mx_36_228 postfix/smtpd[28015]: NOQUEUE: reject: RCPT from unknown[123.124.208.100]:42065: 450 4.7.1 <mailgwin.foton.com.cn>: Helo command rejected: Host not found; from=<puxiaolu@foton.com.cn> to=<lu_184@sohu.com> proto=SMTP helo=<mailgwin.foton.com.cn>

--- 收信过滤日志 ---

Sep 25 19:38:43 proxy_18_76_57 free_milter_server.py[line: 221] FreeMxMilter INFO a37d05bbdf9d4117bc5ce9931088e1d2|8080|OnMailFrom|387.655020|SPF Pass: client-ip=123.124.208.100; helo=mailgwin.foton.com.cn; envelope-from=puxiaolu@foton.com.cn; res=pass;
Sep 25 19:38:43 proxy_18_76_57 free_milter_server.py[line: 221] FreeMxMilter INFO a37d05bbdf9d4117bc5ce9931088e1d2|8080|OnMailFrom|NORMAL|puxiaolu@foton.com.cn|123.124.208.100
Sep 25 19:40:49 proxy_18_88_85 free_milter_server.py[line: 221] FreeMxMilter INFO 60810f7b578a47b98d296ab013988d6c|8080|OnMailFrom|10.972023|Cache SPF Pass: client-ip=123.124.208.100; helo=mailgwin.foton.com.cn; envelope-from=puxiaolu@foton.com.cn; res=pass; key=123.124.208.100foton.com.cn;
Sep 25 19:40:49 proxy_18_88_85 free_milter_server.py[line: 221] FreeMxMilter INFO 60810f7b578a47b98d296ab013988d6c|8080|OnMailFrom|NORMAL|puxiaolu@foton.com.cn|123.124.208.100
Sep 25 19:46:55 proxy_18_88_83 free_milter_server.py[line: 221] FreeMxMilter INFO 9d2555d4490a48e6b7b5b815da68c490|8080|OnMailFrom|8.671045|Cache SPF Pass: client-ip=123.124.208.100; helo=mailgwin.foton.com.cn; envelope-from=puxiaolu@foton.com.cn; res=pass; key=123.124.208.100foton.com.cn;
Sep 25 19:46:55 proxy_18_88_83 free_milter_server.py[line: 221] FreeMxMilter INFO 9d2555d4490a48e6b7b5b815da68c490|8080|OnMailFrom|NORMAL|puxiaolu@foton.com.cn|123.124.208.100
Sep 25 19:51:40 proxy_18_88_83 free_milter_server.py[line: 221] FreeMxMilter INFO 3fdf96d0c49f4a0b8bcfe1e4cc7db42a|8080|OnMailFrom|11.526108|Cache SPF Pass: client-ip=123.124.208.100; helo=mailgwin.foton.com.cn; envelope-from=puxiaolu@foton.com.cn; res=pass; key=123.124.208.100foton.com.cn;
Sep 25 19:51:40 proxy_18_88_83 free_milter_server.py[line: 221] FreeMxMilter INFO 3fdf96d0c49f4a0b8bcfe1e4cc7db42a|8080|OnMailFrom|NORMAL|puxiaolu@foton.com.cn|123.124.208.100
Sep 25 19:52:01 proxy_18_88_87 free_milter_server.py[line: 221] FreeMxMilter INFO 4e248649d61b41de84c0145ac9194192|8080|OnMailFrom|11.126995|Cache SPF Pass: client-ip=123.124.208.100; helo=mailgwin.foton.com.cn; envelope-from=puxiaolu@foton.com.cn; res=pass; key=123.124.208.100foton.com.cn;
Sep 25 19:52:01 proxy_18_88_87 free_milter_server.py[line: 221] FreeMxMilter INFO 4e248649d61b41de84c0145ac9194192|8080|OnMailFrom|NORMAL|puxiaolu@foton.com.cn|123.124.208.100
Sep 25 19:53:46 proxy_18_88_87 free_milter_server.py[line: 221] FreeMxMilter INFO 5c44b771c1be4bc2a23c0a1ac9d00579|8080|OnMailFrom|8.111954|Cache SPF Pass: client-ip=123.124.208.100; helo=mailgwin.foton.com.cn; envelope-from=puxiaolu@foton.com.cn; res=pass; key=123.124.208.100foton.com.cn;
--- 发信日志 ---

Sep 25 20:04:34 smtp19_36_250 postfix/smtp[25410]: 4cXXSx4kcfz4wH8: to=<aolu@foton.com.cn>, relay=smtp.foton.com.cn[123.124.208.100]:25, delay=0.86, delays=0.14/0/0.69/0.03, dsn=2.0.0, status=sent (250 2.0.0 Ok: queued as 7026E1C00ABFFF)

--- 发信过滤日志 ---

Sep 25 20:04:33 proxy_18_88_87 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 1e992059908648fab3c39a9f756154d5|8080|OnRcptTo|puxiaolu@foton.com.cn
Sep 25 20:04:33 proxy_18_88_87 free_milter_server.py[line: 221] FreeMailMilterSmtp INFO 1e992059908648fab3c39a9f756154d5|8080|OnEndHeaders|qid:4cXXSx4kcfz4wH8|cmdfrom:lu_184@sohu.com|msgfrom:lu_184 <lu_184@sohu.com>|rcpt:['puxiaolu@foton.com.cn']|vps_ip:10.18.88.32|subject:测试|vps_port:34396|msgsender:lu_184@sohu.com
```


