# scheduler_test.py
"""
简单的测试脚本：使用 `*_test` 配置进行一次性预约尝试。
- 会把 `Config.LOGIN_DATA` 和 `Config.DEFAULT_USERS` 替换为测试数据
- 开启 `TRY_ALL_SLOTS_FOR_TEST`，以便按顺序尝试当天的所有可用时段
"""
from config import Config
from config_setup import setup_config
from book import Booking
import time


def main():
    # 覆盖为 test 数据
    if hasattr(Config, 'LOGIN_DATA_test'):
        Config.LOGIN_DATA = Config.LOGIN_DATA_test
    if hasattr(Config, 'DEFAULT_USERS_test'):
        Config.DEFAULT_USERS = Config.DEFAULT_USERS_test

    # 强制在测试中尝试所有时段
    Config.TRY_ALL_SLOTS_FOR_TEST = True
    Config.ALLOW_SAME_DAY_BOOKING = True
    Config.AGGREGATE_ALL_DATES = True

    # 测试时我们希望优先尝试今天
    Config.PRIORITIZE_DATES = ['today', 'tomorrow']

    # 尝试一次配置并执行预约（单次运行）
    try:
        setup_config()
    except Exception as exc:
        print(f"测试 - 初始化预约配置失败：{exc}")
        return

    print("测试 - 配置完成，开始尝试预约所有候选时段...")
    try:
        Booking.book_venue()
    except Exception as exc:
        print(f"测试 - 预约过程中出现错误：{exc}")


if __name__ == '__main__':
    main()
