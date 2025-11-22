# utils.py
from config import Config

def generate_payload():
    """
    根据配置文件生成预约的 payload 数据。
    """
    payload = {
        "param": {
            "stockdetail": {Config.BOOKING_DATA['stockid']: Config.BOOKING_DATA['stockdetail_id']},
            "serviceid": Config.BOOKING_DATA['serviceid'],
            "stockid": f"{Config.BOOKING_DATA['stockid']},",
            "remark": "",
            "users": Config.BOOKING_DATA['users']
        },
        "num": 1,
        "json": True
    }
    return payload
