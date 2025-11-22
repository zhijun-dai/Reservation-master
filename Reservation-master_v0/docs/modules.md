# 模块说明

当前脚本化方案只保留了与自动预约直接相关的少量模块。本页按照执行路径介绍它们的职责和关键函数。

## 模块关系概览

- 提供 `save_data_to_json()` / `load_data_from_json()` 在 `backend/data/` 下处理缓存。

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

## 模块关系概览

```
config.py 
           
config_setup.py > 填充 Config.BOOKING_DATA
           
fetch_data.py 
       
login.py 
                 
book.py <
   
scheduler.py  定时触发 check_booking_conditions()
```

## 已移除的模块

- `models.py`、`repositories.py`、`main.py`、`routers.py`、`cli.py` 等与 FastAPI 或数据库相关的文件已从运行流程中剔除。
- 若未来需要恢复旧功能，可参考历史提交或重新引入对应实现；当前文档不再覆盖这些模块。

这样精简的模块划分使预约逻辑更加直观：配置  拉取数据  填充参数  定时预约，所有状态都在内存与少量 JSON 缓存中完成。 
