#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pytest 配置：测试前初始化 token
"""
import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base_tester
from config.token_manager import get_or_login_token
import config.api_config as api_config

def pytest_configure(config):
    """所有测试运行前执行一次：获取token并设置"""
    token_info = get_or_login_token(api_config.ACTIVE_ENV)
    base_tester.set_token(token_info["token"])
