import requests
import json

# 定义要请求的 URL
url = "http://order.njmu.edu.cn:8088/cgyd/product/findOkArea.html"

# 定义请求参数，指定日期和场馆类型（serviceid: 42，表示特定的场馆）
params = {
    "s_date": "2024-09-25",  # 日期参数
    "serviceid": "42"  # 场馆类型
}

# 发送 GET 请求到指定 URL，传递参数
response = requests.get(url, params=params)

# 检查请求是否成功
if response.status_code == 200:
    # 如果响应成功，将响应内容转换为 JSON 格式
    data = response.json().get('object')
    # 遍历返回的每个场地，提取关键信息
    for item in data:
        # 提取场地 ID、名称、状态和时间段等信息
        venue_id = item.get("id")
        venue_name = item.get("sname", "N/A")  # 场地名称
        status = item.get("status", "N/A")  # 场地状态 (1 表示可预约)
        stockid = item.get("stockid", "N/A")
        stock = item.get("stock", {})
        date = stock.get("s_date", "N/A")  # 预约日期
        time_no = stock.get("time_no", "N/A")  # 时间段
        price = stock.get("price", "N/A")  # 价格

        # 输出重要的场地信息
        print(
            f"场地ID: {venue_id}, 场地名称: {venue_name}, 状态: {status}, 日期: {date}, 时间段: {time_no}, 价格: {price}, stockid: {stockid}")
else:
    print(f"请求失败，状态码: {response.status_code}")

