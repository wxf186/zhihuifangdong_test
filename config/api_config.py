# -*- coding: utf-8 -*-
"""
API 配置 - 多环境域名 / 请求头 / 连接池 / 超时

用法:
    from config.api_config import set_env, ENVIRONMENTS, ACTIVE_ENV
    set_env("test2")    # 切换到测试环境2（默认）
    set_env("formal")   # 切换到正式环境
"""

# ==================== 多环境配置 ====================
ENVIRONMENTS = {
    # 测试环境2（默认）
    "test2": {
        "base_url": "http://8.153.90.53:7663",
        "headers_template": {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; V2219A Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.74 Mobile Safari/537.36",
            "Host": "8.153.90.53:7663",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json",
            "Language": "zh-CN",
            "Time-Zone": "Asia/Shanghai"
        },
    },
    # 正式环境
    "formal": {
        "base_url": "https://api.zhihuifangdong.net",
        "headers_template": {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; V2219A Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.74 Mobile Safari/537.36",
            "Host": "api.zhihuifangdong.net",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json",
            "Language": "zh-CN",
            "Time-Zone": "Asia/Shanghai"
        },
    },
}

# 当前激活的环境（可由外部修改）
ACTIVE_ENV = "test2"

def set_env(env_name: str):
    """切换激活环境"""
    global ACTIVE_ENV
    if env_name not in ENVIRONMENTS:
        raise ValueError(f"未知环境: {env_name}，可选: {list(ENVIRONMENTS.keys())}")
    ACTIVE_ENV = env_name

def get_base_url() -> str:
    return ENVIRONMENTS[ACTIVE_ENV]["base_url"]

def get_headers_template() -> dict:
    return ENVIRONMENTS[ACTIVE_ENV]["headers_template"]

# ==================== 兼容旧写法（pool_* 和超时参数，base_url 指向当前激活环境） ====================
API_CONFIG = {
    "base_url": ENVIRONMENTS[ACTIVE_ENV]["base_url"],
    "headers_template": ENVIRONMENTS[ACTIVE_ENV]["headers_template"],
    "pool_connections": 10,
    "pool_maxsize": 20,
    "max_retries": 3,
    "default_timeout": 45,
    "login_timeout": 60,
}

# ==================== 账号矩阵 ====================
USERS = {
    "test2": {
        "username": "13182341676",
        "password": "a1234567",
    },
    "formal": {
        "username": "18629604556",
        "password": "a1234567",
    },
}

TEST_USERS = USERS  # 兼容旧名称
