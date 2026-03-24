# -*- coding: utf-8 -*-
"""Query logs from an SLS LogStore (GetLogsV2)."""
from __future__ import annotations

import argparse
import json
import sys
import time

from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_tea_util import models as util_models

from sls_util import create_sls_client, print_operation_error


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="查询 LogStore 日志（GetLogsV2）")
    parser.add_argument("--region", default="cn-hangzhou", help="地域，如 cn-hangzhou")
    parser.add_argument("--project", required=True, help="SLS Project 名称")
    parser.add_argument("--logstore", required=True, help="LogStore 名称")
    parser.add_argument(
        "--from-time",
        type=int,
        default=None,
        dest="from_time",
        help="起始时间 Unix 秒时间戳（左闭右开区间左端）",
    )
    parser.add_argument(
        "--to-time",
        type=int,
        default=None,
        dest="to_time",
        help="结束时间 Unix 秒时间戳（左闭右开区间右端，不包含）",
    )
    parser.add_argument(
        "--recent-minutes",
        type=int,
        default=None,
        dest="recent_minutes",
        help="与 from-time/to-time 二选一：查询最近 N 分钟",
    )
    parser.add_argument("--query", default="", help="查询语句，默认空（由服务端语义决定）")
    parser.add_argument("--line", type=int, default=100, help="返回行数上限（搜索语句场景，0~100）")
    parser.add_argument("--offset", type=int, default=0, help="偏移（搜索语句场景）")
    parser.add_argument("--reverse", action="store_true", help="按时间逆序（仅搜索语句时生效）")
    parser.add_argument("--topic", default="", help="日志 topic")
    parser.add_argument("--power-sql", action="store_true", dest="power_sql", help="开启 SQL 增强")
    parser.add_argument("--session", default=None, help='会话参数，如 mode=scan')
    parser.add_argument(
        "--accept-encoding",
        default="lz4",
        dest="accept_encoding",
        help="Accept-Encoding，如 lz4、gzip",
    )
    args = parser.parse_args(argv)

    if args.recent_minutes is not None:
        now = int(time.time())
        from_time = now - args.recent_minutes * 60
        to_time = now
    elif args.from_time is not None and args.to_time is not None:
        from_time = args.from_time
        to_time = args.to_time
    else:
        parser.error("请指定 --recent-minutes，或同时指定 --from-time 与 --to-time")

    if from_time >= to_time:
        parser.error("时间区间无效：需满足 from-time < to-time（左闭右开）")

    client = create_sls_client(args.region)
    request = sls_models.GetLogsV2Request(
        query=args.query or None,
        from_=from_time,
        to=to_time,
        line=args.line,
        offset=args.offset,
        reverse=args.reverse if args.reverse else None,
        topic=args.topic or None,
        power_sql=args.power_sql if args.power_sql else None,
        session=args.session,
    )
    headers = sls_models.GetLogsV2Headers(accept_encoding=args.accept_encoding)
    runtime = util_models.RuntimeOptions()
    try:
        resp = client.get_logs_v2with_options(
            args.project, args.logstore, request, headers, runtime
        )
        body_map = resp.body.to_map() if resp.body else {}
        print(json.dumps(body_map, default=str, ensure_ascii=False, indent=2))
    except Exception as error:  # noqa: BLE001
        print_operation_error(error)
        sys.exit(1)


if __name__ == "__main__":
    main()

