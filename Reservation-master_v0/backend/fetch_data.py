import json
import os
from typing import Optional

import requests

from config import Config
from login import Login

class FetchData:
    @staticmethod
    def _request_slots(session: requests.Session, date: str, serviceid: str) -> Optional[list]:
        """内部请求 helper，携带必要的 headers 和 cookies。"""
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
            response = session.get(url, params=params, headers=headers, timeout=10)
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

    @staticmethod
    def fetch_service_data(date, serviceid):
        """获取指定日期和 serviceid 的场地信息，默认携带登录态。"""
        session = Login.get_session()
        data = FetchData._request_slots(session, date, serviceid)
        if data:
            return data

        # 若首次失败，尝试刷新页面后再次请求
        session.get(f"{Config.BASE_URL}/cgyd/product/show.html?id={serviceid}")
        return FetchData._request_slots(session, date, serviceid)

    @staticmethod
    def save_data_to_json(data, date, serviceid):
        """保存获取到的数据为 JSON 文件"""
        folder = 'data'
        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = os.path.join(folder, f"service_data_{serviceid}_{date}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"数据保存为 {filename}")

    @staticmethod
    def load_data_from_json(date, serviceid):
        """从指定日期的 JSON 文件加载数据"""
        folder = 'data'
        filename = os.path.join(folder, f"service_data_{serviceid}_{date}.json")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
