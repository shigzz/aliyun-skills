# -*- coding: utf-8 -*-
"""List LogStores under an SLS project (ListLogStores)."""
from __future__ import annotations

import argparse
import json
import sys

from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_tea_util import models as util_models

from sls_util import create_sls_client, print_operation_error


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="列出指定 Project 下的 LogStore（ListLogStores）")
    parser.add_argument("--region", default="cn-hangzhou", help="地域，如 cn-hangzhou")
    parser.add_argument("--project", required=True, help="SLS Project 名称")
    parser.add_argument("--logstore-name", default=None, dest="logstore_name", help="按名称模糊过滤")
    parser.add_argument("--offset", type=int, default=None, help="分页偏移，默认由服务端决定")
    parser.add_argument(
        "--size",
        type=int,
        default=None,
        help="每页条数，最大 500，默认 200",
    )
    parser.add_argument(
        "--telemetry-type",
        default=None,
        dest="telemetry_type",
        help="数据类型：留空为日志，Metrics 为时序指标",
    )
    parser.add_argument(
        "--mode",
        default=None,
        choices=("standard", "query"),
        help="LogStore 类型：standard / query",
    )
    args = parser.parse_args(argv)

    client = create_sls_client(args.region)
    request = sls_models.ListLogStoresRequest(
        logstore_name=args.logstore_name,
        mode=args.mode,
        offset=args.offset,
        size=args.size,
        telemetry_type=args.telemetry_type,
    )
    runtime = util_models.RuntimeOptions()
    try:
        resp = client.list_log_stores_with_options(args.project, request, {}, runtime)
        body_map = resp.body.to_map() if resp.body else {}
        print(json.dumps(body_map, default=str, ensure_ascii=False, indent=2))
    except Exception as error:  # noqa: BLE001
        print_operation_error(error)
        sys.exit(1)


if __name__ == "__main__":
    main()

