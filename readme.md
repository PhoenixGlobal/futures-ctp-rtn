# 期货交易 - Trader

``` bash
source .venv/bin/activate
fastapi dev # development
# fastapi run --host 127.0.0.1 # production (生产环境仅允许本地访问)
```

## what, why
职责：报单、记录

+ 功能尽量少
	+ -> 代码更新少 -> 不间断运行
	+ -> 简单 -> 稳定
+ 独立
	+ -> 数据库即使用 container 也要单开一个，不和主应用掺和 -> 主应用几乎不影响
+ 忽略数据结构，仅记录原始数据

## Links
+ [pymongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/get-started/)
+ [ctpwrapper](https://github.com/nooperpudd/ctpwrapper)

#### CTP links
+ [ctpwrapper](https://github.com/nooperpudd/ctpwrapper)
	+ [请求参数](https://github.com/nooperpudd/ctpwrapper/blob/master/ctpwrapper/ApiStructure.py)
	+ [常量](https://github.com/nooperpudd/ctpwrapper/blob/master/ctp/header/ThostFtdcUserApiDataType.h)
+ [SimNow](https://www.simnow.com.cn/product.action)
+ [上海期货交易所](https://www.shfe.com.cn/)
+ [中国金融期货交易所](http://www.cffex.com.cn/cn/index.html)
