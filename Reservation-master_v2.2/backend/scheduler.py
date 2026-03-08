import datetime
import schedule
import time
import threading

try:
    from .book import Booking
    from .config import Config
    from .config_setup import setup_config
except ImportError:
    # 兼容直接在 backend 目录下运行脚本
    from book import Booking
    from config import Config
    from config_setup import setup_config


SCHEDULER_POLL_INTERVAL_CAP_SECONDS = 0.2
_scheduler_stop_event = threading.Event()


def _release_window_state(now: datetime.datetime | None = None):
    """返回 (是否在放号窗口, 本次窗口起点, 本次窗口终点)"""
    now = now or datetime.datetime.now()
    start, end = Config.release_window_bounds(now)
    if start <= now < end:
        return True, start, end

    if now < start:
        return False, start, end

    next_start = start + datetime.timedelta(days=1)
    next_end = end + datetime.timedelta(days=1)
    return False, next_start, next_end

def check_booking_conditions():
    """判断是否在可预约时间内并执行预约"""
    in_window, next_start, _ = _release_window_state()
    if not in_window:
        preview_dates = Config.booking_date_candidates_at(next_start)
        next_ts = next_start.strftime("%Y-%m-%d %H:%M")
        print(f"当前不在放号窗口（{Config.SCHEDULE_TIME} 至 +{Config.RELEASE_WINDOW_MINUTES}min），"
              f"将等待 {next_ts} 再尝试。")
        print(f"- 下一次触发预计尝试日期: {preview_dates}")
        return

    now = datetime.datetime.now()
    runtime_dates = Config.booking_date_candidates_at(now)
    print(f"本次触发时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- 本次按当前时间计算的候选日期: {runtime_dates}")

    # 运行计划任务时聚合所有目标日期的候选，确保覆盖今明两天
    prev_aggregate_flag = getattr(Config, 'AGGREGATE_ALL_DATES', False)
    Config.AGGREGATE_ALL_DATES = True

    print("刷新场地信息，确保使用最新的场地数据...")
    try:
        setup_config()
    except Exception as exc:
        print(f"刷新场地信息失败：{exc}")
        Config.AGGREGATE_ALL_DATES = prev_aggregate_flag
        return

    print("当前时间在可预约时间段内，开始执行预约流程...")
    try:
        Booking.book_venue()
    except Exception as exc:
        print(f"自动预约失败：{exc}")
    finally:
        Config.AGGREGATE_ALL_DATES = prev_aggregate_flag

def start_scheduler():
    """启动定时任务，每天在设定的时间运行"""
    _scheduler_stop_event.clear()
    schedule.clear()

    schedule_time = Config.SCHEDULE_TIME
    print(f"设置定时任务，每天 {schedule_time} 执行")
    schedule.every().day.at(schedule_time).do(check_booking_conditions)

    in_window, next_start, _ = _release_window_state()
    now = datetime.datetime.now()

    if in_window:
        print("\n当前处于放号窗口，立即执行一次预约检查...")
        check_booking_conditions()
    else:
        wait_hours = max(0.0, (next_start - now).total_seconds() / 3600)
        preview_dates = Config.booking_date_candidates_at(next_start)
        print(f"\n距离下一次放号还有约 {wait_hours:.2f} 小时。")
        print(f"下一次触发时间: {next_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"下一次触发预计尝试日期: {preview_dates}")

    while not _scheduler_stop_event.is_set():
        schedule.run_pending()
        idle = schedule.idle_seconds()
        sleep_duration = (
            SCHEDULER_POLL_INTERVAL_CAP_SECONDS
            if idle is None
            else max(0.0, min(idle, SCHEDULER_POLL_INTERVAL_CAP_SECONDS))
        )
        # 高频检查，保持触发延迟在一个较小常量区间内
        time.sleep(sleep_duration)

    schedule.clear()
    print("调度器已停止。")


def stop_scheduler():
    """请求停止调度器主循环。"""
    _scheduler_stop_event.set()

if __name__ == "__main__":
    print("启动场馆预约调度器...")
    print("====================================")
    
    # 显示预约配置信息
    schedule_time = Config.SCHEDULE_TIME
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_preferred = Config.preferred_time_slots_for_date(tomorrow)
    
    print("预约配置信息:")
    print(f"- 预约时间: 每天 {schedule_time}")
    print(f"- 优先日期: {Config.PRIORITIZE_DATES}")
    print(f"- 明天 ({tomorrow}) 优先时间段: {tomorrow_preferred}")
    print(f"- 放号窗口: {schedule_time} 至 +{Config.RELEASE_WINDOW_MINUTES}分钟")
    print(f"- 预约逻辑: 按优先级顺序尝试所有候选时段，直到成功")
    print("- 注意: 实际预约时会在放号窗口内重新拉取最新场地数据")
    print("====================================")
    
    # 启动调度器
    start_scheduler()
