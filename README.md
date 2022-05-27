# flask_rum
rum client with flask


```sh
set FLASK_APP=app.py
set FLASK_DEBUG=1
flask run
```

code reformat:

```sh
isort .
black -l 80 -t py37 -t py38 -t py39 -t py310 .
black -l 120 -t py37 -t py38 -t py39 -t py310 .

```


 pyinstaller -F -i BreezePython.ico --add-data="HttpServer\static;HttpServer\static" --add-data="HttpServer\templates;Httpserver\templates" --add-data="settings.py;." manage.py

执行打包：

pyinstaller -F -i FlaskRum.ico --add-data="static;static" --add-data="templates;templates"  app.py

遇到报错：没放图

FileNotFoundError: Icon input file D:\Jupyter\flask_rum\FlaskRum.ico not found

遇到报错：图的尺寸不对，改之；在线转换 http://www.zuohaotu.com/image-to-ico.aspx 

struct.error: unpack requires a buffer of 16 bytes


也可以用 python 直接运行

from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = ['application.py', '--add-data=templates;templates', '--name=demo']
    run(opts)

打包成功后，确实是个exe，但是只是后台，不是前台的浏览器

想要双击exe打开后，直接是应用。

一个新的工具：

https://blog.csdn.net/lpwmm/article/details/117671483

要在源码中调用 ui 的库，并用 ui 来run

编译后，只能访问静态网页，其它网页会有报错

ui的实例要加入 host 参数试试

