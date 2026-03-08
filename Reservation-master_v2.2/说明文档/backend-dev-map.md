# Backend Developer Map

本文件面向开发者，补充 `architecture.md` 的运行视角，重点描述模块依赖、调用链路、可重构边界与风险点。

## 1. 当前模块图

```text
Start.py (GUI entry)
  -> backend.config (runtime settings)
  -> backend.config_setup.setup_config
      -> backend.fetch_data.FetchData.fetch_service_data
          -> backend.login.Login.get_session
  -> backend.book.Booking.book_venue
      -> backend.login.Login.get_session
  -> backend.scheduler.start_scheduler
      -> backend.scheduler.check_booking_conditions
          -> backend.config_setup.setup_config
          -> backend.book.Booking.book_venue
```

## 2. 模块职责与输入输出

### `backend/config.py`
- 职责: 统一配置中心 + 日期/时间候选计算。
- 输入: 静态配置与当前时间。
- 输出: `BOOKING_DATA` 运行态数据、候选日期/时间计算结果。

### `backend/login.py`
- 职责: 登录并返回带 cookies 的 `requests.Session`。
- 输入: 账号密码（显式参数或 `Config.LOGIN_DATA`）。
- 输出: 已认证 `Session`。

### `backend/fetch_data.py`
- 职责: 请求 `findOkArea` 接口，拉取场地数据。
- 输入: 日期、serviceid。
- 输出: 标准化后的 slots 列表（或 `None`）。

### `backend/config_setup.py`
- 职责: 从线上数据中筛选候选时段并写回 `Config.BOOKING_DATA`。
- 输入: `Config` 中的偏好、日期策略。
- 输出: `slot_candidates` 与首候选。

### `backend/book.py`
- 职责: 构造预约请求，按候选顺序重试下单。
- 输入: `Config.BOOKING_DATA`。
- 输出: 成功即返回；全部失败抛异常。

### `backend/scheduler.py`
- 职责: 定时触发与放号窗口控制。
- 输入: 当前时间、`Config` 调度参数。
- 输出: 触发 `setup_config + book_venue`。

## 3. 关键状态流

1. `setup_config()` 将候选写入 `Config.BOOKING_DATA['slot_candidates']`。
2. `book_venue()` 读取该候选并依次尝试。
3. `scheduler` 每次触发前再跑一次 `setup_config()`，确保候选是最新数据。

结论: 真实业务状态通过 `Config.BOOKING_DATA` 在模块间传递，这是当前最核心的耦合点。

## 4. 已识别的重构边界

### 边界 A: 配置计算 vs IO
- 现状: `config_setup.py` 内同时做网络拉取、偏好排序、日志打印、状态写回。
- 建议: 先拆成 3 层函数
  - 数据源层: 拉取 slots
  - 纯计算层: 从 slots 计算 candidates
  - 状态层: 写回 `Config.BOOKING_DATA`

### 边界 B: 预约执行 vs 错误策略
- 现状: `book.py` 同时负责发请求与 message 分类策略。
- 建议: 将 message 判定封装为策略函数（已完成基础拆分），后续可替换为映射表。

### 边界 C: 调度器 vs 业务动作
- 现状: `scheduler.py` 直接操作 `Config.AGGREGATE_ALL_DATES`。
- 建议: 后续可引入显式参数传递，降低全局状态切换风险。

## 5. 后续安全重构顺序（不改逻辑）

1. 引入 `booking_context` 数据类（替代散落字典键访问）。
2. 将 `config_setup` 的日志与计算分离，便于单测。
3. 为 `book.py` 增加请求函数注入点（便于 mock 测试）。
4. 将 `scheduler` 主循环和单次执行解耦，方便 GUI 控制停止。

## 6. 回归测试最小清单

- `Config.booking_date_candidates_at()` 在跨天时结果正确。
- `setup_config()` 在无候选时抛错、在有候选时正确填充关键字段。
- `book_venue()` 能按候选顺序切换，且成功后立即退出。
- `scheduler.check_booking_conditions()` 在窗口内外行为符合预期。

---
本文件用于后续持续重构时快速对齐模块边界，避免直接进行高风险“大改”。
