# -*- coding: utf-8 -*-
# SDK 安装信息请参见文档：https://help.aliyun.com/zh/oss/developer-reference/2-0-manual-preview-version
from __future__ import annotations

import sys

from typing import List

from alibabacloud_oss_v2 import models as oss_models
from alibabacloud_oss_v2.client import Client
from alibabacloud_oss_v2.config import Config
from alibabacloud_oss_v2.credentials import EnvironmentVariableCredentialsProvider



class Sample:

    def __init__(self):
        pass

    @staticmethod
    def put_bucket_acl() -> None:
        # 建议使用环境变量的方式创建凭证，请确保代码运行环境设置了环境变量 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET
        credentials_provider = EnvironmentVariableCredentialsProvider()
        config = Config(
            credentials_provider = credentials_provider,
            region = 'cn-hangzhou'
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Oss
        # config.endpoint = `oss-cn-hangzhou.aliyuncs.com`;
        client = Client(config)
        put_bucket_acl_request = oss_models.PutBucketAclRequest()
        resp = client.put_bucket_acl(put_bucket_acl_request)
        print(vars(resp))

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        Sample.put_bucket_acl()

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        Sample.put_bucket_acl()


if __name__ == '__main__':
    Sample.main(sys.argv[1:])

