# -*- coding: utf-8 -*-
"""Shared OSS script helpers: credentials, client, JSON-friendly result conversion."""
from __future__ import annotations

import datetime
import os
from typing import Any, Dict, Mapping, Optional

from alibabacloud_oss_v2.client import Client
from alibabacloud_oss_v2.config import Config
from alibabacloud_oss_v2.credentials import (
    EnvironmentVariableCredentialsProvider,
    StaticCredentialsProvider,
)
from alibabacloud_oss_v2.types import CredentialsProvider

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore


def load_env() -> None:
    """Load `.env` from the current working directory when AK/SK are not in the environment."""
    if not load_dotenv:
        return
    ak = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    sk = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
    o_ak = os.getenv("OSS_ACCESS_KEY_ID", "").strip()
    o_sk = os.getenv("OSS_ACCESS_KEY_SECRET", "").strip()
    if (ak and sk) or (o_ak and o_sk):
        return
    load_dotenv()


def _session_token() -> Optional[str]:
    for key in (
        "ALIBABA_CLOUD_SECURITY_TOKEN",
        "ALIBABA_CLOUD_SESSION_TOKEN",
        "OSS_SESSION_TOKEN",
    ):
        v = os.getenv(key, "").strip()
        if v:
            return v
    return None


def ensure_credentials() -> None:
    """Require either ALIBABA_CLOUD_* or OSS_* access key pair (after optional .env load)."""
    load_env()
    ak = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    sk = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
    o_ak = os.getenv("OSS_ACCESS_KEY_ID", "").strip()
    o_sk = os.getenv("OSS_ACCESS_KEY_SECRET", "").strip()
    if (ak and sk) or (o_ak and o_sk):
        return
    raise RuntimeError(
        "缺少阿里云 OSS 凭证。请设置其一：\n"
        "  - ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET（推荐，与本仓库其他 skill 一致）\n"
        "  - OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET（与 OSS Python SDK 官方示例一致）\n"
        "也可通过当前工作目录的 .env 文件提供上述变量。"
    )


def credentials_provider() -> CredentialsProvider:
    """Prefer ALIBABA_CLOUD_* + optional STS token; fall back to OSS_* env provider."""
    load_env()
    ak = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    sk = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
    if ak and sk:
        token = _session_token()
        return StaticCredentialsProvider(ak, sk, token)
    return EnvironmentVariableCredentialsProvider()


def create_client(region: str) -> Client:
    ensure_credentials()
    return Client(
        Config(
            credentials_provider=credentials_provider(),
            region=region,
        )
    )


def result_to_jsonable(obj: Any) -> Any:
    """Turn SDK models / lists / dicts into JSON-serializable structures."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, dict):
        return {k: result_to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [result_to_jsonable(x) for x in obj]
    if isinstance(obj, Mapping):
        return {k: result_to_jsonable(v) for k, v in obj.items()}
    if hasattr(obj, "__dict__"):
        out: Dict[str, Any] = {}
        for k, v in obj.__dict__.items():
            if k.startswith("_"):
                continue
            out[k] = result_to_jsonable(v)
        return out
    return str(obj)


def print_operation_error(error: BaseException) -> None:
    """Print a readable error line; include nested ServiceError fields when present."""
    msg = getattr(error, "message", None) or str(error)
    print(msg)
    inner = error
    for _ in range(4):
        unwrap = getattr(inner, "unwrap", None)
        if not callable(unwrap):
            break
        try:
            nxt = unwrap()
        except Exception:  # noqa: BLE001
            break
        if nxt is None or nxt is inner:
            break
        inner = nxt
        m = getattr(inner, "message", None)
        if m:
            print(m)
    data = getattr(error, "data", None)
    if isinstance(data, dict) and data.get("Recommend"):
        print(data["Recommend"])

