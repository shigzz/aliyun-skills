# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys
import json

from typing import List

from alibabacloud_domain20180129.client import Client as Domain20180129Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_domain20180129 import models as domain_20180129_models
from alibabacloud_tea_util import models as util_models


class Sample:
    @staticmethod
    def create_client() -> Domain20180129Client:
        """
        使用凭据初始化账号Client
        @return: Client
        @throws Exception
        """
        # 工程代码建议使用更安全的无AK方式，凭据配置方式请参见：https://help.aliyun.com/document_detail/378659.html。
        credential = CredentialClient()
        config = open_api_models.Config(
            credential=credential
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Domain
        config.endpoint = f'domain.aliyuncs.com'
        return Domain20180129Client(config)

    @staticmethod
    def ensure_credentials() -> None:
        """检查阿里云凭证是否已配置"""
        access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
        access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

        if not access_key_id or not access_key_secret:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
                access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()
            except ImportError:
                pass

        if not access_key_id or not access_key_secret:
            raise RuntimeError(
                "缺少阿里云凭证。请先设置 ALIBABA_CLOUD_ACCESS_KEY_ID 和 "
                "ALIBABA_CLOUD_ACCESS_KEY_SECRET（可通过环境变量或当前工作目录的 .env 文件提供）。"
            )

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        Sample.ensure_credentials()
        client = Sample.create_client()

        # 从命令行参数读取域名，如果未提供则提示
        if len(args) < 1:
            print("用法: python check_domain.py <domain_name>")
            print("示例: python check_domain.py example.com")
            return

        domain_name = args[0]
        check_domain_request = domain_20180129_models.CheckDomainRequest(
            domain_name=domain_name
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.check_domain_with_options(check_domain_request, runtime)
            print(json.dumps(resp, default=str, indent=2, ensure_ascii=False))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        Sample.ensure_credentials()
        client = Sample.create_client()

        # 从命令行参数读取域名，如果未提供则提示
        if len(args) < 1:
            print("用法: python check_domain.py <domain_name>")
            print("示例: python check_domain.py example.com")
            return

        domain_name = args[0]
        check_domain_request = domain_20180129_models.CheckDomainRequest(
            domain_name=domain_name
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = await client.check_domain_with_options_async(check_domain_request, runtime)
            print(json.dumps(resp, default=str, indent=2, ensure_ascii=False))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))


if __name__ == '__main__':
    Sample.main(sys.argv[1:])

