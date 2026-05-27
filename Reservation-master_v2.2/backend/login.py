# login.py
import requests

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import _compat

from backend.config import Config


def get_session(username: str | None = None, password: str | None = None):
    """获取已认证的会话，使用提供的或默认的凭据"""
    timeout = getattr(Config, 'REQUEST_TIMEOUT_SECONDS', 10)
    login_url = f"{Config.BASE_URL}/cgyd/login.html"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    login_data = Config.LOGIN_DATA.copy()
    if username:
        login_data['dlm'] = str(username)
    if password:
        login_data['mm'] = str(password)

    session = requests.Session()
    response = session.post(login_url, data=login_data, headers=headers, timeout=timeout)

    if response.status_code != 200:
        raise RuntimeError("登录接口返回异常状态码")

    show_url = f"{Config.BASE_URL}/cgyd/product/show.html?id={Config.SERVICE_ID}"
    session.get(show_url, timeout=timeout)
    return session


if __name__ == '__main__':
    session = get_session()
    print(f"Session: {session.cookies}")
