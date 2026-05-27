"""
简单的测试脚本：使用 `*_test` 配置进行一次性预约尝试。
- 会把 `Config.LOGIN_DATA` 和 `Config.DEFAULT_USERS` 替换为测试数据
- 开启 `TRY_ALL_SLOTS_FOR_TEST`，以便按顺序尝试当天的所有可用时段
"""
import time

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import _compat

from backend.config import Config
from backend.config_setup import setup_config
from backend.book import book_venue


def main():
    if hasattr(Config, 'LOGIN_DATA_test'):
        Config.LOGIN_DATA = Config.LOGIN_DATA_test
    if hasattr(Config, 'DEFAULT_USERS_test'):
        Config.DEFAULT_USERS = Config.DEFAULT_USERS_test

    Config.TRY_ALL_SLOTS_FOR_TEST = True
    Config.ALLOW_SAME_DAY_BOOKING = True
    Config.AGGREGATE_ALL_DATES = True

    Config.PRIORITIZE_DATES = ['today', 'tomorrow']

    try:
        setup_config()
    except Exception as exc:
        print(f"测试 - 初始化预约配置失败：{exc}")
        return

    print("测试 - 配置完成，开始尝试预约所有候选时段...")
    try:
        book_venue()
    except Exception as exc:
        print(f"测试 - 预约过程中出现错误：{exc}")


if __name__ == '__main__':
    main()
