# script-console

_Web Terminal_

## 安装

### docker

```shell
git clone https://github.com/Dog-Egg/script-console.git

cd script-console

docker build -t script-console .

docker run --rm -v /xxx/scripts:/scripts -v /xxx/data:/data -P -d script-console
```

## .sc-conf.yaml

脚本配置文件

```yaml
commands:
  - pattern: \.py$    # [必填] 正则表达式，匹配 .py 结尾的文件
    program: python   # [必填] 使用 python 来执行文件
    environment: # 环境变量
      PYTHONPATH: /xxx/site-packages
access:
  - pattern: adminGroup   # [必填] 正则表达式
    groups: # 用户组访问权限
      - admin
```

## 用户系统

- 不登录会以匿名用户的形式展示；
- 系统特定的 admin 为管理员组，其它组可以随意自定义组名；
- 程序启动时会在运行日志打印一个的 admin token，用以首次启动系统时使用。

## 截图

![](./screenshot/screenshot1.png)

## TODO List

- [ ] 交互式控制台
- [ ] 支持飞书、钉钉登录
