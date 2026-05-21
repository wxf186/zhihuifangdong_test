# -*- coding: utf-8 -*-
"""
Token 持久化管理
- 登录成功后 token 写入文件
- 运行时优先从文件读取，避免重复登录
- 按环境隔离（test2 / formal）
"""
import os
import json
import base64
import time

# token 文件存放目录
_TOKEN_DIR = os.path.join(os.path.dirname(__file__), "..", "tokens")
os.makedirs(_TOKEN_DIR, exist_ok=True)


def _get_token_file(env: str) -> str:
    """获取指定环境的 token 文件路径"""
    return os.path.join(_TOKEN_DIR, f"{env}.json")


def save_token(token: str, env: str, user_id: str = None) -> None:
    """
    将 token 持久化到文件
    :param token: JWT token 字符串
    :param env: 环境名（test2 / formal）
    :param user_id: 用户ID（可选，用于记录）
    """
    path = _get_token_file(env)
    # 计算过期时间（JWT exp 字段是秒级时间戳）
    try:
        payload = token.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded = json.loads(base64.b64decode(payload))
        exp = decoded.get("exp", 0)
    except Exception:
        exp = 0

    data = {
        "token": token,
        "user_id": user_id,
        "exp": exp,
        "saved_at": time.time(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_token(env: str) -> dict:
    """
    从文件加载 token
    :return: {"token": ..., "user_id": ...} 或 None（无文件或已过期）
    """
    path = _get_token_file(env)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    # 检查是否过期（留 60s 缓冲）
    exp = data.get("exp", 0)
    if exp and time.time() >= exp - 60:
        return None

    return {
        "token": data.get("token"),
        "user_id": data.get("user_id"),
    }


def get_or_login_token(env: str) -> dict:
    """
    优先加载已有 token，失效则重新登录
    :return: {"token": ..., "user_id": ...}
    """
    # 1. 尝试加载
    cached = load_token(env)
    if cached:
        return cached

    # 2. 加载失败，执行登录
    from config.api_config import USERS, API_CONFIG, get_base_url
    from base_tester import api_request

    current_user = USERS[env]
    login_payload = {
        "username": current_user["username"],
        "password": current_user["password"],
    }

    print(f"🔐 文件无有效Token，执行登录... [环境: {env}] {get_base_url()}")

    response = api_request(
        "POST",
        "/auth/auth/apploginMultipleRole",
        need_auth=False,
        data=login_payload,
        timeout=API_CONFIG.get("login_timeout", 10),
    )

    if not (response.get("success") and response.get("data", {}).get("token")):
        raise RuntimeError(f"登录失败: {response.get('message', '未知错误')}")

    token = response["data"]["token"]
    user_id = None
    try:
        payload = token.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        user_id = json.loads(base64.b64decode(payload)).get("id")
    except Exception:
        pass

    # 持久化
    save_token(token, env, user_id)
    print(f"✅ 登录成功，Token已缓存，用户ID: {user_id}")

    return {"token": token, "user_id": user_id}
