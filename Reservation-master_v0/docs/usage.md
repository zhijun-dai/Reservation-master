# 脚本使用指南

本文介绍日常运行脚本的步骤与常见命令。

## 1. 准备配置

1. 打开 `backend/config.py`。
2. 确认或修改以下字段：
   - `LOGIN_DATA`：登录学号与密码。
   - `DEFAULT_USERS`：随行人员学号，多个学号使用 `/` 分隔。
   - `SERVICE_ID`：目标场馆类型（默认 22）。
   - `ADVANCE_DAY_CANDIDATES`：按优先级排列的提前天数。
   - `PREFERRED_TIME_SLOTS`：希望预约的时间段列表。
   - `VENUE_KEYWORD`（可选）：筛选场地名称包含指定关键字。
   - `BOOKING_HOURS`：允许脚本执行预约请求的时间范围。
   - `SCHEDULE_TIME`：每日定时尝试预约的时间。

> 建议运行前清空 `backend/data/` 下过期的 JSON 缓存，以免引用旧数据。

## 2. 拉取场地并写入配置

```powershell
cd backend
..\.venv\Scripts\activate  # 如果已创建虚拟环境
python config_setup.py
```

脚本会：

- 遍历 `ADVANCE_DAY_CANDIDATES` 找出首个可用日期；
- 带登录态访问学校接口，获取可用场地；
- 根据时间段偏好和关键字规则筛选场地；
- 将选中的场地信息写入 `Config.BOOKING_DATA` 并在终端展示；
- 缓存文件到 `backend/data/service_data_{serviceid}_{date}.json`。

若输出没有符合偏好的场地或未拉取到任何场地数据，请检查放号时间与网络环境。

## 3. 启动调度器

确认 `Config.BOOKING_DATA` 包含有效信息后运行：

```powershell
python scheduler.py
```

运行时会看到：

- 初始化阶段不断尝试执行 `setup_config()`，失败会等待 10 分钟后重试。
- 成功后打印设置定时任务，每天 HH:MM 执行。
- 到达 `SCHEDULE_TIME` 且当前时间位于 `BOOKING_HOURS` 时，输出当前时间在可预约时间段内，开始执行预约流程。
- 预约成功会显示返回消息；常见失败原因也会打印在终端。

保持终端窗口不要关闭即可。如果需要挂在后台，可参考 `docs/installation.md` 的托管部分。

## 4. 手动立即尝试

有时需要立即验证预约流程是否可用，可在完成 `config_setup.py` 后直接运行：

```powershell
python book.py
```

等同于调用 `Booking.book_venue()`，会在当前会话内尝试最多 5 次。

## 5. 常见输出说明

| 输出 | 含义 |
| --- | --- |
| `没有获取到数据` | 接口返回空对象，可能尚未放号或账号无权限 |
| `预约失败：未到该日期的预订时间` | 放号尚未开始，调度器会继续等待并重试 |
| `预约失败：每日限预约一场` | 当天已经成功预约，需要更换账号或等待次日 |
| `请求失败，状态码: XXX` | 学校接口异常或网络问题，脚本会继续重试 |

## 6. 建议的日常流程

1. 每天放号前运行 `python config_setup.py` 确认当天场地情况。
2. 启动或确认 `scheduler.py` 已在运行。
3. 放号时刻关注终端输出，确认是否成功预约。
4. 预约完成后，按需手动停止调度器或让其继续等待下一日。

## 7. 日志与排错

- 终端输出是最直接的运行日志，可根据提示定位问题。
- 如需长期留存日志，可使用 `python scheduler.py > scheduler.log 2>&1` 持续采集。
- 若 `Config.BOOKING_DATA` 未能填充，请检查 `config_setup.py` 输出并验证缓存文件内容。

掌握以上步骤即可完成脚本的日常运行。 
