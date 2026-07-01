# 期货交易 - Trader

职责：报单、记录

+ 功能尽量少
	+ -> 代码更新少 -> 不间断运行
	+ -> 简单 -> 稳定
+ 独立
	+ -> 数据库即使用 container 也要单开一个，不和主应用掺和 -> 主应用几乎不影响
+ 忽略数据结构，仅记录原始数据

## Links
+ [pymongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/get-started/)
