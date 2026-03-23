---
name: aliyun-sls-skills
description: >-
  通过 Python 代码调用阿里云 SLS (Simple Log Service) API 查询日志。支持
  ListLogStores（列出日志库）和 GetLogsV2（查询日志）接口。使用场景：用户要求查询
  阿里云 SLS 日志、列出 LogStore、搜索日志内容、分析 SLS 数据时触发此技能。
---

# 阿里云 SLS 日志查询

通过 Python SDK `alibabacloud_sls20201230` 调用阿里云 SLS API，支持 ListLogStores 和 GetLogsV2 两个接口。

## 前置检查（必须首先执行）

在编写任何 SLS 查询代码之前，**必须先检查**阿里云凭证是否已配置。

运行以下命令检查环境变量：

```bash
echo "AK_ID: ${ALIBABA_CLOUD_ACCESS_KEY_ID:+已设置}"
echo "AK_SECRET: ${ALIBABA_CLOUD_ACCESS_KEY_SECRET:+已设置}"
```

如果输出为空，说明未设置。引导用户通过以下任一方式配置：

**方式一：环境变量（推荐）**

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
```

**方式二：项目 .env 文件**

在项目根目录创建 `.env` 文件：

```
ALIBABA_CLOUD_ACCESS_KEY_ID=your-access-key-id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-access-key-secret
```

然后在 Python 代码入口处加载：

```python
from dotenv import load_dotenv
load_dotenv()
```

> 凭证检查未通过时，**不要继续执行后续步骤**，先让用户完成配置。

## 安装依赖

```bash
pip install alibabacloud_sls20201230 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util
```

如果使用 `.env` 方式还需安装：

```bash
pip install python-dotenv
```

## 创建 SLS Client

region 由用户提供（如 `cn-hangzhou`、`cn-shanghai`、`cn-beijing` 等），拼接为 endpoint：

```python
from alibabacloud_sls20201230.client import Client as Sls20201230Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models


def create_sls_client(region: str) -> Sls20201230Client:
    credential = CredentialClient()
    config = open_api_models.Config(credential=credential)
    config.endpoint = f'{region}.log.aliyuncs.com'
    return Sls20201230Client(config)
```

## ListLogStores

列出指定 Project 下的所有 LogStore。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project | str | 是 | SLS Project 名称 |
| logstore_name | str | 否 | 按名称过滤（模糊匹配） |
| offset | int | 否 | 分页偏移量，默认 0 |
| size | int | 否 | 每页返回数量，默认 200，最大 500 |
| telemetry_type | str | 否 | 日志类型（None/Metrics） |
| mode | str | 否 | LogStore 类型（standard/query） |

```python
from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_tea_util import models as util_models
import json


def list_logstores(client, project: str, logstore_name: str = None) -> dict:
    request = sls_models.ListLogStoresRequest()
    if logstore_name:
        request.logstore_name = logstore_name
    runtime = util_models.RuntimeOptions()
    resp = client.list_log_stores_with_options(project, request, {}, runtime)
    return resp.body.to_map()
```

用法：

```python
client = create_sls_client("cn-hangzhou")
result = list_logstores(client, "your-project-name")
print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

# 按名称过滤查询
result = list_logstores(client, "your-project-name", logstore_name="error")
```

**响应结构**：
- `total`: 符合条件的 LogStore 总数
- `count`: 当前返回的行数
- `logstores`: LogStore 名称列表

完整参考代码见 [reference/list_logstores.py](reference/list_logstores.py)。

## GetLogsV2

查询指定 LogStore 中的日志（V2 版本接口，支持更多参数和优化的响应格式）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project | str | 是 | SLS Project 名称 |
| logstore | str | 是 | LogStore 名称 |
| from_time | int | 是 | 起始时间（Unix 时间戳，秒），左闭右开区间 |
| to_time | int | 是 | 结束时间（Unix 时间戳，秒），左闭右开区间 |
| query | str | 否 | SLS 查询语句（支持搜索和 SQL 分析） |
| line | int | 否 | 返回行数，默认 100，最大 100（仅查询语句时有效） |
| offset | int | 否 | 分页偏移量，默认 0（仅查询语句时有效） |
| reverse | bool | 否 | 是否按时间逆序，默认 false（仅查询语句时有效） |
| topic | str | 否 | 日志主题，默认空 |
| powerSql | bool | 否 | 是否开启独享 SQL，默认 false |
| session | str | 否 | 查询参数，如 "mode=scan" |
| isAccurate | bool | 否 | 是否开启纳秒级有序 |

```python
import time
from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_tea_util import models as util_models
import json


def get_logs_v2(client, project: str, logstore: str,
                from_time: int, to_time: int,
                query: str = "", line: int = 100, offset: int = 0,
                reverse: bool = False, topic: str = "",
                power_sql: bool = False) -> dict:
    request = sls_models.GetLogsV2Request(
        query=query,
        from_=from_time,
        to=to_time,
        line=line,
        offset=offset,
        reverse=reverse,
        topic=topic,
        power_sql=power_sql,
    )
    headers = sls_models.GetLogsV2Headers(accept_encoding="lz4")
    runtime = util_models.RuntimeOptions()
    resp = client.get_logs_v2with_options(project, logstore, request, headers, runtime)
    return resp.body.to_map()


def get_recent_logs_v2(client, project: str, logstore: str,
                       query: str = "", minutes: int = 15) -> dict:
    """查询最近 N 分钟的日志（便捷方法）"""
    now = int(time.time())
    return get_logs_v2(client, project, logstore, now - minutes * 60, now, query)
```

用法：

```python
client = create_sls_client("cn-hangzhou")

# 查询最近 15 分钟日志
result = get_recent_logs_v2(client, "your-project", "your-logstore", query="error")
print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

# 指定时间范围查询
result = get_logs_v2(client, "your-project", "your-logstore",
                     from_time=1700000000, to_time=1700003600,
                     query="* | SELECT count(*) as cnt")

# 使用 scan 模式查询大量数据
result = get_logs_v2(client, "your-project", "your-logstore",
                     from_time=1700000000, to_time=1700003600,
                     query="*", session="mode=scan")
```

**响应结构**：
- `meta`: 查询元数据
  - `progress`: 查询完成状态（Complete/Incomplete）
  - `count`: 返回的日志行数
  - `processedRows`: 处理的行数
  - `elapsedMillisecond`: 查询耗时（毫秒）
  - `hasSQL`: 是否为 SQL 查询
  - `keys`: 查询结果中所有的 key
- `data`: 日志数据数组

完整参考代码见 [reference/get_logs_v2.py](reference/get_logs_v2.py)。

## 错误处理

所有 API 调用应使用 try/except 捕获异常：

```python
try:
    resp = client.get_logs_v2with_options(project, logstore, request, headers, runtime)
except Exception as error:
    print(f"错误: {error.message}")
    if hasattr(error, 'data') and error.data:
        print(f"诊断: {error.data.get('Recommend', '')}")
```

| 常见错误 | 原因 | 处理方式 |
|----------|------|----------|
| 401/403 | AK/SK 无效或无权限 | 检查环境变量和 RAM 权限 |
| ProjectNotExist | Project 名称错误 | 确认 Project 名称和 region |
| LogStoreNotExist | LogStore 名称错误 | 先用 ListLogStores 查看可用的 LogStore |
| ParameterInvalid | 请求参数错误 | 检查时间范围和 query 语法 |

## 使用流程

```
1. 检查凭证 → ALIBABA_CLOUD_ACCESS_KEY_ID / SECRET 是否已设置
2. 安装依赖 → pip install 所需包
3. 确认信息 → 向用户确认 region、project 名称
4. 列出 LogStore → 调用 ListLogStores 了解可用的日志库
5. 查询日志 → 调用 GetLogsV2，传入 project、logstore、时间范围和查询条件
```

> 如果用户不确定 project 或 logstore 名称，先执行第 4 步列出所有可用的 LogStore。

