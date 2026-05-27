# 南京医科大学场馆自动预约系统 v2.2

自动预约羽毛球场的图形界面工具。双击即用，无需编程。

## 快速开始

```powershell
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\pip install -r Reservation-master_v2.2\backend\requirements.txt

# 2. 启动
.venv\Scripts\python.exe Reservation-master_v2.2\Start.py
```

或者直接双击 `Reservation-master_v2.2\install.bat`（安装依赖），再双击 `启动预约系统.bat`（启动程序）。

## 核心文件

| 文件 | 作用 |
|------|------|
| `Start.py` | Tkinter 图形界面入口，4 个标签页：首页、配置、操作、日志 |
| `backend/config.py` | 配置项：账号、时间段偏好、日期优先级、网络参数 |
| `backend/login.py` | `get_session()` — 登录学校 SSO，返回带 Cookie 的 Session |
| `backend/fetch_data.py` | `fetch_service_data()` — 查询指定日期的可用场地 |
| `backend/config_setup.py` | `setup_config()` — 拉取数据并按偏好过滤，写入候选列表 |
| `backend/book.py` | `book_venue()` — 逐个尝试候选，自动重试（5 次/个） |
| `backend/scheduler.py` | 每日 08:00 自动拉取数据并预约 |
| `_compat.py` | 统一后端模块的导入路径 |

## 配置说明

`backend/config.py` 中：

- `LOGIN_DATA` — 登录学号和密码
- `DEFAULT_USERS` — 入场人学号（多个用 `/` 分隔）
- `PRIORITIZE_DATES` — 日期优先级，如 `['tomorrow', 'today']`
- `PREFERRED_TIME_SLOTS` — 全局时间段偏好（按顺序尝试）
- `WEEKLY_PREFERRED_TIME_SLOTS` — 按星期几的时间段偏好
- `FETCH_SCAN_DAYS = 3` — 预拉取时扫描未来 N 天
- `SCHEDULE_TIME = "08:00"` — 每日自动预约时间
- `REQUEST_TIMEOUT_SECONDS = 10` — 网络请求超时

设置页已支持点击数字（1/2/3...）排序时间段和日期优先级。

## 数据流

```
配置 → get_session() → fetch_service_data(date, serviceid)
  → setup_config() 按偏好过滤 → BOOKING_DATA['slot_candidates']
  → book_venue() 逐个尝试（含重试）
```
