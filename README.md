# 兰理工选课助手

兰州理工大学选课系统 WebUI 助手。

## 当前形态

- 双击 console 版 exe。
- 终端启动本地 Web 服务。
- 使用系统默认浏览器打开单页 WebUI。
- 关闭终端或按 `Ctrl+C` 退出服务。
- HTML、CSS、JavaScript 和图标全部内嵌在 exe 中。

当前是演示构建，真实登录、查课和抢课接口正在接入。

## 运行演示 exe

```text
dist\LUT-Course-Helper.exe
```

启动后终端会显示：

```text
兰理工选课助手 WebUI
本地地址：http://127.0.0.1:<端口>/index.html
```

浏览器没有自动打开时，手动访问终端中的地址。

## 源码运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe webui\launcher.py
```

## 构建

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean LUT-Course-Helper.spec
```

输出：

```text
dist\LUT-Course-Helper.exe
```

## 目录

```text
prototype/       HTML 原型、评审截图和单文件原型
webui/           内嵌 WebUI 与 console 启动器
src/luthelper/   领域、应用与未来的 HTTP API
tests/           自动化测试
docs/            重构计划和 UI 规范
```

## 说明

- 本地服务只绑定 `127.0.0.1`，不对局域网开放。
- 页面不依赖外部 CDN；字体使用系统字体。
- Qt / Fluent Widgets 路线已放弃，旧代码仅作为历史参考。
