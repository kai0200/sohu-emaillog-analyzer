# 修改日志

## 调用顺序

- SPF错误 → HELO错误 → 无相关日志 → 250送达
- 这样可避免“无相关日志”抢先命中而屏蔽更具体的结论（如 SPF、HELO）

## 运行示例

- SPF错误：
  """ python3 analyze_logs.py --log samples/case3.txt --sender gulw@ydamc.com --recipient 18655335713@sohu.com """
- HELO错误：
  """ python3 analyze_logs.py --log samples/case4.txt --sender puxiaolu@foton.com.cn --recipient lu_184@sohu.com """
- 无相关日志
  """ python3 analyze_logs.py -l samples/case5.txt -s seller-notification@amazon.co.uk -r yangcaiyunyun@sohu.com """
  """ python3 analyze_logs.py --log samples/case1.txt --sender '@twitter.com' --recipient 'tianjiazhou@sohu.com' """

- 250送达：
  """ python3 analyze_logs.py --log samples/case2.txt --sender acxzy@sohu.com --recipient Ylinda@vtb.ru      """
  """ python3 analyze_logs.py --log samples/case6.txt --sender lu_184@sohu.com --recipient gscc@substack.com """

- 测试log无250，但是有过滤日志，认为邮件发送可能成功
  """python3 analyze_logs.py -l samples/case6.txt -s benyzy@sohu.com  -r yanzhiyong@yadingdata.com"""


## 文件位置

- 模块文件： checks/*.py
- 主程序： analyze_logs.py
- 示例日志： samples/case*.txt

## 扩展建议

- 为每个模块提供统一接口 run(text, sender, recipient) -> bool （已实现），后续新增检查只需添加新文件并在主程序中引入
- 若后续检查共享工具函数，可再抽取 checks/common.py 以减少重复逻辑


## 单元测试

```shell
- (TraeAI-3) ~/Documents/sohu-emaillog-analyzer [5]
$ python3 -m unittest discover -s tests -p "test*.py" -q
$ python3 -m unittest tests.test_checks.TestSent250 -v
```


## 新增模式

- 支持位置参数： python3 analyze_logs.py <LOG_FILE> <SENDER> <RECIPIENT>
- 保留原有可选参数： python3 analyze_logs.py --log <LOG_FILE> --sender <SENDER> --recipient <RECIPIENT>

## 实现说明

- 参数解析增加位置参数收集，长度为 3 时优先生效
- 若位置参数未提供，则回退至原有 --log/--sender/--recipient 解析
- 任一参数缺失时输出简要用法并退出


## 20251124 增加sent_250.py模块，支持发信日志表格输出

发信日志表格输出

```shell
python3 analyze_logs.py -l samples/case1.txt  -s webmaster@vip.sohu.com -r tianjiazhou@sohu.com
- 时间 | QID | 发件人信息 | 收件人信息 | 主题
- 11月13日 10:36:53 | 4d6PYK5LnFzHnZQ | webmaster <webmaster@vip.sohu.com> | tianjiazhou@sohu.com | 搜狐邮箱售后服务中心
- 11月13日 10:37:27 | 4d6PYz1vT8zPjxl | tianjiazhou@sohu.com | webmaster@vip.sohu.com | 回复:搜狐邮箱售后服务中心
- 11月13日 11:21:43 | 4d6QY35wrsz1y63 | tianjiazhou@sohu.com | webmaster@vip.sohu.com | 搜狐邮箱售后服务中心
```
