# 常见问题

汇总脚本使用过程中最常见的疑问与解决方案。

## 配置与准备

### Q: `Config.BOOKING_DATA` 一直是空的怎么办？
A: 运行 `python config_setup.py` 并关注输出。如果提示未拉取到任何场地数据，说明学校尚未放号或账号无权限；若提示没有符合偏好的场地，请调整 `PREFERRED_TIME_SLOTS`、`VENUE_KEYWORD` 或 `ADVANCE_DAY_CANDIDATES`。

### Q: 需要同时预约多个人吗？
A: 在 `config.py` 中将 `DEFAULT_USERS` 设置为多个学号，用 `/` 分隔，例如 `"22011207/22011208"`。脚本会直接将该字符串提交给官方系统。

### Q: 可以抢其他场馆吗？
A: 可以，只要知道对应的 `serviceid`。修改 `SERVICE_ID` 后重新运行 `config_setup.py` 即可。若偏好时间段不同，也一并调整 `PREFERRED_TIME_SLOTS`。

## 拉取数据

### Q: 缓存的 JSON 文件会过期吗？
A: 缓存不会自动清理。建议在每次放号前删除 `backend/data/` 下旧的 `service_data_*` 文件，以确保使用最新数据。

### Q: 运行 `config_setup.py` 报网络错误怎么办？
A: 确认处于校园网或 VPN 环境，且账号可以正常访问 http://order.njmu.edu.cn:8088。如仍失败，可稍后再试或使用浏览器登录验证。

## 自动预约

### Q: 调度器还没到放号时间就退出了？
A: `scheduler.py` 会一直运行，除非手动关闭或抛出未捕获的异常。若终端显示 `KeyboardInterrupt`，可能是不小心按了 `Ctrl+C`；重新运行即可。

### Q: 一直输出未到该日期的预订时间？
A: 说明放号尚未开始，这是正常现象。脚本每次会等待 1 秒后继续尝试，直到放号或遇到其他错误。

### Q: 看到每日限预约一场怎么处理？
A: 代表账号当日已经成功预约。脚本会立即停止尝试，该账号需等待次日或更换账号。

### Q: 想在后台运行还有日志怎么办？
A: 可以使用重定向保存日志，例如：

```powershell
python scheduler.py *> ..\logs\scheduler.log
```

或在 Linux 上：

```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

## 账号与安全

### Q: 密码能否加密存储？
A: 脚本默认在 `config.py` 中明文存放。推荐做法是将密码保存在环境变量中，然后在 `config.py` 中读取，例如 `os.environ.get("NJMU_PASSWORD")`。

### Q: 会不会泄露我的预约记录？
A: 脚本只调用官方接口，不会额外上传数据。请确保运行环境安全，避免共享 `config.py` 或日志文件。

## 其他问题

### Q: 还能访问旧的 Web/API 功能吗？
A: 当前版本已移除相关模块。如需 REST API 或数据库功能，需要回退到旧版本或自行重新实现。

### Q: 想改成短信/邮件提醒可以吗？
A: 可以在 `scheduler.py` 中捕获成功预约的场景，调用第三方通知服务。当前代码没有内置该功能。

### Q: 如何确认预约是否成功？
A: 终端会打印预约成功！及返回信息，同时可登录学校官网查看个人预约记录进行确认。

若文档未覆盖你的问题，可结合终端日志和缓存数据定位，或联系维护者反馈。 
