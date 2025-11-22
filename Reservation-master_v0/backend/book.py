# book.py
import json
import time

import requests
from urllib.parse import urlencode
from config import Config
from login import Login

BASE_URL = 'http://order.njmu.edu.cn:8088'

class Booking:
    def __init__(self, stockid='', serviceid='', id='', users='', username='', password=''):
        self.stockid = stockid
        self.serviceid = serviceid
        self.id = id
        self.users = users
        self.username = username
        self.password = password
        if username and password:
            login = Login(username, password)
            self.session = login.pre_login()
            self.book_url = f"{BASE_URL}/cgyd/order/tobook.html"
            self.payload = {
                "param": {
                    "stockdetail": {str(self.stockid): str(self.id)},
                    "serviceid": self.serviceid,
                    "stockid": f"{self.stockid},",
                    "remark": "",
                    "users": self.users
                },
                "num": 1,
                "json": True
            }

            # 将 payload 字典转换为 URL 编码的字符串
            self.encoded_payload = urlencode({
                "param": json.dumps(self.payload["param"]),
                "num": self.payload["num"],
                "json": self.payload["json"]
            })

            self.headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{BASE_URL}/cgyd/product/show.html?id={self.serviceid}"
            }

    def pre_book(self):
        max_attempts = 50
        for attempt in range(max_attempts):
            response = self.session.post(self.book_url, data=self.encoded_payload, headers=self.headers)
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}，重试 ({attempt + 1}/{max_attempts})")
                time.sleep(0.5)
                continue

            try:
                result = response.json()
            except ValueError:
                print("响应解析失败，尝试刷新会话后重试。")
                self.session.get(f"{Config.BASE_URL}/cgyd/product/show.html?id={self.serviceid}")
                time.sleep(0.5)
                continue

            message = result.get('message', '')
            if result.get('result') == '1':
                print("预约成功！")
                print(message)
                return result

            if '未到该日期的预订时间' in message:
                print(f"预约失败：{message}，等待后继续尝试 ({attempt + 1}/{max_attempts})")
                time.sleep(0.5)
                continue

            if '每日限预约一场' in message:
                print(f"预约失败：{message}")
                return result

            print(f"其他错误：{message}，重试 ({attempt + 1}/{max_attempts})")
            time.sleep(0.5)

        raise RuntimeError("多次尝试预约仍未成功。")


    @staticmethod
    def book_venue():
        required_keys = ['serviceid', 'stockid', 'stockdetail_id', 'users']
        missing = [key for key in required_keys if not Config.BOOKING_DATA.get(key)]
        if missing:
            raise RuntimeError(f"Config.BOOKING_DATA 缺少字段: {', '.join(missing)}，请先运行 config_setup.setup_config()")

        session = Login.get_session()
        book_url = f"{Config.BASE_URL}/cgyd/order/tobook.html"
        payload_template = {
            "param": {
                "stockdetail": {str(Config.BOOKING_DATA['stockid']): str(Config.BOOKING_DATA['stockdetail_id'])},
                "serviceid": Config.BOOKING_DATA['serviceid'],
                "stockid": f"{Config.BOOKING_DATA['stockid']},",
                "remark": "",
                "users": Config.BOOKING_DATA['users']
            },
            "num": 1,
            "json": True
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{Config.BASE_URL}/cgyd/product/show.html?id={Config.BOOKING_DATA['serviceid']}"
        }

        # 如果 setup_config 提供了多个候选时段，则依次尝试每个候选
        candidates = Config.BOOKING_DATA.get('slot_candidates')
        if not candidates:
            # 回退到旧的 payload_template 行为
            candidates = [{
                'time_no': Config.BOOKING_DATA.get('time_slot', ''),
                'stockid': Config.BOOKING_DATA.get('stockid', ''),
                'stockdetail_id': Config.BOOKING_DATA.get('stockdetail_id', ''),
                'sname': Config.BOOKING_DATA.get('sname', '')
            }]

        retryable_messages = (
            '未到该日期的预订时间',
            '系统繁忙',
            '请稍后重试'
        )
        non_retryable_messages = (
            '已过有效期',
            '该场地已被预约',
            '预约时间已过',
            '超出可预约时间段'
        )

        for idx, cand in enumerate(candidates, start=1):
            print(
                f"尝试第 {idx}/{len(candidates)} 个候选: "
                f"日期 {cand.get('date', '未知日期')} / 时间段 {cand.get('time_no')} / 场地 {cand.get('sname')}"
            )
            # 构建每个候选的 payload
            payload_template['param'] = {
                "stockdetail": {str(cand.get('stockid', '')): str(cand.get('stockdetail_id', ''))},
                "serviceid": Config.BOOKING_DATA['serviceid'],
                "stockid": f"{cand.get('stockid', '')},",
                "remark": "",
                "users": Config.BOOKING_DATA['users']
            }

            for attempt in range(1, 6):
                encoded_payload = urlencode({
                    "param": json.dumps(payload_template["param"]),
                    "num": payload_template["num"],
                    "json": payload_template["json"]
                })

                response = session.post(book_url, data=encoded_payload, headers=headers)
                if response.status_code != 200:
                    print(f"请求失败，状态码: {response.status_code}，重试 ({attempt}/5)")
                    time.sleep(1)
                    continue

                try:
                    result = response.json()
                except ValueError:
                    print("响应不是 JSON，重新尝试获取页面...")
                    session.get(f"{Config.BASE_URL}/cgyd/product/show.html?id={Config.BOOKING_DATA['serviceid']}")
                    time.sleep(1)
                    continue

                if result.get('result') == '1':
                    print("预约成功！")
                    print(result.get('message', ''))
                    return

                message = result.get('message', '')
                if '未到该日期的预订时间' in message:
                    print(f"预约失败：{message}，将在当前会话内继续尝试 ({attempt}/5)")
                    time.sleep(1)
                    continue

                if '每日限预约一场' in message:
                    print(f"预约失败：{message}，停止尝试其他时段")
                    return

                retryable = any(key in message for key in retryable_messages)
                non_retryable = any(key in message for key in non_retryable_messages)

                if retryable:
                    print(f"其他错误：{message}，重试 ({attempt}/5)")
                    time.sleep(1)
                    continue

                print(f"其他错误：{message}，不再重试当前候选。")
                break

            print(
                f"候选 {cand.get('date', '未知日期')} / {cand.get('time_no')} / {cand.get('sname')} "
                "尝试完毕，切换到下一个候选。"
            )

        raise RuntimeError("所有候选时段均尝试完毕，未能预约成功。请检查配置或稍后再试。")

if __name__ == '__main__':
    Booking.book_venue()
