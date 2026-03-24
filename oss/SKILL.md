---
name: aliyun-oss-skill
description: >-
  通过 Python（alibabacloud_oss_v2）操作阿里云 OSS：列举 Bucket（ListBuckets）、创建 Bucket（PutBucket）、设置 Bucket ACL（PutBucketAcl）、上传 Object（PutObject）。
  适用于「列出 OSS Bucket」「创建存储空间」「修改 Bucket 访问权限」「上传文件到 OSS」等场景。
  API 契约见 reference/*.yml；可运行示例见 scripts/；依赖见 scripts/requirements.txt。
---

## 能力概述

## 目录结构

```
aliyun-oss-skills/
├── SKILL.md
├── .env.example
├── reference/                    # API 定义（YML），含入参与返回值说明
│   ├── list_buckets.yml
│   ├── put_bucket.yml
│   ├── put_bucket_acl.yml
│   └── put_object.yml
└── scripts/
    ├── oss_util.py               # 凭证与 Client 构造（供脚本复用）
    ├── list_buckets.py
    ├── put_bucket.py
    ├── put_bucket_acl.py
    ├── put_object.py
    └── requirements.txt
```

- **reference/**：存放 API 相关信息（YML 片段），供查阅参数与响应含义。
- **scripts/**：可直接运行的示例（例如在本 skill 目录下执行 `python scripts/list_buckets.py`）；也可阅读实现后改写。
- **依赖**：`pip install -r aliyun-oss-skills/scripts/requirements.txt`。

本 skill 提供以下**独立能力**，可按需单独或组合使用：

| 能力 | API | 用途 | 使用场景 |
|------|-----|------|----------|
| **列举 Bucket** | ListBuckets（GetService） | 列出当前账号下的存储空间 | 资产盘点、按前缀/标签筛选 Bucket |
| **创建 Bucket** | PutBucket | 在指定地域新建存储空间 | 新环境初始化、自动化开通 |
| **设置 Bucket ACL** | PutBucketAcl | 覆盖式设置 Bucket 访问权限（私有/公共读/公共读写） | 收紧或调整 Bucket 可见性、合规整改 |
| **上传 Object** | PutObject | 上传本地文件为对象 | 部署静态资源、备份文件 |

**说明**：

- 各能力相互独立，无固定调用顺序。
- **PutBucket / PutBucketAcl / PutObject 为写操作**：执行前须确认 Bucket 名称、地域、ACL 取值（`public-read` / `public-read-write` 风险高）、是否覆盖同名对象；避免对生产 Bucket 误操作。
- REST 文档中的 query/header 名称（如 `max-keys`）与 Python SDK 字段名可能不同，**以 `alibabacloud_oss_v2.models` 中 Request 类参数为准**（例如 `max_keys`）。

---

# 前置检查（必须首先执行）

调用 OSS 前须确认访问凭证已配置。

### 检查顺序

**1. 优先检查环境变量**

```bash
echo "AK_ID: ${ALIBABA_CLOUD_ACCESS_KEY_ID:+已设置}"
echo "AK_SECRET: ${ALIBABA_CLOUD_ACCESS_KEY_SECRET:+已设置}"
```

**2. 若未设置，检查当前工作目录的 `.env`**

```bash
find . -maxdepth 1 -name ".env" -exec cat {} \;
```

`.env` 示例见 [.env.example](.env.example)。

**3. 凭证变量约定（优先级）**

- **推荐**：`ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`（与本仓库其他 Alibaba Cloud skill 一致）。临时凭证可额外设置 `ALIBABA_CLOUD_SECURITY_TOKEN`（或 `OSS_SESSION_TOKEN`）。
- **备选**：`OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`（与 OSS Python SDK 官方示例一致）；STS 时可设 `OSS_SESSION_TOKEN`。

脚本逻辑：**若已配置 `ALIBABA_CLOUD_*` 则使用静态凭证；否则使用 `OSS_*` 环境变量凭证提供者**。

**4. Python 中加载（与 scripts 行为一致）**

```python
from dotenv import load_dotenv
import os

access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

if not access_key_id or not access_key_secret:
    load_dotenv()
    access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

# 若仍无 ALIBABA_CLOUD_*，可回退检查 OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET
```

未通过凭证检查时不应继续调用 OSS。

---

## 安装依赖

```bash
pip install -r aliyun-oss-skills/scripts/requirements.txt
```

或手动安装：

```bash
pip install alibabacloud_oss_v2 python-dotenv
```

---

# 列举 Bucket（ListBuckets）

通过 `alibabacloud_oss_v2` 列举当前账号下的 Bucket。SDK 使用 `region` 配置客户端（默认 `cn-hangzhou`）；具体 Endpoint 由 SDK 按地域解析。

## 常用请求参数（摘要）

| 参数（YML / 概念） | SDK 字段（Python） | 说明 |
|-------------------|-------------------|------|
| prefix | `prefix` | 名称前缀过滤 |
| marker | `marker` | 分页起点 |
| max-keys | `max_keys` | 单次最大条数（1~1000） |
| x-oss-resource-group-id | `resource_group_id` | 资源组 |
| tag-key / tag-value | `tag_key` / `tag_value` | 按标签过滤 |
| tagging | `tagging` | 标签列表表达式；与 tag-key/tag-value 互斥 |

完整字段见 [reference/list_buckets.yml](reference/list_buckets.yml)。

## RAM 权限提示

列举 Bucket 需要账号级读权限，例如策略中包含 `oss:ListBuckets`（具体策略以控制台/文档为准）。

## 核心流程

1. 配置凭证（环境变量或 `.env`）
2. `Config(credentials_provider=..., region=...)` + `Client(config)`
3. 构建 `ListBucketsRequest`，设置可选过滤条件
4. 调用 `client.list_buckets(request)`
5. 解析返回的 `ListBucketsResult`（含 `buckets`、`is_truncated`、`next_marker` 等）

示例脚本：[scripts/list_buckets.py](scripts/list_buckets.py)

### 命令行示例

```bash
cd aliyun-oss-skills
python scripts/list_buckets.py --region cn-hangzhou
python scripts/list_buckets.py --prefix myapp- --max-keys 50
```

---

# 创建 Bucket（PutBucket）

在指定 **region** 下创建 Bucket；**bucket** 名称须全局符合 OSS 命名规范（小写字母、数字、短划线，3~63 字符等）。

## 常用请求参数（摘要）

| 参数 | SDK 字段 | 说明 |
|------|----------|------|
| bucket（host） | `bucket` | 必填 |
| x-oss-acl | `acl` | `private` / `public-read` / `public-read-write` |
| x-oss-resource-group-id | `resource_group_id` | 可选 |
| x-oss-bucket-tagging | `bucket_tagging` | 如 `k1=v1&k2=v2` |

完整说明见 [reference/put_bucket.yml](reference/put_bucket.yml)。

## RAM 权限提示

创建 Bucket 需要 `oss:PutBucket` 等写权限；同一账号在同一地域可创建的 Bucket 数量有上限（见官方文档）。

## 核心流程

1. 确认地域与 Bucket 名称
2. 构建 `PutBucketRequest(bucket=..., acl=..., ...)`
3. 调用 `client.put_bucket(request)`

示例脚本：[scripts/put_bucket.py](scripts/put_bucket.py)

### 命令行示例

```bash
python scripts/put_bucket.py --bucket my-unique-bucket-name --region cn-hangzhou
python scripts/put_bucket.py --bucket my-unique-bucket-name --region cn-hangzhou --acl private
```

---

# 设置 Bucket ACL（PutBucketAcl）

对**已存在**的 Bucket **覆盖式**设置访问权限（ACL）。REST 上对应 `PUT /?acl`，请求头 `x-oss-acl`；SDK 使用 `PutBucketAclRequest` 的 `acl` 字段。

## 常用请求参数（摘要）

| 参数 | SDK 字段 | 说明 |
|------|----------|------|
| bucket（host） | `bucket` | 必填，目标 Bucket 名称 |
| x-oss-acl | `acl` | 必填：`private`、`public-read`、`public-read-write`（公共读/写请谨慎） |

完整说明与接口行为见 [reference/put_bucket_acl.yml](reference/put_bucket_acl.yml)。

## 行为与注意

- **覆盖语义**：新 ACL 会覆盖原 ACL，并非合并。
- **权限**：请求者需对 Bucket 拥有写入 ACL 的权限，策略中通常包含 `oss:PutBucketAcl`（以控制台/文档为准）。
- **Bucket 不存在**：契约说明若指定 Bucket 不存在，调用该接口**会新建 Bucket**；生产自动化仍建议先显式 PutBucket 创建，勿依赖该副作用。

## RAM 权限提示

需要目标 Bucket 的 ACL 写权限，例如 `oss:PutBucketAcl`。

## 核心流程

1. 确认 Bucket 所在 `region`、目标 ACL 取值（优先 `private`）
2. `Config` + `Client`（与其它脚本相同地域）
3. 构建 `PutBucketAclRequest(bucket=..., acl=...)`
4. 调用 `client.put_bucket_acl(request)`

示例脚本：[scripts/put_bucket_acl.py](scripts/put_bucket_acl.py)（SDK 生成骨架；运行前请在请求中设置 `bucket` 与 `acl`，或与 [scripts/oss_util.py](scripts/oss_util.py) 的 `create_client` 方式对齐后再调用）。

### 代码示例

```python
from alibabacloud_oss_v2 import models as oss_models

req = oss_models.PutBucketAclRequest(
    bucket="examplebucket",
    acl="private",  # 或 public-read、public-read-write（慎用）
)
resp = client.put_bucket_acl(req)
```

---

# 上传 Object（PutObject）

将**本地文件**上传为指定 Bucket 下的 Object。**默认允许覆盖**同名 Object；可使用 `--forbid-overwrite` 禁止覆盖（版本控制 Bucket 下行为以官方文档为准）。

## 常用请求参数（摘要）

| 参数 | SDK 字段 | 说明 |
|------|----------|------|
| bucket | `bucket` | 必填 |
| key | `key` | Object 完整路径 |
| body | `body` | 二进制内容（脚本从 `--file` 读取） |
| Content-Type | `content_type` | 可选；脚本可按扩展名推测 |
| x-oss-forbid-overwrite | `forbid_overwrite` | 禁止覆盖 |

单文件大小等限制见 [reference/put_object.yml](reference/put_object.yml)。

## RAM 权限提示

需要目标 Bucket 的写权限，例如 `oss:PutObject`。

## 核心流程

1. 确认 Bucket 所在 `region`、目标 `key`
2. 读取本地文件为 `bytes`
3. 构建 `PutObjectRequest(bucket=..., key=..., body=..., content_type=...)`
4. 调用 `client.put_object(request)`

示例脚本：[scripts/put_object.py](scripts/put_object.py)

### 命令行示例

```bash
python scripts/put_object.py --bucket my-bucket --key path/to/object.bin --file ./local.bin --region cn-hangzhou
python scripts/put_object.py --bucket my-bucket --key index.html --file ./index.html --content-type text/html --region cn-hangzhou
```

---

## 错误处理建议

脚本对异常会打印可读信息；若为嵌套错误会尝试 `unwrap` 输出内层 `message`。若异常对象含 OpenAPI 风格 `data` 且带 `Recommend`，会一并打印。

常见情况：

- **403 AccessDenied**：AK/SK 无效、RAM 策略不足或 Resource 不匹配。
- **404 NoSuchBucket**：Bucket 不存在或地域错误。
- **409 BucketAlreadyExists** 等：Bucket 名已被占用或冲突。

OSS Python SDK 异常类型见 `alibabacloud_oss_v2.exceptions`（如 `ServiceError`）。

---

## 使用流程小结

1. 检查环境变量或 `.env`，确认凭证已配置。
2. 安装 `scripts/requirements.txt`。
3. 根据场景选择 ListBuckets / PutBucket / PutBucketAcl / PutObject，对照 YML 与 `models` 中的 Request 字段构造请求。
4. 调用对应 `client` 方法，解析 JSON 输出或 Result 对象。

## 注意事项

- **reference/** 中的 YML 用于查阅契约；**scripts/** 用于验证环境与调用链。
- 业务与示例不符时，以官方 [OSS 开发者文档](https://help.aliyun.com/zh/oss/) 与 SDK 源码为准。
- 列举结果若 `is_truncated` 为 true，需用 `next_marker` 继续请求以翻页。

