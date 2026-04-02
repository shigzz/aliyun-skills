---
name: aliyun-sls-skills
description: >-
  通过 Python（alibabacloud_sls20201230）调用阿里云 SLS：ListProject（列出 Project）、ListLogStores（列出日志库）、GetLogsV2（查询日志）。
  适用于「列出 Project」「列出 LogStore」「查询 SLS 日志」「搜索与分析日志」等场景。
  API 契约见 reference/*.yml；可运行示例见 scripts/；依赖见 scripts/requirements.txt。
---

## 能力概述

## 目录结构

```
aliyun-sls-skills/
├── SKILL.md
├── .env.example
├── reference/                    # API 定义（YML），含入参与返回值
│   ├── list_project.yml
│   ├── list_logstores.yml
│   └── get_log_v2.yml
└── scripts/
    ├── sls_util.py               # 凭证与 Client 构造（供脚本复用）
    ├── list_project.py
    ├── list_logstores.py
    ├── get_logs_v2.py
    └── requirements.txt
```

- **reference/**：存放 API 相关信息（YML 片段），供查阅参数与响应含义。
- **scripts/**：可直接运行的示例（例如在 `aliyun-sls-skills` 目录下执行 `python scripts/list_logstores.py ...`）；也可阅读实现后改写。
- **依赖**：`pip install -r aliyun-sls-skills/scripts/requirements.txt`。

本 skill 提供以下**独立能力**，可按需组合：

| 能力 | API | 用途 | 使用场景 |
|------|-----|------|----------|
| **列出 Project** | ListProject | 列出账号下 SLS Project | 确认 project 名称、分页浏览 |
| **列出日志库** | ListLogStores | 列出 Project 下 LogStore | 确认 logstore 名称、分页浏览 |
| **查询日志** | GetLogsV2 | 按时间范围与查询语句拉取日志 | 检索错误日志、SQL 分析、scan 模式 |

**说明**：

- 若用户不确定 `project` 名称，可先 **ListProject** 查看账号下所有项目。
- 若用户不确定 `logstore` 名称，可先 **ListLogStores** 再 **GetLogsV2**。
- **GetLogsV2** 时间区间为**左闭右开** `[from, to)`，且须满足 `from < to`。
- Python SDK 中请求参数字段名以 `alibabacloud_sls20201230.models` 为准（例如 `GetLogsV2Request` 使用 `from_`、`to`，而非 `from_time` / `to_time`）。

---

# 项目配置文件（`.aliyun-config.json`）

将 SLS 相关的上下文信息保存到**当前工作目录**下的 `.aliyun-config.json`，便于后续操作复用已确认的 region、project、logstore 等配置，避免重复询问。

## 建议字段

```json
{
  "version": 1,
  "sls": {
    "region": "cn-hangzhou",
    "project": "your-project",
    "logstore": "your-logstore",
    "last_query_at": "2026-04-01T12:00:00Z"
  },
  "notes": "可选备注"
}
```

| 字段 | 说明 |
|------|------|
| `version` | 配置文件版本号 |
| `sls.region` | SLS 所在地域（如 `cn-hangzhou`） |
| `sls.project` | Project 名称 |
| `sls.logstore` | 默认 LogStore 名称（可选） |
| `sls.last_query_at` | 上次查询时间（ISO 8601 格式） |

## 读取规则

执行 SLS 操作前，**先检查当前工作目录是否存在 `.aliyun-config.json`**：

```python
import json
import os

config_path = os.path.join(os.getcwd(), ".aliyun-config.json")
sls_config = {}

if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        sls_config = config.get("sls", {})

region = sls_config.get("region")
project = sls_config.get("project")
logstore = sls_config.get("logstore")
```

**配置复用逻辑**：

1. 若 `.aliyun-config.json` 中已存在完整的 `sls.region`、`sls.project`（以及按需的 `sls.logstore`），且与用户本次意图一致，可 **直接复用** 而无需再次询问。
2. 若用户明确要求变更 region、project 或 logstore，须 **重新确认** 并更新配置。
3. 若配置文件不存在或字段缺失，需先通过 **ListProject** / **ListLogStores** 等 API 查询后，**由用户选择或确认** 再写入。

## 写入规则

在以下时机更新 `.aliyun-config.json`：

1. **用户首次确认 region、project、logstore 后**：写入完整配置。
2. **每次成功执行查询后**：更新 `sls.last_query_at`。
3. **用户变更目标资源时**：覆盖对应字段。

```python
import json
import os
from datetime import datetime, timezone

config_path = os.path.join(os.getcwd(), ".aliyun-config.json")

# 读取现有配置（若存在）
config = {}
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

# 更新 sls 部分
config["version"] = config.get("version", 1)
config["sls"] = {
    "region": "cn-hangzhou",
    "project": "your-project",
    "logstore": "your-logstore",
    "last_query_at": datetime.now(timezone.utc).isoformat()
}

# 写入
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
```

## 与其他 skill 共享

`.aliyun-config.json` 可包含多个阿里云产品的配置（如 `oss`、`cdn`、`domain` 等）。**本 skill 仅读写 `sls` 字段**，不得覆盖或删除其他产品的配置段。

```json
{
  "version": 1,
  "sls": { "region": "cn-hangzhou", "project": "..." },
  "oss": { "bucket": "...", "region": "..." },
  "cdn": { "domain": "..." }
}
```

## 安全提示

- **勿在配置文件中存储 AK/SK 等敏感凭证**；凭证应通过环境变量或 `.env` 管理。
- 是否将 `.aliyun-config.json` 提交到版本库，由团队规范决定（建议加入 `.gitignore`）。

---

# 前置检查（必须首先执行）

调用 SLS 前须确认访问凭证已配置。

### 检查顺序

**1. 环境变量**

```bash
echo "AK_ID: ${ALIBABA_CLOUD_ACCESS_KEY_ID:+已设置}"
echo "AK_SECRET: ${ALIBABA_CLOUD_ACCESS_KEY_SECRET:+已设置}"
```

**2. 当前目录 `.env`**

```bash
find . -maxdepth 1 -name ".env" -exec cat {} \;
```

示例见 [.env.example](.env.example)。

**3. Python 中加载（与 scripts 行为一致）**

```python
from dotenv import load_dotenv
import os

access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

if not access_key_id or not access_key_secret:
    load_dotenv()
    access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

if not access_key_id or not access_key_secret:
    raise RuntimeError("缺少 ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET")
```

未通过凭证检查时不应继续调用 API。

---

## 安装依赖

```bash
pip install -r aliyun-sls-skills/scripts/requirements.txt
```

或手动安装（与仓库其他 Tea SDK skill 一致）：

```bash
pip install alibabacloud_sls20201230 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util python-dotenv
```

---

## 创建 SLS Client

`endpoint` 格式为 `{region}.log.aliyuncs.com`。示例脚本通过 [scripts/sls_util.py](scripts/sls_util.py) 的 `create_sls_client(region)` 使用 **显式 AK/SK**（与 [aliyun-domain-skills/scripts/query_domainlist.py](../aliyun-domain-skills/scripts/query_domainlist.py) 相同）。

若需无 AK 链（ECS 角色、OIDC 等），可在自定义代码中改用 `CredentialClient()` 传入 `open_api_models.Config(credential=credential)`，并仍设置 `endpoint`。

```python
from alibabacloud_sls20201230.client import Client as Sls20201230Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models

credential = CredentialClient()
config = open_api_models.Config(credential=credential)
config.endpoint = f"{region}.log.aliyuncs.com"
client = Sls20201230Client(config)
```

---

# ListProject

列出当前账号下符合条件的 **Project** 信息。完整字段见 [reference/list_project.yml](reference/list_project.yml)。

## 常用参数（摘要）

| 概念 | SDK 字段 | 说明 |
|------|----------|------|
| projectName | `project_name` | Project 名称，支持模糊匹配 |
| offset | `offset` | 查询开始行，默认 0 |
| size | `size` | 每页行数，默认 500，最大 500 |
| resourceGroupId | `resource_group_id` | 资源组 ID |
| fetchQuota | `fetch_quota` | 是否获取 Project 配额信息 |

## 核心流程

1. `create_client()` 创建 SLS Client（使用凭据链或显式 AK/SK）
2. 构建 `ListProjectRequest`
3. `client.list_project_with_options(request, headers, runtime)`
4. 使用 `resp.body.to_map()` 得到字典

示例脚本：[scripts/list_project.py](scripts/list_project.py)

### 命令行示例

```bash
cd aliyun-sls-skills
python scripts/list_project.py
```

### 代码示例

```python
from alibabacloud_sls20201230.client import Client as Sls20201230Client
from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
import json

credential = CredentialClient()
config = open_api_models.Config(credential=credential)
config.endpoint = "cn-hangzhou.log.aliyuncs.com"
client = Sls20201230Client(config)

request = sls_models.ListProjectRequest(project_name="test", size=10)
runtime = util_models.RuntimeOptions()
resp = client.list_project_with_options(request, {}, runtime)
print(json.dumps(resp.body.to_map(), default=str, indent=2, ensure_ascii=False))
```

**响应**（body，常见字段）：`total`、`count`、`projects` 等，以实际返回为准。

---

# ListLogStores

列出指定 **project** 下的 LogStore。完整字段见 [reference/list_logstores.yml](reference/list_logstores.yml)。

## 常用参数（摘要）

| 概念 | SDK 字段 | 说明 |
|------|----------|------|
| project | 方法参数 `project` | 必填 |
| logstoreName | `logstore_name` | 模糊匹配过滤 |
| offset / size | `offset` / `size` | 分页，size 最大 500，默认 200 |
| telemetryType | `telemetry_type` | 日志 / Metrics |
| mode | `mode` | `standard` / `query` |

## 核心流程

1. `create_sls_client(region)`
2. 构建 `ListLogStoresRequest`
3. `client.list_log_stores_with_options(project, request, {}, runtime)`
4. 使用 `resp.body.to_map()` 得到字典

示例脚本：[scripts/list_logstores.py](scripts/list_logstores.py)

### 命令行示例

```bash
cd aliyun-sls-skills
python scripts/list_logstores.py --region cn-hangzhou --project your-project
python scripts/list_logstores.py --region cn-hangzhou --project your-project --logstore-name app
```

### 代码示例

```python
from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_tea_util import models as util_models
import json

from sls_util import create_sls_client

client = create_sls_client("cn-hangzhou")
request = sls_models.ListLogStoresRequest(logstore_name="error")
runtime = util_models.RuntimeOptions()
resp = client.list_log_stores_with_options("your-project", request, {}, runtime)
print(json.dumps(resp.body.to_map(), default=str, indent=2, ensure_ascii=False))
```

**响应**（body，常见字段）：`total`、`count`、`logstores` 等，以实际返回为准。

---

# GetLogsV2

在指定 **project**、**logstore** 上按时间范围查询。完整说明见 [reference/get_log_v2.yml](reference/get_log_v2.yml)。

## 常用参数（摘要）

| 概念 | SDK 字段 | 说明 |
|------|----------|------|
| from（Unix 秒） | `from_` | 区间左端（含） |
| to（Unix 秒） | `to` | 区间右端（不含） |
| query | `query` | 搜索或 SQL 分析语句 |
| line / offset | `line` / `offset` | 搜索语句下的分页，line 最大 100 |
| reverse | `reverse` | 是否按时间逆序（搜索语句时） |
| topic | `topic` | 主题 |
| powerSql | `power_sql` | SQL 增强 |
| session | `session` | 如 `mode=scan` |
| Accept-Encoding | `GetLogsV2Headers(accept_encoding=...)` | 如 `lz4`、`gzip` |

> 若 `query` 为分析语句，`line`/`offset` 往往不生效，请用 SQL `LIMIT` 等分页（见官方文档）。

## 核心流程

1. 构建 `GetLogsV2Request(from_=..., to=..., query=..., ...)`
2. `headers = GetLogsV2Headers(accept_encoding="lz4")`（或 `gzip`）
3. `client.get_logs_v2with_options(project, logstore, request, headers, runtime)`
4. `resp.body.to_map()` — 通常含 `meta`、`data`

示例脚本：[scripts/get_logs_v2.py](scripts/get_logs_v2.py)

### 命令行示例

```bash
python scripts/get_logs_v2.py --region cn-hangzhou --project your-project --logstore your-logstore --recent-minutes 15 --query "error"
python scripts/get_logs_v2.py --region cn-hangzhou --project your-project --logstore your-logstore \
  --from-time 1700000000 --to-time 1700003600 --query '* | SELECT count(*) AS cnt'
python scripts/get_logs_v2.py --region cn-hangzhou --project your-project --logstore your-logstore \
  --from-time 1700000000 --to-time 1700003600 --query '*' --session "mode=scan"
```

### 代码示例

```python
import time
from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_tea_util import models as util_models
import json

from sls_util import create_sls_client

client = create_sls_client("cn-hangzhou")
now = int(time.time())
request = sls_models.GetLogsV2Request(
    query="error",
    from_=now - 900,
    to=now,
    line=100,
    offset=0,
    reverse=False,
)
headers = sls_models.GetLogsV2Headers(accept_encoding="lz4")
runtime = util_models.RuntimeOptions()
resp = client.get_logs_v2with_options("your-project", "your-logstore", request, headers, runtime)
print(json.dumps(resp.body.to_map(), default=str, indent=2, ensure_ascii=False))
```

---

## 错误处理

```python
try:
    resp = client.get_logs_v2with_options(project, logstore, request, headers, runtime)
except Exception as error:
    print(getattr(error, "message", str(error)))
    if hasattr(error, "data") and error.data:
        print(error.data.get("Recommend", ""))
```

脚本使用 [scripts/sls_util.py](scripts/sls_util.py) 中的 `print_operation_error` 做同类输出。

| 常见情况 | 说明 |
|----------|------|
| 401/403 | AK/SK 或 RAM 权限不足 |
| ProjectNotExist | Project 名或 region 错误 |
| LogStoreNotExist | 先用 ListLogStores 核对名称 |
| ParameterInvalid | 时间区间、query 语法、offset 等参数不合法 |

---

## 使用流程小结

1. 检查环境变量或 `.env` 中的 AK/SK。
2. 安装 `scripts/requirements.txt`。
3. 检查 `.aliyun-config.json` 是否已有 SLS 配置（region、project、logstore），若存在且与意图一致可直接复用。
4. 若不确定 **project** 名称，先 **ListProject** 查看账号下项目。
5. 确认 **region**、**project**；不确定 logstore 时先 **ListLogStores**。
6. **GetLogsV2** 传入合法时间区间与 `query`，解析 `body` 中 `meta` / `data`。
7. 操作成功后更新 `.aliyun-config.json`，保存本次使用的 region、project、logstore 等信息。

## 注意事项

- **reference/** 用于查契约；**scripts/** 用于验证环境与调用方式。
- 业务与示例不符时，以 [SLS 官方文档](https://help.aliyun.com/zh/sls/) 与当前 SDK 模型为准。

