# login.py
import requests

try:
    from .config import Config
except ImportError:
    # 兼容直接在 backend 目录下运行脚本
    from config import Config


class Login:
    @staticmethod
    def get_session(username: str | None = None, password: str | None = None):
        """获取已认证的会话，使用提供的或默认的凭据"""
        timeout = getattr(Config, 'REQUEST_TIMEOUT_SECONDS', 10)
        login_url = f"{Config.BASE_URL}/cgyd/login.html"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # 优先使用显式提供的凭据，否则使用配置中的默认值
        login_data = Config.LOGIN_DATA.copy()
        if username:
            login_data['dlm'] = str(username)
        if password:
            login_data['mm'] = str(password)

        session = requests.Session()
        response = session.post(login_url, data=login_data, headers=headers, timeout=timeout)

        if response.status_code != 200:
            raise RuntimeError("登录接口返回异常状态码")

        # 访问任意场馆页面以确保后续请求具备必要的 cookies
        show_url = f"{Config.BASE_URL}/cgyd/product/show.html?id={Config.SERVICE_ID}"
        session.get(show_url, timeout=timeout)
        return session


if __name__ == '__main__':
    session = Login.get_session()
    print(f"Session: {session.cookies}")
