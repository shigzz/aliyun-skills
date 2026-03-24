# -*- coding: utf-8 -*-
"""List OSS buckets (ListBuckets / GetService)."""
from __future__ import annotations

import argparse
import json
import sys

from alibabacloud_oss_v2 import models as oss_models

from oss_util import create_client, print_operation_error, result_to_jsonable


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="列举当前账号下的 OSS Bucket（ListBuckets）")
    parser.add_argument(
        "--region",
        default="cn-hangzhou",
        help="地域 ID，默认 cn-hangzhou（列举为账号级操作，region 用于 SDK 配置）",
    )
    parser.add_argument("--prefix", default=None, help="只返回名称以此前缀开头的 Bucket")
    parser.add_argument("--marker", default=None, help="从该 marker 之后按字母序继续列举")
    parser.add_argument(
        "--max-keys",
        type=int,
        default=None,
        help="单次返回的最大 Bucket 数量（1~1000，以 SDK 为准）",
    )
    parser.add_argument("--resource-group-id", default=None, dest="resource_group_id")
    parser.add_argument("--tag-key", default=None, dest="tag_key")
    parser.add_argument("--tag-value", default=None, dest="tag_value")
    parser.add_argument("--tagging", default=None, help="标签列表，与 tag-key/tag-value 互斥")
    args = parser.parse_args(argv)

    client = create_client(args.region)
    req = oss_models.ListBucketsRequest(
        prefix=args.prefix,
        marker=args.marker,
        max_keys=args.max_keys,
        resource_group_id=args.resource_group_id,
        tag_key=args.tag_key,
        tag_value=args.tag_value,
        tagging=args.tagging,
    )
    try:
        resp = client.list_buckets(req)
        print(json.dumps(result_to_jsonable(resp), ensure_ascii=False, indent=2))
    except Exception as error:  # noqa: BLE001
        print_operation_error(error)
        sys.exit(1)


if __name__ == "__main__":
    main()

