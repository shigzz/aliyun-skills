# -*- coding: utf-8 -*-
"""Upload an object to OSS (PutObject)."""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from pathlib import Path

from alibabacloud_oss_v2 import models as oss_models

from oss_util import create_client, print_operation_error, result_to_jsonable


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="上传文件到 OSS（PutObject）")
    parser.add_argument("--bucket", required=True, help="目标 Bucket 名称")
    parser.add_argument("--key", required=True, help="Object 路径（完整 key）")
    parser.add_argument("--file", required=True, help="本地文件路径")
    parser.add_argument("--region", default="cn-hangzhou", help="Bucket 所在地域 ID")
    parser.add_argument(
        "--content-type",
        default=None,
        help="Content-Type；默认按文件扩展名推测",
    )
    parser.add_argument(
        "--forbid-overwrite",
        action="store_true",
        help="禁止覆盖同名 Object（对应 x-oss-forbid-overwrite）",
    )
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"文件不存在或不是普通文件: {path}", file=sys.stderr)
        sys.exit(1)

    content_type = args.content_type
    if not content_type:
        guessed, _ = mimetypes.guess_type(str(path))
        content_type = guessed or "application/octet-stream"

    client = create_client(args.region)
    with path.open("rb") as f:
        body = f.read()

    req = oss_models.PutObjectRequest(
        bucket=args.bucket,
        key=args.key,
        body=body,
        content_type=content_type,
        forbid_overwrite=args.forbid_overwrite,
    )
    try:
        resp = client.put_object(req)
        print(json.dumps(result_to_jsonable(resp), ensure_ascii=False, indent=2))
    except Exception as error:  # noqa: BLE001
        print_operation_error(error)
        sys.exit(1)


if __name__ == "__main__":
    main()

