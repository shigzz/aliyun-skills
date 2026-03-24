# -*- coding: utf-8 -*-
"""Create an OSS bucket (PutBucket)."""
from __future__ import annotations

import argparse
import json
import sys

from alibabacloud_oss_v2 import models as oss_models

from oss_util import create_client, print_operation_error, result_to_jsonable


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="创建 OSS 存储空间（PutBucket）")
    parser.add_argument("--bucket", required=True, help="Bucket 名称（小写字母、数字、短划线，3~63 字符）")
    parser.add_argument("--region", default="cn-hangzhou", help="地域 ID")
    parser.add_argument(
        "--acl",
        choices=("private", "public-read", "public-read-write"),
        default=None,
        help="Bucket ACL，默认 private（服务端默认）",
    )
    parser.add_argument("--resource-group-id", default=None, dest="resource_group_id")
    parser.add_argument(
        "--bucket-tagging",
        default=None,
        dest="bucket_tagging",
        help="标签，如 k1=v1&k2=v2",
    )
    args = parser.parse_args(argv)

    client = create_client(args.region)
    req = oss_models.PutBucketRequest(
        bucket=args.bucket,
        acl=args.acl,
        resource_group_id=args.resource_group_id,
        bucket_tagging=args.bucket_tagging,
    )
    try:
        resp = client.put_bucket(req)
        print(json.dumps(result_to_jsonable(resp), ensure_ascii=False, indent=2))
    except Exception as error:  # noqa: BLE001
        print_operation_error(error)
        sys.exit(1)


if __name__ == "__main__":
    main()

