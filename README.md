# LUTHelper

兰州理工大学选课系统桌面助手。当前处于重构阶段二：Fluent Qt 主壳与静态演示页面。

## 当前状态

- 阶段一：HTML 视觉原型与设计规范已完成。
- 阶段二：PySide6 + Fluent Widgets 主壳、登录弹窗和三页模拟数据界面已完成。
- 真实登录、查课、抢课和账号持久化将在阶段三接入。

## 环境

- Windows 10/11 x64
- Python 3.12
- PySide6 6.12
- PySide6-Fluent-Widgets 1.11

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## 运行

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m luthelper
```

启动后先显示演示登录弹窗，填写任意密码和 4 位验证码即可进入主界面。

## 测试

```powershell
$env:PYTHONPATH = "src"
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q
```

## 目录

```text
prototype/   HTML 视觉原型和评审截图
src/         Python 应用源码
tests/       单元测试与 Qt 测试
docs/        重构计划和 UI 规范
```

## 许可

正式版本计划以 GPLv3 开源。发布前需补充 `LICENSE` 和对应源码地址。
