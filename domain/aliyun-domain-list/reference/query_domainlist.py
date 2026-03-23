# -*- coding: utf-8 -*-
# Reference script for Domain QueryDomainList.
import os
import sys
import json

from typing import List

from alibabacloud_domain20180129.client import Client as Domain20180129Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_domain20180129 import models as domain_20180129_models
from alibabacloud_tea_util import models as util_models

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> Domain20180129Client:
        """
        使用凭据初始化账号Client
        @return: Client
        @throws Exception
        """
        access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
        access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Domain
        config.endpoint = f'domain.aliyuncs.com'
        return Domain20180129Client(config)

    @staticmethod
    def load_env() -> None:
        """从当前工作目录的 .env 文件加载环境变量（仅在环境变量未设置时）"""
        if load_dotenv:
            # 检查是否已设置环境变量
            access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
            access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

            # 如果环境变量未设置，尝试从 .env 文件加载
            if not access_key_id or not access_key_secret:
                load_dotenv()

    @staticmethod
    def ensure_credentials() -> None:
        """检查阿里云凭证是否已配置（优先使用环境变量，其次 .env 文件）"""
        # 先从环境变量读取
        access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
        access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

        # 如果环境变量未设置，尝试从 .env 文件加载
        if not access_key_id or not access_key_secret:
            Sample.load_env()
            access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
            access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

        # 最终检查
        if not access_key_id or not access_key_secret:
            raise RuntimeError(
                "缺少阿里云凭证。请先设置 ALIBABA_CLOUD_ACCESS_KEY_ID 和 "
                "ALIBABA_CLOUD_ACCESS_KEY_SECRET（可通过环境变量或当前工作目录的 .env 文件提供）。"
            )

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        Sample.load_env()
        Sample.ensure_credentials()
        client = Sample.create_client()
        query_domain_list_request = domain_20180129_models.QueryDomainListRequest(
            page_num=1,
            page_size=20
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.query_domain_list_with_options(query_domain_list_request, runtime)
            print(json.dumps(resp, default=str, indent=2, ensure_ascii=False))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(getattr(error, "message", str(error)))
            # 诊断地址
            if hasattr(error, "data") and error.data:
                print(error.data.get("Recommend"))

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        Sample.load_env()
        Sample.ensure_credentials()
        client = Sample.create_client()
        query_domain_list_request = domain_20180129_models.QueryDomainListRequest(
            page_num=1,
            page_size=20
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = await client.query_domain_list_with_options_async(query_domain_list_request, runtime)
            print(json.dumps(resp, default=str, indent=2, ensure_ascii=False))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(getattr(error, "message", str(error)))
            # 诊断地址
            if hasattr(error, "data") and error.data:
                print(error.data.get("Recommend"))


if __name__ == '__main__':
    Sample.main(sys.argv[1:])

