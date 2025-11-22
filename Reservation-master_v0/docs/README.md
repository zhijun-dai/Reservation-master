# 南京医科大学场馆自动预约脚本文档

本文档聚焦于最新的脚本化预约流程，涵盖环境准备、核心模块说明以及常见问题。旧版 FastAPI 服务、数据库模型与 CLI 工具已下线。

## 文档目录

- [系统概述](overview.md)
- [安装与配置](installation.md)
- [运行架构](architecture.md)
- [模块说明](modules.md)
- [脚本使用指南](usage.md)
- [常见问题](faq.md)

## 快速上手

```powershell
cd ../backend
python -m venv ..\.venv
..\.venv\Scripts\activate
pip install -r requirements.txt
python config_setup.py
python scheduler.py
```

## 支持

如果遇到脚本使用问题，可先查阅 [常见问题](faq.md)。如需进一步帮助，请联系维护者。 