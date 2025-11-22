# config.py
import datetime

# .venv\Scripts\activate
class Config:
    # 登录账号信息（请替换为你同学的真实账号密码）
    LOGIN_DATA = {
        # 将以下占位符替换为真实的账号/密码
        'dlm': '<YOUR_STUDENT_ID>',
        'mm': '<YOUR_PASSWORD>',
        'yzm': '1',
        'logintype': 'sno',
        'continueurl': '',
        'openid': ''
    }
    LOGIN_DATA_test = {
        'dlm': '<TEST_STUDENT_ID>',
        'mm': '<TEST_PASSWORD>',
        'yzm': '1',
        'logintype': 'sno',
        'continueurl': '',
        'openid': ''
    }

    # 默认使用者学号（多个以 / 分隔），用于预约接口中的 users 字段
    DEFAULT_USERS = '<YOUR_STUDENT_ID>'

    DEFAULT_USERS_test = '<TEST_STUDENT_ID>'

    # 羽毛球馆 serviceid 固定为 22，如需其他场馆请调整
    SERVICE_ID = '22'

    # 优先预约的时间段列表（按顺序尝试），格式保持与平台一致
    PREFERRED_TIME_SLOTS = [
        '20:01-21:00',
        '19:01-20:00',
        '21:01-22:00'
    ]

    # 每周的优先预约时间段，可按星期粒度配置；未指定的日期会退回到 PREFERRED_TIME_SLOTS
    WEEKLY_PREFERRED_TIME_SLOTS = {
        "monday": ['18:01-19:00', '19:01-20:00', '20:01-21:00'],
        "tuesday": ['20:01-21:00', '19:01-20:00', '21:01-22:00'],
        "wednesday": ['18:01-19:00', '19:01-20:00'],
        "thursday": ['18:01-19:00', '19:01-20:00'],
        "friday": ['20:01-21:00', '19:01-20:00', '21:01-22:00'],
        "saturday": ['20:01-21:00', '19:01-20:00', '21:01-22:00'],
        "sunday": ['20:01-21:00', '19:01-20:00', '21:01-22:00']
    }

    # 可选：限定场馆名称包含的关键字（例如 “体育馆”），留空则不限制
    VENUE_KEYWORD = ''

    # 是否在没有匹配到偏好时间段时回退到任意可用场地
    FALLBACK_TO_FIRST_AVAILABLE = True

    # 是否允许将今天纳入候选（设置为 False 将跳过当天）
    ALLOW_SAME_DAY_BOOKING = True

    # 优先尝试的日期顺序：'today' 在前表示先抢当天，可选值 'today' / 'tomorrow'
    PRIORITIZE_DATES = ['tomorrow', 'today']

    # 是否在配置阶段聚合所有候选日期的时段（不影响偏好筛选）
    AGGREGATE_ALL_DATES = False

    # 运行时会在此字典中存放最新预约参数
    BOOKING_DATA = {
        'serviceid': SERVICE_ID,
        'users': DEFAULT_USERS,
        'date': '',
        'time_slot': '',
        'venue_id': '',
        'stockid': '',
        'stockdetail_id': ''
    }

    # 基础 URL
    BASE_URL = 'http://order.njmu.edu.cn:8088'

    # 预约允许执行的时间段
    BOOKING_HOURS = (8, 23)

    # 每天自动尝试预约的时间
    SCHEDULE_TIME = "08:00"

    # 测试时强制尝试所有时段（供 scheduler_test.py 使用）
    TRY_ALL_SLOTS_FOR_TEST = False
    @staticmethod
    def is_booking_time():
        """判断当前时间是否在允许的预约时间段内"""
        now = datetime.datetime.now().time()
        start_time = datetime.time(Config.BOOKING_HOURS[0], 0)
        end_time = datetime.time(Config.BOOKING_HOURS[1], 0)
        return start_time <= now <= end_time

    WEEKDAY_NAMES = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    )

    @staticmethod
    def preferred_time_slots_for_date(date_value):
        """返回指定日期应当尝试的时间段列表。"""
        if isinstance(date_value, datetime.date):
            target_date = date_value
        else:
            try:
                target_date = datetime.date.fromisoformat(str(date_value))
            except ValueError:
                target_date = None

        weekly = Config.WEEKLY_PREFERRED_TIME_SLOTS or {}
        if target_date:
            weekday_index = target_date.weekday()
            weekday_key = Config.WEEKDAY_NAMES[weekday_index]
            candidates = (
                weekly.get(weekday_key)
                or weekly.get(weekday_key[:3])
                or weekly.get(str(weekday_index))
                or weekly.get('default')
            )
        else:
            candidates = weekly.get('default')

        if not candidates:
            candidates = Config.PREFERRED_TIME_SLOTS

        return [slot.strip() for slot in candidates if slot and slot.strip()]

    @staticmethod
    def booking_date_candidates():
        """按优先级返回可尝试的预约日期列表。"""
        priority_raw = getattr(Config, 'PRIORITIZE_DATES', None) or ['today', 'tomorrow']
        dates = []
        today = datetime.date.today()
        now = datetime.datetime.now()

        # 如果当前仍在可预约时间段内，或存在一个偏好时段的开始时间在今天之后，优先将今天纳入候选
        include_today = False
        try:
            # 当配置了偏好时间段时，判断是否有偏好时段的开始时间晚于当前时间
            for ts in Config.preferred_time_slots_for_date(today):
                if not ts or '-' not in ts:
                    continue
                start_str = ts.split('-')[0].strip()
                hh, mm = start_str.split(':')
                start_time = datetime.time(int(hh), int(mm))
                if now.time() < start_time:
                    include_today = True
                    break
        except Exception:
            include_today = False

        # 如果当前时间在允许的预约时间段内，也可以尝试今天
        if Config.is_booking_time():
            include_today = True

        allow_same_day = getattr(Config, 'ALLOW_SAME_DAY_BOOKING', True)

        # 解析优先级配置
        priority_offsets = []
        for entry in priority_raw:
            if entry is None:
                continue
            text = str(entry).strip().lower()
            if not text:
                continue
            if text == 'today':
                priority_offsets.append(0)
                continue
            if text == 'tomorrow':
                priority_offsets.append(1)
                continue
            if text.startswith('day+'):
                try:
                    priority_offsets.append(int(text.replace('day+', '')))
                    continue
                except ValueError:
                    pass
            try:
                priority_offsets.append(int(text))
            except ValueError:
                continue

        ordered_offsets = []
        seen_offsets = set()

        def push_offset(value: int):
            if value == 0 and not allow_same_day:
                return
            if value == 0 and not include_today:
                return
            if value in seen_offsets:
                return
            ordered_offsets.append(value)
            seen_offsets.add(value)

        for value in priority_offsets:
            push_offset(value)

        if not ordered_offsets:
            fallback_list = []
            if allow_same_day and include_today:
                fallback_list.append(0)
            fallback_list.append(1)
            for candidate in fallback_list:
                try:
                    push_offset(int(candidate))
                except (TypeError, ValueError):
                    continue
                if ordered_offsets:
                    break

        for days in ordered_offsets:
            target = today + datetime.timedelta(days=days)
            dates.append(target.isoformat())

        return dates

    @staticmethod
    def next_booking_date():
        """返回首选的预约日期。"""
        return Config.booking_date_candidates()[0]