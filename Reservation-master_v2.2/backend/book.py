"""场地预约执行模块。"""

import json
import time
from typing import Any
from urllib.parse import urlencode

import requests

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import _compat

from backend.config import Config
from backend.login import get_session


MAX_RETRY_PER_CANDIDATE = 5
RETRY_SLEEP_SECONDS = 1
RETRYABLE_MESSAGES = (
    '未到该日期的预订时间',
    '系统繁忙',
    '请稍后重试',
)
NON_RETRYABLE_MESSAGES = (
    '已过有效期',
    '该场地已被预约',
    '预约时间已过',
    '超出可预约时间段',
)


def _encode_payload(payload: dict[str, Any]) -> str:
    """将 payload 字典转换为 URL 编码的字符串"""
    return urlencode({
        "param": json.dumps(payload["param"]),
        "num": payload["num"],
        "json": payload["json"]
    })


def _create_headers(serviceid: str) -> dict[str, str]:
    """创建请求头"""
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{Config.BASE_URL}/cgyd/product/show.html?id={serviceid}"
    }


def _booking_candidates() -> list[dict[str, Any]]:
    """返回候选列表，兼容旧字段。"""
    candidates = Config.BOOKING_DATA.get('slot_candidates')
    if candidates:
        return candidates

    return [{
        'time_no': Config.BOOKING_DATA.get('time_slot', ''),
        'stockid': Config.BOOKING_DATA.get('stockid', ''),
        'stockdetail_id': Config.BOOKING_DATA.get('stockdetail_id', ''),
        'sname': Config.BOOKING_DATA.get('sname', ''),
    }]


def _build_payload(candidate: dict[str, Any], serviceid: str) -> dict[str, Any]:
    """根据候选项构建预约请求负载。"""
    return {
        "param": {
            "stockdetail": {
                str(candidate.get('stockid', '')): str(candidate.get('stockdetail_id', ''))
            },
            "serviceid": serviceid,
            "stockid": f"{candidate.get('stockid', '')},",
            "remark": "",
            "users": Config.BOOKING_DATA['users'],
        },
        "num": 1,
        "json": True,
    }


def _is_retryable_message(message: str) -> bool:
    return any(key in message for key in RETRYABLE_MESSAGES)


def _is_non_retryable_message(message: str) -> bool:
    return any(key in message for key in NON_RETRYABLE_MESSAGES)


def book_venue():
    """执行场地预约"""
    required_keys = ['serviceid', 'stockid', 'stockdetail_id', 'users']
    missing = [key for key in required_keys if not Config.BOOKING_DATA.get(key)]
    if missing:
        raise RuntimeError(f"Config.BOOKING_DATA 缺少字段: {', '.join(missing)}，请先运行 config_setup.setup_config()")

    timeout = getattr(Config, 'REQUEST_TIMEOUT_SECONDS', 10)
    session = get_session()
    book_url = f"{Config.BASE_URL}/cgyd/order/tobook.html"
    serviceid = Config.BOOKING_DATA['serviceid']
    headers = _create_headers(serviceid)
    candidates = _booking_candidates()

    for idx, cand in enumerate(candidates, start=1):
        print(
            f"尝试第 {idx}/{len(candidates)} 个候选: "
            f"日期 {cand.get('date', '未知日期')} / 时间段 {cand.get('time_no')} / 场地 {cand.get('sname')}"
        )

        payload = _build_payload(cand, serviceid)

        for attempt in range(1, MAX_RETRY_PER_CANDIDATE + 1):
            encoded_payload = _encode_payload(payload)

            try:
                response = session.post(book_url, data=encoded_payload, headers=headers, timeout=timeout)
            except requests.RequestException as exc:
                print(f"请求异常：{exc}，重试 ({attempt}/{MAX_RETRY_PER_CANDIDATE})")
                time.sleep(RETRY_SLEEP_SECONDS)
                continue

            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}，重试 ({attempt}/{MAX_RETRY_PER_CANDIDATE})")
                time.sleep(RETRY_SLEEP_SECONDS)
                continue

            try:
                result = response.json()
            except ValueError:
                print("响应不是 JSON，重新尝试获取页面...")
                try:
                    session.get(f"{Config.BASE_URL}/cgyd/product/show.html?id={serviceid}", timeout=timeout)
                except requests.RequestException as exc:
                    print(f"刷新场馆页面失败：{exc}")
                time.sleep(RETRY_SLEEP_SECONDS)
                continue

            if result.get('result') == '1':
                print("预约成功！")
                print(result.get('message', ''))
                return

            message = result.get('message', '')

            if '每日限预约一场' in message:
                print(f"预约失败：{message}，停止尝试其他时段")
                return

            if _is_non_retryable_message(message):
                print(f"其他错误：{message}，不再重试当前候选。")
                break

            print(f"其他错误：{message}，重试 ({attempt}/{MAX_RETRY_PER_CANDIDATE})")
            time.sleep(RETRY_SLEEP_SECONDS)

        print(
            f"候选 {cand.get('date', '未知日期')} / {cand.get('time_no')} / {cand.get('sname')} "
            "尝试完毕，切换到下一个候选。"
        )

    raise RuntimeError("所有候选时段均尝试完毕，未能预约成功。请检查配置或稍后再试。")


if __name__ == '__main__':
    book_venue()
