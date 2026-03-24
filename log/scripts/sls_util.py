# -*- coding: utf-8 -*-
"""Shared SLS script helpers: credentials and Client construction."""
from __future__ import annotations

import os

from alibabacloud_sls20201230.client import Client as Sls20201230Client
from alibabacloud_tea_openapi import models as open_api_models

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore


def load_env() -> None:
    if not load_dotenv:
        return
    ak = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    sk = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
    if ak and sk:
        return
    load_dotenv()


def ensure_credentials() -> None:
    load_env()
    access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
    if not access_key_id or not access_key_secret:
        raise RuntimeError(
            "缺少阿里云凭证。请先设置 ALIBABA_CLOUD_ACCESS_KEY_ID 和 "
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET（可通过环境变量或当前工作目录的 .env 文件提供）。"
        )


def create_sls_client(region: str) -> Sls20201230Client:
    """
    使用 AK/SK 创建 SLS Client（与 aliyun-domain-skills 脚本一致）。
    也可在自定义代码中改用 CredentialClient() 以支持更多凭据链。
    """
    ensure_credentials()
    access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
    )
    config.endpoint = f"{region}.log.aliyuncs.com"
    return Sls20201230Client(config)


def print_operation_error(error: BaseException) -> None:
    msg = getattr(error, "message", None) or str(error)
    print(msg)
    data = getattr(error, "data", None)
    if isinstance(data, dict) and data.get("Recommend"):
        print(data["Recommend"])

