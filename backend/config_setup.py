from typing import Any

try:
    from .config import Config
    from .fetch_data import FetchData
except ImportError:
    # 兼容直接在 backend 目录下运行脚本
    from config import Config
    from fetch_data import FetchData


def _normalize_time(value: str) -> str:
    return (value or '').replace(' ', '')


def _load_slots(date: str, serviceid: str) -> list[dict[str, Any]]:
    # 始终从服务端拉取最新数据，确保时效性
    data = FetchData.fetch_service_data(date, serviceid)
    return data or []


def _slot_time_no(slot: dict[str, Any]) -> str:
    return _normalize_time(slot.get('stock', {}).get('time_no', ''))


def _build_slot_candidate(date: str, slot: dict[str, Any]) -> dict[str, str]:
    return {
        'time_no': _slot_time_no(slot),
        'stockid': str(slot.get('stockid', '')),
        'stockdetail_id': str(slot.get('id', '')),
        'sname': slot.get('sname', ''),
        'date': date,
    }


def _print_available_times(slots: list[dict[str, Any]]) -> None:
    available_times = {_slot_time_no(slot) for slot in slots}
    print(f"- 可用时间段: {sorted(available_times)}")


def _has_preferred_match(candidates: list[dict[str, Any]], preferred_times: list[str]) -> bool:
    for slot in candidates[:10]:
        if _slot_time_no(slot) in preferred_times:
            return True
    return False


def _print_summary(all_slot_candidates: list[dict[str, str]]) -> None:
    print("配置已完成，已收集候选时段:")
    print(f"- 候选总数: {len(all_slot_candidates)} (按日期/时间段/场地组合计)")
    print("- 预约尝试顺序:")
    for idx, cand in enumerate(all_slot_candidates, start=1):
        print(f"  {idx}. {cand.get('date')} {cand.get('time_no')} {cand.get('sname')}")

    date_counter: dict[str, int] = {}
    for cand in all_slot_candidates:
        key = cand.get('date', '未知日期')
        date_counter[key] = date_counter.get(key, 0) + 1

    print("- 日期分布:")
    for date, count in sorted(date_counter.items()):
        print(f"  {date}: {count} 个候选")


def _pick_preferred_slots(date: str, slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
            time_no = _slot_time_no(slot)
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
    all_slot_candidates: list[dict[str, str]] = []
    first_candidate_info: dict[str, str] | None = None
    last_error = None
    for date in Config.booking_date_candidates():
        print(f"准备预约 {date} 的场次 (serviceid={serviceid})")
        slots = _load_slots(date, serviceid)
        if not slots:
            last_error = f"{date} 未拉取到任何场地数据。"
            continue

        # 显示优先时间段
        preferred_times = [_normalize_time(ts) for ts in Config.preferred_time_slots_for_date(date)]
        print(f"- 优先时间段: {preferred_times}")
        
        _print_available_times(slots)

        candidates = _pick_preferred_slots(date, slots)
        if not candidates:
            last_error = f"{date} 没有符合偏好的场地。"
            continue

        # 检查是否有匹配的偏好时间段
        matched_preferred = _has_preferred_match(candidates, preferred_times)
        
        if matched_preferred:
            print("- 成功匹配到偏好时间段，按优先级排序")
        else:
            print("- 未匹配到偏好时间段，使用所有可用场地")

        slot_candidates = [_build_slot_candidate(date, slot) for slot in candidates]
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

    _print_summary(all_slot_candidates)
    print(f"- 使用者: {Config.BOOKING_DATA['users']}")


if __name__ == "__main__":
    setup_config()