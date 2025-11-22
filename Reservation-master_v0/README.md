# 南京医科大学场馆自动预约脚本

当前版本的仓库已被精简为一套纯脚本化的自动预约流程。我们只保留了连通学校场馆预约系统所需的核心文件：

- `backend/config.py`：集中管理账号密码、日期策略、时间段偏好等配置。若需提交到 GitHub，请改写并引用 `backend/config.example.py`。
- `backend/config_setup.py`：按配置抓取场地信息并填充 `Config.BOOKING_DATA`。
- `backend/fetch_data.py`：使用登录态请求学校接口并返回实时 JSON 数据（默认不再落地缓存）。
- `backend/login.py`：封装登录逻辑，返回带 Cookie 的 `requests.Session`。
- `backend/book.py`：根据 `Config.BOOKING_DATA` 构造预约请求并自动重试。
- `backend/scheduler.py`：每日定时执行预约流程，可直接运行。

> 默认针对羽毛球馆（`serviceid=22`）。请在校园网或 VPN 环境下使用。

## 快速开始

### 1. 创建虚拟环境并安装依赖

```powershell
cd backend
python -m venv ..\.venv
..\.venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` 只保留了 `requests` 和 `schedule`，满足自动预约所需的全部依赖。

### 2. 配置账号与偏好

修改 `backend/config.py`：

- `LOGIN_DATA['dlm']` / `LOGIN_DATA['mm']`：登录学号和密码。
- `DEFAULT_USERS`：实际入场的学号，多个学号用 `/` 分隔。
- `SERVICE_ID`：场馆类型，羽毛球场默认为 `22`。
- `PRIORITIZE_DATES`：日期优先级（如 `['tomorrow', 'today']`）。
- `ALLOW_SAME_DAY_BOOKING`：是否在候选列表中纳入 “今天”。
- `WEEKLY_PREFERRED_TIME_SLOTS` / `PREFERRED_TIME_SLOTS`：按星期或全局的时间段偏好。
- `VENUE_KEYWORD`：可选关键字过滤场地名称。
- `AGGREGATE_ALL_DATES`：是否在一次运行中遍历今明两天所有场地/时段。

### 3. 预拉取场地并确认配置

```powershell
..\.venv\Scripts\python.exe config_setup.py
```

该脚本将：

1. 按 `PRIORITIZE_DATES` 和 `ALLOW_SAME_DAY_BOOKING` 生成日期候选；
2. 在线实时拉取每个日期的场地数据；
3. 根据周维度或全局的时间段偏好筛选可用场地；
4. 将今明两天（或配置的全部日期）写入 `Config.BOOKING_DATA['slot_candidates']`，供预约流程逐个尝试。

若提示“未拉取到场地”或“没有符合偏好”，请确认：

- 学校是否已经对目标日期放号；
- 当前机器是否处于校园网或 VPN 环境；
- `SERVICE_ID`、时间段关键字是否设置正确。

### 4. 启动自动预约

```powershell
..\.venv\Scripts\python.exe scheduler.py
```

- 启动后会先循环调用 `setup_config()`，直至成功选中场地。
- 处于可预约时间段时会立即尝试一次；其余时间按照 `Config.SCHEDULE_TIME` 指定的时间（默认每日 08:00）执行预约。
- 只有在 `Config.BOOKING_HOURS` 覆盖的时间段内才会真正发出预约请求。
- 每次预约前都会重新拉取最新场地；当优先日期发生切换时同样会刷新配置。

运行时请保持终端开启，或将脚本交由任务计划（Windows Task Scheduler、Linux systemd 等）托管。

## 常见操作

- **手动立即尝试预约**：确保 `config_setup.py` 运行成功后，执行 `python book.py`。
- **查看候选列表**：关注 `setup_config()` 输出或在调度输出中查看 “候选总数/日期”。
- **调整时间段优先级**：直接修改 `PREFERRED_TIME_SLOTS` 的顺序即可。

## 常见问题

| 现象 | 建议排查 |
| --- | --- |
| 登录失败或请求异常 | 校园网/VPN 状态、账号密码是否正确、学校系统是否可访问 |
| 一直提示“未到该日期的预订时间” | 学校尚未放号，调度器会在时间范围内自动重试 |
| 返回“每日限预约一场” | 说明账号当日已有成功预约，需更换账号或次日再试 |
| 获取到的场地列表为空 | 可能已被抢空或学校尚未放号，也可能是 `SERVICE_ID` / 日期优先级配置不匹配 |

## 与旧版本的区别

- 移除了 FastAPI、数据库模型、命令行交互等不再使用的模块。
- `requirements.txt` 缩减为最小依赖集合。
- 文档改写为以脚本为中心的操作指南。
- 保留的 `frontend/` 目录未与自动预约脚本联动，若无需求可以忽略。

如需恢复旧版的 Web/API 功能，请回退到早期提交或自行重新引入相关模块。当前版本聚焦于“最少配置即可自动抢场地”。
