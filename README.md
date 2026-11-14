# 采购门户草稿协作台

这是业务接收链路的现有项目。模块边界、来源行为和消费端格式见 `docs/contracts.md`。
演练仅使用项目自己的合成资料与环回服务，不读取外部账户或真实人员信息。

## 运行

Python 3.11。先在独立环境安装 `requirements.txt`；空文件表示仅用标准库。
浏览器项目在准备环境时执行 `python -m playwright install --with-deps chromium`，正式运行不下载浏览器。

```sh
python -m unittest discover -s tests -v
python -m compileall -q .
python demo.py
```

`demo.py` 从干净的临时目录运行当前业务路径，完整打印结构化结果后退出。
HTTP 服务绑定环回随机端口，由上下文管理器关闭；运行时不依赖外网。
原始证据和接收事件可用 `evidence.py` 保存在调用者指定的目录中。

## 持续运行门户

```sh
python3 portal.py --host 127.0.0.1 --port 8080
```

浏览器打开 `http://127.0.0.1:8080/`，输入本地演练账号和密码后登录。
`HOST`、`PORT` 环境变量也可配置监听地址；显式参数优先，Ctrl+C 或 SIGTERM 正常关闭服务。
`npm start -- --host 127.0.0.1 --port 8080` 是同一 Python 服务的启动入口，无 npm 依赖。
不要用静态文件服务器代替门户：页面需要同源的会话、草稿读取和保存接口。
未登录时仅显示登录表单；已有本地会话的页面刷新会恢复草稿，但不会保存或提交。

## 容器

```sh
docker build -t collection-product .
docker run --rm --network none collection-product
docker run --rm --network none collection-product python -m unittest discover -s tests -v
docker run --rm -p 127.0.0.1:8080:8080 collection-product python portal.py --host 0.0.0.0 --port 8080
```

镜像构建是依赖准备阶段。测试和演练在已准备的镜像中执行；不要在测试内安装依赖。
