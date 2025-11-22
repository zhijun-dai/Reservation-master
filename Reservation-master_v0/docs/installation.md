# 安装与配置

本文档介绍如何准备运行南京医科大学场馆自动预约脚本的环境。

## 系统要求

- Python 3.10 及以上版本（推荐与示例环境保持一致）
- Windows、macOS 或 Linux
- 能访问学校预约系统的网络（校园网或 VPN）

## 安装步骤

1. **获取代码**

   下载或克隆项目后进入 `backend` 目录：

   ```powershell
   cd Reservation-master_v0\backend
   ```

2. **创建虚拟环境（可选但推荐）**

   ```powershell
   python -m venv ..\.venv
   ..\.venv\Scripts\activate
   ```

3. **安装依赖**

   ```powershell
   pip install -r requirements.txt
   ```

   当前仅依赖两个包：

   - `requests`：访问学校预约接口
   - `schedule`：管理每日定时任务

## 配置脚本

所有核心配置位于 `config.py`：

- `LOGIN_DATA`：预约登录账号和密码
- `DEFAULT_USERS`：入场人员学号（多个学号用 `/` 分隔）
- `SERVICE_ID`：场馆类型，默认 `22` 表示羽毛球馆
- `ADVANCE_DAY_CANDIDATES`：放号后希望抢的提前天数列表
- `PREFERRED_TIME_SLOTS`：按优先级设置的时间段
- `VENUE_KEYWORD`：可选的场地名称关键字过滤
- `BOOKING_HOURS`：允许执行预约请求的时间段
- `SCHEDULE_TIME`：每日自动尝试预约的时间

配置完毕后，运行 `config_setup.py` 以拉取场地并校验配置：

```powershell
python config_setup.py
```

脚本会在 `backend/data/` 下生成缓存文件 `service_data_{serviceid}_{date}.json`，并在终端打印当前选中的场地信息。

## 启动自动预约

在确认 `Config.BOOKING_DATA` 已正确填充后启动调度器：

```powershell
python scheduler.py
```

调度器会：

- 启动时循环执行 `setup_config()`，直到找到可用场地；
- 每天按照 `SCHEDULE_TIME` 触发预约逻辑；
- 仅在 `BOOKING_HOURS` 指定的时间范围内发送预约请求；
- 遇到未到预约时间等提示时自动重试。

保持终端运行即可。如果需要在服务器或无头环境中常驻，可以继续参考下节的托管方式。

## 托管与守护

### Windows 任务计划

1. 使用任务计划程序创建基本任务。
2. 触发器设置为每日在 `SCHEDULE_TIME` 之前运行。
3. 操作选择启动程序，指向虚拟环境中的 `python.exe`，参数填写 `scheduler.py` 的完整路径。

### Linux systemd

创建服务文件 `/etc/systemd/system/njmu-reservation.service`：

```
[Unit]
Description=NJMU reservation scheduler
After=network.target

[Service]
WorkingDirectory=/path/to/Reservation-master_v0/backend
ExecStart=/path/to/Reservation-master_v0/.venv/bin/python scheduler.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

然后执行：

```bash
sudo systemctl enable --now njmu-reservation.service
```

## 升级与维护

1. 停止正在运行的调度器进程。
2. 更新代码或配置后重新运行 `config_setup.py` 校验场地。
3. 重新启动 `scheduler.py`。

若修改了账号或时间段偏好，记得清理 `backend/data/` 下的旧缓存，以免使用过期数据。
