# login.py
import requests
from config import Config


class Login:

    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
        self.login_data = {
            'dlm': str(self.username),
            'mm': str(self.password),
            'yzm': '1',
            'logintype': 'sno',
            'continueurl': '',
            'openid': ''
        }

    @staticmethod
    def get_session(username: str | None = None, password: str | None = None):
        """Obtain an authenticated session using either provided or default credentials."""
        login_url = f"{Config.BASE_URL}/cgyd/login.html"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Prefer explicit credentials; fallback to the defaults in Config.
        login_data = Config.LOGIN_DATA.copy()
        if username:
            login_data['dlm'] = str(username)
        if password:
            login_data['mm'] = str(password)

        session = requests.Session()
        response = session.post(login_url, data=login_data, headers=headers)

        if response.status_code != 200:
            raise RuntimeError("登录接口返回异常状态码")

        # 访问任意场馆页面以确保后续请求具备必要的 cookies。
        show_url = f"{Config.BASE_URL}/cgyd/product/show.html?id=22"
        session.get(show_url)
        return session

    def pre_login(self):
        login_url = f"{Config.BASE_URL}/cgyd/login.html"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # 发送登录请求
        session = requests.Session()
        response = session.post(login_url, data=self.login_data, headers=headers)
        if response.status_code == 200:
            print("登录成功，获取 session")
            url = 'http://order.njmu.edu.cn:8088/cgyd/product/show.html?id=22'
            session.get(url)
            return session
        else:
            raise Exception("登录失败")


if __name__ == '__main__':
    session = Login.get_session()
    print(f"Session: {session.cookies}")
