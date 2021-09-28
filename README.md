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
scripts:
  - pattern: \.py$    # [必填] 正则表达式，匹配 .py 结尾的文件
    program: python   # [必填] 使用 python 来执行文件
    priority: -1      # 优先级，一个文件可能会匹配多个配置，程序会使用优先级最高的配置，默认为 0
    environment: # 环境变量
      PYTHONPATH: /xxx/site-packages
    groups: # 用户组访问权限，不写均可访问
      - admin
```

## .scignore

忽略的文件和目录不会在前端展示

```
site-packages/
README.md
```

## 用户系统

- 不登录会以匿名用户的形式展示；
- 系统特定的 admin 为管理员组，其它组可以随意自定义组名；
- 程序启动时会在运行日志打印一个的 admin token，用以首次启动系统时使用。

## 截图

![](./screenshot/screenshot1.png)
