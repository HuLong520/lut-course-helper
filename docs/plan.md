# LUTHelper 重构计划（WebUI 路线）

## 1. 最终目标

LUTHelper 是一个 Windows x64 单文件绿色应用：

- 用户双击 `抢课助手.exe`。
- 显示终端窗口并启动本地 Web 服务。
- 自动使用系统默认浏览器打开界面。
- 关闭终端或按 `Ctrl+C` 退出，网页随之失效。

最终界面是浏览器级现代 WebUI；Python 继续负责登录、验证码、查课、已选课程、抢课任务和账号配置。

交付优先级：

1. 稳定可用。
2. 单文件、体积受控。
3. 现代 WebUI。
4. 开发效率与可维护性。

## 2. 技术路线

### 2.1 最终形态

```text
抢课助手.exe
├─ Python 启动器
├─ 内嵌 index.html（单 HTML，CSS/JS/图标全部内联）
└─ 本地 HTTP 服务 127.0.0.1:<随机端口>
```

启动流程：

1. 启动 Python 启动器，显示终端。
2. 创建内嵌页面用的临时目录。
3. 启动仅绑定 `127.0.0.1` 的本地 HTTP 服务。
4. 通过 Python `webbrowser` 调用系统默认浏览器。
5. 终端显示访问地址，并持续运行直到用户关闭。

约束：

- 不对局域网开放，只绑定 `127.0.0.1`。
- 不依赖 WebView2、pywebview 或 Electron 窗口。
- 页面资源全部来自内嵌 HTML；浏览器不允许外网访问时仍能使用界面框架。
- 关闭 exe 终端后服务停止，不常驻后台。

### 2.2 已放弃方案

- 放弃 PySide6-Fluent-Widgets 原生桌面 UI；阶段二 Qt 版本停止开发。
- 放弃 pywebview 窗口内嵌；当前环境 WebView2 初始化失败，且该路线不满足“终端 + 默认浏览器”的交互预期。
- 放弃 Electron、Tauri 和独立本地前端工程；它们会增加构建复杂度、包体或重写成本。

已有 Qt 代码与阶段二提交保留为历史参考，不再作为正式产品入口。正式启动入口改为 `webui/launcher.py`。

## 3. 界面与交互

### 3.1 登录

- WebUI 启动时显示登录遮罩，不跳转独立页面。
- 支持账号下拉、新增账号、密码显示切换、验证码刷新。
- 登录按钮提交后由 Python 后端处理。
- 登录中状态、验证码错误和网络错误均在页面内显示。
- 登录成功后遮罩关闭，进入三页主壳。

### 3.2 主导航

三页：

- 课程
- 全校课程
- 已选课程

课程页是主工作台，右侧抢课队列和底部日志抽屉都与它同页。

### 3.3 课程页

- 左栏课程检索，右栏抢课队列，默认比例约 62/38。
- 课程行内使用圆形加号；加入后变为青绿对勾；再次点击取消。
- 单教学班课程在右侧显示为紧凑卡片。
- 多教学班课程使用可折叠卡片。
- 队列顶部使用单个状态按钮：未运行显示“开始全部”，运行后显示红色“全部停止”。
- 队列为空时点击开始，只显示“请先选择课程”。
- 每课线程使用 1–20 的数字输入框。
- 右侧删除课程组或教学班后，左侧加入状态立即同步。
- 日志默认折叠，展开后覆盖主内容，支持课程组筛选、级别筛选、导出和清空。

### 3.4 全校课程

- 进入页面时自动加载。
- 支持手动刷新。
- 关键词和校区筛选在本地完成。
- 勾选教学班后加入待选篮子，再统一加入抢课队列。
- 按课程代码自动分组；加入前显示将创建的课程组数量。

### 3.5 已选课程

- 左侧已选课程列表，右侧周课表。
- 周次支持“全部周次”和 1–20 周。
- 冲突课程块使用红色边框和警示图标。
- 无法排入网格的课程进入“未排入网格”列表。
- 课程详情只读，不提供加入抢课队列。
- 退课记录折叠显示；首版不实现退课写操作。

## 4. 前端与后端边界

### 4.1 单 HTML

正式 WebUI 只有一个 `index.html`，其中包含：

- CSS 变量和全部样式。
- 内联 SVG 图标。
- 模拟数据和正式页面结构。
- 前端交互脚本。

开发阶段保留 `prototype/` 分文件版本，便于维护；发布构建只嵌入合并后的 `webui/index.html`。

### 4.2 Python 接口

Python 后端通过本地 HTTP 接口向前端提供数据：

```text
GET  /api/session
GET  /api/captcha
POST /api/login
POST /api/logout
GET  /api/batches
POST /api/batches/select
GET  /api/courses?type=<type>&campus=<campus>
GET  /api/courses/all
GET  /api/courses/selected
POST /api/tasks/add
POST /api/tasks/remove
POST /api/tasks/start
POST /api/tasks/stop
POST /api/tasks/schedule
GET  /api/logs
```

规则：

- 所有接口只监听 `127.0.0.1`。
- 每个进程生成随机本地会话令牌，前端请求必须带令牌。
- 密码、token 和请求日志不写入前端 DOM。
- 登录成功后 token 只保存在 Python 进程内。

### 4.3 业务层复用

继续使用现有分层：

```text
src/luthelper/domain/         数据模型、错误、协议
src/luthelper/application/    登录、查课、抢课协调、日志
src/luthelper/infrastructure/ LutClient、账号存储、OCR
src/luthelper/web/            本地 HTTP 路由和 JSON 序列化
webui/                        单 HTML 启动器与页面资源
```

Qt 的 `presentation/` 不再迁移到正式入口，只保留历史代码。

## 5. 业务规则（保持不变）

### 5.1 课程组

- 按课程代码 `KCH` 分组。
- 同一课程组内禁止重复 `JXBID`。
- 第一个教学班为首选，后续为备选。
- 同一课程组同一时刻只运行一个教学班。
- 首选不可选时切换到下一个备选。
- 首选恢复余量时，暂停备选并切回首选。
- 组内任一教学班成功，停止本组其余任务。
- 组内顺序只能在整组未开始时调整。

### 5.2 抢课参数

- 请求间隔 50–10000 ms。
- 每课线程 1–20。
- 抢到即停默认开启。
- 固定间隔，不做指数退避。
- 修改参数仅影响之后启动的任务。

### 5.3 成功判定

首版沿用旧版 `code=200` / 关键词判断，预留 `PENDING_CONFIRMATION` 状态；WebSocket 与已选课程核验后续接入。

### 5.4 账号

- 账号密码明文保存在 exe 同级 `accounts.json`。
- 不迁移旧 `config.json` 或 QSettings。
- 首次登录成功后创建文件。
- token 不落盘。
- 任务、日志、筛选条件只在进程内保存。

## 6. 依赖与打包

### 6.1 正式依赖

正式 WebUI 启动器最小依赖：

- Python 3.12
- `requests`
- `beautifulsoup4`
- `lxml`
- `pycryptodome`
- `PyInstaller`

可选：

- `ddddocr`：开发构建使用；正式构建排除。

不再需要：

- PySide6
- PySide6-Fluent-Widgets
- pywebview
- SciPy / NumPy / WebEngine

### 6.2 构建

- 使用 PyInstaller console 模式，确保终端可见。
- 使用 `--onefile`。
- 将 `webui/index.html` 作为 datas 嵌入。
- 正式 exe 名称：`抢课助手.exe`。
- 开发 exe 名称：`LUTHelper-dev.exe`。
- 不使用 UPX。
- 正式构建不包含 OCR 依赖。

当前演示构建：

- `dist/LUTHelper-demo.exe`
- 约 8.4 MB
- console 版
- 内嵌 `index.html`

## 7. 实施阶段

### 阶段 A：单文件 WebUI 验收（当前）

- `prototype/standalone.html` 可独立打开。
- `webui/index.html` 作为正式内嵌页面。
- `webui/launcher.py` 启动本地 HTTP 服务并打开默认浏览器。
- `LUTHelper.spec` 生成 console onefile exe。

验收：

- 双击 exe 出现终端。
- 终端显示本地访问地址。
- 默认浏览器打开 WebUI。
- 关闭终端后网页失效。

### 阶段 B：接入 Python API

- 将 `src/luthelper` 的领域模型接到本地 HTTP 路由。
- 登录、验证码、批次、课程、已选课程改为真实数据。
- 课程加入/取消、任务开始/停止、删除同步改为后端状态。
- 保留前端演示模式作为后端不可用时的降级。

### 阶段 C：抢课协调器

- 实现首选/备选切换。
- 实现每秒全局定时。
- 实现组内成功停止。
- 实现日志事件和 InfoBar 通知。

### 阶段 D：打包与清理

- 正式构建 `抢课助手.exe`。
- 开发构建 `LUTHelper-dev.exe`。
- 验证单文件启动、端口、浏览器打开和退出。
- 旧 Qt 产物归档，不删除历史提交。

## 8. 测试

- `pytest` 覆盖领域模型、账号存储、课程解析和任务状态。
- HTTP 路由测试使用 `127.0.0.1` 临时端口。
- WebUI 运行后检查 `GET /index.html` 返回 200。
- 手工验收终端、默认浏览器、登录遮罩、三页切换和退出。
- 打包后验证 exe 不依赖工作目录，双击即可启动。

## 9. 当前进度

- HTML 原型和全部视觉评审修改完成。
- 单文件 `prototype/standalone.html` 已完成。
- `webui/index.html` 和 console 启动器已完成。
- `dist/LUTHelper-demo.exe` 已生成，当前约 8.4 MB。
- PySide6 / Fluent Widgets 路线已停止；相关提交保留为历史参考。
- 下一阶段开始接入 Python API 和真实登录数据。
