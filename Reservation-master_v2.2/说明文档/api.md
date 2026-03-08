# 接口说明

当前版本不再对外提供 FastAPI 服务，本仓库的脚本直接与南京医科大学官方预约系统交互。本文记录脚本所使用的关键接口，便于排查或抓包分析。

## 1. 登录接口

- **URL**：`http://order.njmu.edu.cn:8088/cgyd/login.html`
- **方法**：`POST`
- **用途**：提交 `LOGIN_DATA` 中的学号和密码，获取认证 Cookie。
- **注意**：脚本随后会访问一次 `show.html` 以补齐后续请求所需的 Cookie。

示例载荷：

```
dlm=<学号>&mm=<密码>&yzm=1&logintype=sno&continueurl=&openid=
```

## 2. 场地查询接口

- **URL**：`http://order.njmu.edu.cn:8088/cgyd/product/findOkArea.html`
- **方法**：`GET`
- **主要参数**：
  - `s_date`：查询日期，格式 `YYYY-MM-DD`
  - `serviceid`：场馆类型（羽毛球馆为 `22`）
- **请求头**：
  - `Referer`：`http://order.njmu.edu.cn:8088/cgyd/product/show.html?id=<serviceid>`
  - `X-Requested-With: XMLHttpRequest`
- **响应**：JSON，对象中 `object` 字段为可用场地列表。

示例响应片段：

```json
{
  "result": "1",
  "object": [
    {
      "id": 299748,
      "sname": "场地4",
      "stockid": 20239,
      "stock": {
        "time_no": "20:01-21:00"
      }
    }
  ]
}
```

## 3. 预约提交接口

- **URL**：`http://order.njmu.edu.cn:8088/cgyd/order/tobook.html`
- **方法**：`POST`
- **请求体**：`application/x-www-form-urlencoded`

脚本使用的字段：

- `param`：JSON 字符串，核心内容包括
  - `stockdetail`：形如 `{stockid: stockdetail_id}`
  - `serviceid`：场馆服务 ID
  - `stockid`：库存 ID（以逗号结尾）
  - `users`：入场人员学号，多个学号使用 `/` 分隔
- `num`：固定 `1`
- `json`：布尔值 `true`

常见响应：

```json
{"result":"1","message":"预订成功"}
{"result":"0","message":"未到该日期的预订时间"}
{"result":"0","message":"每日限预约一场"}
```

## 4. 缓存位置

- 场地数据缓存：`backend/data/service_data_{serviceid}_{date}.json`
- 缓存内容即接口 `object` 的原始数据，便于离线查看。

## 5. 调试建议

- 如需抓包分析，可在浏览器登录后使用开发者工具观察与脚本一致的接口。
- 若想替换请求头，可修改 `fetch_data.py` 与 `book.py` 中的 `headers` 定义。
- 如果接口返回 `result=0` 且 `object` 为空，通常表示尚未放号或没有符合条件的场地。

## 6. 与旧版本的区别

- 不再暴露 `/api/v1/*` 这类自建接口；所有调用均指向学校官方域名。
- 旧文档中涉及的 FastAPI 端点、数据库调试接口均已下线。
- 若需恢复对外 API，请自行重新部署 FastAPI + 数据库 模块。

掌握以上信息即可理解脚本和官方系统之间的通信细节。 
