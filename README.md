# open-link-tool
openlink上位机

## 开发

### Python版本 3.8.10
https://www.python.org/downloads/release/python-3810/

### 安装 qfluentwidget
pip install "PyQt-Fluent-Widgets[full]" -i https://pypi.org/simple/

### 安装依赖
pip install -r requirements.txt

### 运行
python demo.py

## Nuitka打包
### 安装
```shell
python -m pip install -U nuitka
```

### 打包命令
```shell
python -m nuitka --mingw64 --standalone --show-memory --enable-plugin=pyqt5 --plugin-enable=numpy --show-progress --output-dir=output demo.py 

```

第一次打包时，会提示你下载一个 C 语言缓存工具（以加速重复编译生成的 C 代码）和一个基于 MinGW64 的 C 语言编译器，输入`yes`即可。
命令选项的含义
```
–mingw64：Windows 上基于gcc的 MinGW64 编译器（ --clang，–msvc=MSVC_VERSION，–mingw64）
–standalone：程序打包成一个可独立执行的文件夹（将这个文件夹复制到其他没有python环境的电脑上，依然可以运行）。与之对应的是–onefile：将程序打包成一个文件。
–show-memory：显示内存使用情况
–show-progress：显示打包进度
–output-dir=output：在项目文件根目录下生成一个output文件夹，demo.py：程序入口文件
```

```
--mingw64 #默认为已经安装的vs2017去编译，否则就按指定的比如mingw(官方建议)
--standalone 独立环境，这是必须的(否则拷给别人无法使用)
--windows-disable-console 没有CMD控制窗口
--output-dir=out 生成exe到out文件夹下面去
--show-progress 显示编译的进度，很直观
--show-memory 显示内存的占用
--enable-plugin=pyside6
--plugin-enable=tk-inter 打包tkinter模块的刚需
--plugin-enable=numpy 打包numpy,pandas,matplotlib模块的刚需
--plugin-enable=torch 打包pytorch的刚需
--plugin-enable=tensorflow 打包tensorflow的刚需
--windows-icon-from-ico=你的.ico 软件的图标
--windows-company-name=Windows下软件公司信息
--windows-product-name=Windows下软件名称
--windows-file-version=Windows下软件的信息
--windows-product-version=Windows下软件的产品信息
--windows-file-description=Windows下软件的作用描述
--windows-uac-admin=Windows下用户可以使用管理员权限来安装
--linux-onefile-icon=Linux下的图标位置
--onefile 像pyinstaller一样打包成单个exe文件(2021年我会再出教程来解释)
--include-package=复制比如numpy,PyQt5 这些带文件夹的叫包或者轮子
--include-module=复制比如when.py 这些以.py结尾的叫模块
```
### 可能出现的一些问题

https://blog.csdn.net/weixin_42636075/article/details/142623816

## CONFIG文件设计

最上层是机器名称，直接对应了treeNode的rootname，为了兼容多个机器，可直接在设置文件中修改
[MACHINE-0]
machine_name = Galzer-Maker
module1_addr = 0x0100
module1_name = ESP32
module2_addr = 0x0200
module2_name = ESP32
