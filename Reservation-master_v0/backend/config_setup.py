from config import Config
from fetch_data import FetchData


def _normalize_time(value: str) -> str:
    return (value or '').replace(' ', '')


def _load_slots(date: str, serviceid: str):
    # 始终从服务端拉取最新数据，确保时效性
    data = FetchData.fetch_service_data(date, serviceid)
    return data or []


def _pick_preferred_slots(date: str, slots):
    """返回按偏好顺序排列的候选时段列表（可能为空）。
    如果开启 Config.TRY_ALL_SLOTS_FOR_TEST，则返回所有符合关键字过滤的时段，顺序与输入相同。
    """
    preferred_times = [_normalize_time(ts) for ts in Config.preferred_time_slots_for_date(date)]
    keyword = Config.VENUE_KEYWORD.strip()

    # 测试模式：强制尝试所有时段（按原始顺序）
    if getattr(Config, 'TRY_ALL_SLOTS_FOR_TEST', False):
        result = []
        for slot in slots:
            if not keyword or keyword in slot.get('sname', ''):
                result.append(slot)
        return result

    matches = []
    # 先按偏好时间顺序收集匹配项
    for pref in preferred_times:
        for slot in slots:
            time_no = _normalize_time(slot.get('stock', {}).get('time_no', ''))
            if time_no == pref and (not keyword or keyword in slot.get('sname', '')):
                if slot not in matches:
                    matches.append(slot)

    # 回退到任意可用场地（优先包含关键字的场地）
    if Config.FALLBACK_TO_FIRST_AVAILABLE and slots:
        if keyword:
            for slot in slots:
                if keyword in slot.get('sname', '') and slot not in matches:
                    matches.append(slot)
        for slot in slots:
            if slot not in matches:
                matches.append(slot)

    return matches


def setup_config():
    serviceid = Config.SERVICE_ID
    users = Config.DEFAULT_USERS.strip()
    if not users:
        raise ValueError("Config.DEFAULT_USERS 不能为空，请在 config.py 中设置使用者学号。")

    aggregate_mode = (
        getattr(Config, 'TRY_ALL_SLOTS_FOR_TEST', False)
        or getattr(Config, 'AGGREGATE_ALL_DATES', False)
    )
    all_slot_candidates = []
    first_candidate_info = None
    last_error = None
    for date in Config.booking_date_candidates():
        print(f"准备预约 {date} 的场次 (serviceid={serviceid})")
        slots = _load_slots(date, serviceid)
        if not slots:
            last_error = f"{date} 未拉取到任何场地数据。"
            continue

        candidates = _pick_preferred_slots(date, slots)
        if not candidates:
            last_error = f"{date} 没有符合偏好的场地。"
            continue

        slot_candidates = []
        for slot in candidates:
            slot_candidates.append({
                'time_no': _normalize_time(slot.get('stock', {}).get('time_no', '')),
                'stockid': str(slot.get('stockid', '')),
                'stockdetail_id': str(slot.get('id', '')),
                'sname': slot.get('sname', ''),
                'date': date
            })
        if aggregate_mode:
            all_slot_candidates.extend(slot_candidates)
            if first_candidate_info is None and slot_candidates:
                first_candidate_info = slot_candidates[0]
            # 在测试模式下继续收集后续日期
            continue
        else:
            all_slot_candidates = slot_candidates
            first_candidate_info = slot_candidates[0]
            break

    if not all_slot_candidates or first_candidate_info is None:
        raise RuntimeError(last_error or "无法获取任何可用的预约场地，请检查配置。")

    Config.BOOKING_DATA['serviceid'] = serviceid
    Config.BOOKING_DATA['users'] = users
    Config.BOOKING_DATA['slot_candidates'] = all_slot_candidates
    Config.BOOKING_DATA['date'] = first_candidate_info.get('date', '')
    Config.BOOKING_DATA['time_slot'] = first_candidate_info.get('time_no', '')
    Config.BOOKING_DATA['stockid'] = first_candidate_info.get('stockid', '')
    Config.BOOKING_DATA['stockdetail_id'] = first_candidate_info.get('stockdetail_id', '')
    Config.BOOKING_DATA['venue_id'] = first_candidate_info.get('stockdetail_id', '')
    Config.BOOKING_DATA['sname'] = first_candidate_info.get('sname', '')

    print("配置已完成，已收集候选时段:")
    print(f"- 候选总数: {len(all_slot_candidates)} (按日期/时间段/场地组合计)")
    print(f"- 首个候选: {first_candidate_info.get('date')} {first_candidate_info.get('time_no')} {first_candidate_info.get('sname')}")
    date_counter = {}
    for cand in all_slot_candidates:
        key = cand.get('date', '未知日期')
        date_counter[key] = date_counter.get(key, 0) + 1
    for date, count in sorted(date_counter.items()):
        print(f"- {date}: {count} 个候选")
    print(f"- 使用者: {Config.BOOKING_DATA['users']}")


if __name__ == "__main__":
    setup_config()