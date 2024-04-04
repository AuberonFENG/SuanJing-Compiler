# 算经解释器程序说明书 （开发者）

### 使用的Python库

```py
pip install flask==3.0.1 flask-ext=0.1 flask-session 0.7.0 werkzeug==3.0.1
```


### 如何使用:
1. 安装所有python依赖库
2. 运行文件"**main.py**"
3. 自动打开网页"http://127.0.0.1:8080/user/homepage"

### 文件解释:
1. 根目录: <br>
    "main.py" 是程序主文件；<br>
    "readme.md" 是程序说明（本文件） <br>
    "app"文件里包含了所有子文件. <br>
3. 在"app"文件夹中: <br>
    "controller" 存储了所有控制文件包含lexer, parser, user <br>
    "templates" 存储了所有用户界面程序（html css）<br>
    "static" 存储了所有静态资源库，即网页背景等 <br>


### THE END. Thanks for reading this instruction.
