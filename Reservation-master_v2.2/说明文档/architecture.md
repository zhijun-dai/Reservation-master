# 运行架构

当前项目以最小化脚本形式运作，同时提供图形用户界面，整体架构如下：

```
+---------------------+
|  图形界面 (Start.py)  |
+----------+----------+
           |
           v
+---------------------+
|  定时调度 (schedule) |
+----------+----------+
           |
           v
+----------+----------+
|  预约流程控制 book.py |
+----------+----------+
           |
           v
+----------+----------+
|  会话管理 login.py    |
+----------+----------+
           |
           v
+----------+----------+
|  场地数据 fetch_data   |
+----------+----------+
           |
           v
+----------+----------+
|  配置 config/config_setup |
+---------------------+
```

## 关键阶段

1. **配置阶段**
   - `config.py` 定义账号、时间策略、场馆偏好等静态信息。
   - `config_setup.py` 根据配置调用学校接口，筛选出符合偏好的场地，并写入 `Config.BOOKING_DATA`。

2. **执行阶段**
   - `scheduler.py` 使用 `schedule` 库，按照 `Config.SCHEDULE_TIME` 配置的时间触发预约。
   - 在允许的时间段 (`Config.BOOKING_HOURS`) 内调用 `Booking.book_venue()`，失败时根据返回信息自动重试。

3. **数据缓存**
   - `fetch_data.py` 会在 `backend/data/` 下生成 JSON 缓存，避免短时间内重复访问同一日期的接口。

## 组件说明

| 组件 | 职责 |
| --- | --- |
| `config.py` | 集中管理账号、偏好、调度时间等常量 |
| `config_setup.py` | 拉取场地数据并写入 `Config.BOOKING_DATA` |
| `fetch_data.py` | 封装带登录态的 HTTP 请求，支持缓存 |
| `login.py` | 登录学校系统，返回可复用的 `requests.Session` |
| `book.py` | 根据当前配置构造预约请求并自动重试 |
| `scheduler.py` | 每日定时运行预约流程 |
| `Start.py` | 图形用户界面入口，提供可视化配置和操作 |
| `utils.py` | 提供工具函数，如 `generate_payload()` |

## 模块详细说明

### login.py
- `Login.get_session()` 按需使用显式凭证或 `Config.LOGIN_DATA` 登录学校预约系统，并访问一次场馆展示页以确保 Cookie 完整。
- `Login.pre_login()` 仍保留给手动实例化 `Booking` 时使用（当前流程主要依赖静态方法 `Booking.book_venue()`）。

### book.py
- 类 `Booking` 提供两种使用方式：
  - 实例方法 `pre_book()`：使用显式账号密码循环尝试预约，多用于测试或特殊需求。
  - 静态方法 `book_venue()`：读取 `Config.BOOKING_DATA` 并在同一会话内重试 5 次。
- 针对常见错误（未到预约时间、每日限预约一场、响应非 JSON）进行了分类处理，便于及时终止或刷新会话。

### scheduler.py
- `check_booking_conditions()` 是调度入口：
  - 首先确认当前时间位于 `Config.BOOKING_HOURS`。
  - 如果首选日期发生变化，会重新运行 `setup_config()`。
  - 随后调用 `Booking.book_venue()` 并捕获异常。
- `start_scheduler()` 将上述函数注册到 `schedule.every().day.at(Config.SCHEDULE_TIME)`，并持续轮询执行。
- 在脚本作为主程序运行时，会不断尝试 `setup_config()` 直到成功，再启动调度循环。

### utils.py
- 当前仅保留 `generate_payload()` 作为示例工具函数，其逻辑与 `Config.BOOKING_DATA` 相匹配，便于需要调试请求体时复用。

## 调度逻辑

- 程序启动时先调用 `setup_config()`，如果获取失败会按设定间隔重试。
- 进入调度循环后，每分钟检查一次是否到达 `SCHEDULE_TIME`。
- 只要当前时间位于 `BOOKING_HOURS` 内，就尝试执行预约。
- 如果发现首选日期变化（`booking_date_candidates()` 返回的首位发生改变），会自动重新跑一次 `setup_config()`。

## 与旧架构的区别

- 不再包含 FastAPI/CLI 层，也不依赖数据库、仓储模式等复杂抽象。
- 所有状态均在内存中维护，必要时借助 JSON 文件缓存。
- 调度器完全基于 `schedule` 与 `time` 模块，无额外框架。

这套架构的目标是保证脚本轻量、易部署、易维护，同时可按需扩展（例如将预约结果写入日志、对接通知渠道等）。

开发者若需要继续做代码清理与重构，请结合 `backend-dev-map.md`（模块关系与重构边界）。
