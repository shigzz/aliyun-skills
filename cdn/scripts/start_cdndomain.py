# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys
import json

from typing import List

from alibabacloud_cdn20180510.client import Client as Cdn20180510Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cdn20180510 import models as cdn_20180510_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> Cdn20180510Client:
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
        # Endpoint 请参考 https://api.aliyun.com/product/Cdn
        config.endpoint = f'cdn.aliyuncs.com'
        return Cdn20180510Client(config)

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        client = Sample.create_client()
        start_cdn_domain_request = cdn_20180510_models.StartCdnDomainRequest()
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.start_cdn_domain_with_options(start_cdn_domain_request, runtime)
            print(json.dumps(resp, default=str, indent=2))
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
        client = Sample.create_client()
        start_cdn_domain_request = cdn_20180510_models.StartCdnDomainRequest()
        runtime = util_models.RuntimeOptions()
        try:
            resp = await client.start_cdn_domain_with_options_async(start_cdn_domain_request, runtime)
            print(json.dumps(resp, default=str, indent=2))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))


if __name__ == '__main__':
    Sample.main(sys.argv[1:])

