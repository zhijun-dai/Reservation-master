from typing import Optional

import requests

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import _compat

from backend.config import Config
from backend.login import get_session


def _request_slots(session: requests.Session, date: str, serviceid: str) -> Optional[list]:
    """内部请求 helper，携带必要的 headers 和 cookies。"""
    timeout = getattr(Config, 'REQUEST_TIMEOUT_SECONDS', 10)
    url = f"{Config.BASE_URL}/cgyd/product/findOkArea.html"
    params = {
        "s_date": date,
        "serviceid": serviceid
    }
    headers = {
        "Referer": f"{Config.BASE_URL}/cgyd/product/show.html?id={serviceid}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = session.get(url, params=params, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        print(f"请求异常: {exc}")
        return None

    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}")
        return None

    try:
        payload = response.json()
    except ValueError:
        print("响应不是有效的 JSON。")
        return None

    data = payload.get('object') if isinstance(payload, dict) else None
    if not data:
        print("没有获取到数据")
    return data


def fetch_service_data(date, serviceid):
    """获取指定日期和 serviceid 的场地信息，默认携带登录态。"""
    timeout = getattr(Config, 'REQUEST_TIMEOUT_SECONDS', 10)
    session = get_session()
    data = _request_slots(session, date, serviceid)
    if data:
        return data

    # 若首次失败，尝试刷新页面后再次请求
    try:
        session.get(f"{Config.BASE_URL}/cgyd/product/show.html?id={serviceid}", timeout=timeout)
    except requests.RequestException as exc:
        print(f"刷新场馆页面失败: {exc}")
        return None
    return _request_slots(session, date, serviceid)
