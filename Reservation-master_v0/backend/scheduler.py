import schedule
import time
from book import Booking
from config import Config
from config_setup import setup_config

def check_booking_conditions():
    """判断是否在可预约时间内并执行预约"""
    if not Config.is_booking_time():
        print(f"当前时间不在预约时间段内（{Config.BOOKING_HOURS[0]}:00 - {Config.BOOKING_HOURS[1]}:00）")
        return

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
        Booking.book_venue()  # 直接调用预约函数
    except Exception as exc:
        print(f"自动预约失败：{exc}")
    finally:
        Config.AGGREGATE_ALL_DATES = prev_aggregate_flag

def start_scheduler():
    """启动定时任务，每天在设定的时间运行"""
    schedule_time = Config.SCHEDULE_TIME
    print(f"设置定时任务，每天 {schedule_time} 执行")
    schedule.every().day.at(schedule_time).do(check_booking_conditions)

    if Config.is_booking_time():
        print("当前处于预约时间段，立即执行一次预约检查...")
        check_booking_conditions()

    while True:
        schedule.run_pending()
        idle = schedule.idle_seconds()
        sleep_duration = 0.2 if idle is None else max(0.0, min(idle, 0.2))
        time.sleep(sleep_duration)  # 高频检查，保持触发延迟在 0.2 秒以内

if __name__ == "__main__":
    while True:
        try:
            setup_config()
            break
        except Exception as exc:
            print(f"初始化预约配置失败：{exc}")
            print("将在 10 分钟后重试加载场地数据...")
            time.sleep(600)

    start_scheduler()
