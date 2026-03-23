---
name: aliyun-describe-instance-bill
description: 查询阿里云实例级账单（DescribeInstanceBill）。适用于"查询实例账单""查看账单详情""了解消费情况"等场景。
---

# 阿里云实例账单查询

通过 Python SDK `alibabacloud_bssopenapi20171214` 调用阿里云 BSS OpenAPI，查询当前账号下的实例级账单。

## 前置检查（必须首先执行）

执行任何查询前，必须先确认 AK/SK 已配置。

**从当前工作目录的 `.env` 文件读取**：

检查当前工作目录下是否存在 `.env` 文件：

```bash
find . -maxdepth 1 -name ".env" -exec cat {} \;
```

`.env` 文件格式：

```dotenv
ALIBABA_CLOUD_ACCESS_KEY_ID=your-access-key-id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-access-key-secret
```

Python 代码中加载：

```python
from dotenv import load_dotenv
import os

load_dotenv()  # 从当前工作目录的 .env 文件加载

access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
```

**或者通过环境变量**：

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
```

未通过凭证检查时，不应继续执行查询步骤。

## 安装依赖

```bash
pip install alibabacloud_bssopenapi20171214 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util python-dotenv
```

## 请求参数

### 必填参数

| 参数 | 类型 | 说明 |
|------|------|------|
| BillingCycle | string | 账期，格式为 YYYY-MM，仅支持最近 18 个月，如 `2024-03` |

### 可选参数（筛选条件）

| 参数 | 类型 | 说明 |
|------|------|------|
| ProductCode | string | 产品代码，如 `rds`、`ecs` |
| ProductType | string | 产品类型，当 ProductCode 为云市场产品时需指定 |
| SubscriptionType | string | 订阅类型：`Subscription`（预付费）/ `PayAsYouGo`（后付费） |
| IsBillingItem | boolean | 是否按计费项维度拉取，默认 `false` |
| Granularity | string | 账单颗粒度：`MONTHLY`（月）/ `DAILY`（日），选择 DAILY 时需指定 BillingDate |
| BillingDate | string | 账单日期，格式 YYYY-MM-DD，仅 Granularity=DAILY 时必填 |
| IsHideZeroCharge | boolean | 是否隐藏零费用账单，默认 `false` |
| BillOwnerId | integer | 资源归属账号 ID |

### 分页参数（SDK 使用 NextToken 方式）

| 参数 | 类型 | 说明 |
|------|------|------|
| MaxResults | integer | 每页数量，最大 300 |
| NextToken | string | 下一页令牌，首次请求为空，后续使用上一次响应中的 NextToken |

## 响应结构

```python
response.body.data = {
    "NextToken": "xxx",         # 下一页的令牌（如果没有更多数据则不返回）
    "MaxResults": 300,          # 每页数量
    "TotalCount": 100,          # 总记录数
    "BillingCycle": "2024-03",
    "Items": {
        "Item": [...]           # 账单详情列表
    }
}
```

## 分页获取完整数据

**必须实现分页逻辑**，因为单次 API 调用最多返回 300 条记录。

### 分页规则

1. 首次请求：不指定 `NextToken` 或设为空字符串
2. 后续请求：使用上一次响应中 `response.body.data.next_token` 的值
3. 终止条件：响应中 `next_token` 为空或不存在（表示已获取完所有数据）

### 分页获取示例代码

```python
def fetch_all_bills(client, billing_cycle, max_results=300, **filter_kwargs):
    """获取指定账期的所有账单记录（自动分页）"""
    all_items = []
    next_token = None

    while True:
        request = bss_open_api_20171214_models.DescribeInstanceBillRequest(
            billing_cycle=billing_cycle,
            max_results=max_results,
            next_token=next_token,
            **filter_kwargs
        )
        response = client.describe_instance_bill_with_options(request, util_models.RuntimeOptions())

        if not response.body.success or not response.body.data.items.item:
            break

        items = response.body.data.items
        all_items.extend(items)

        # 判断是否还有更多数据
        next_token = getattr(response.body.data, 'next_token', None)
        if not next_token:
            break

    return all_items
```

## DescribeInstanceBill 用法

核心流程：

1. 从环境变量（或当前工作目录的 `.env`）读取 `ALIBABA_CLOUD_ACCESS_KEY_ID` / `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
2. 创建 `BssOpenApi20171214Client`
3. 根据查询条件构建请求参数（包括筛选条件和分页参数）
4. **实现分页逻辑**，循环调用直到获取完整数据
5. 汇总并处理所有账单记录

## 参考实现

`reference/` 目录包含的是 **Agent 参考样例**，不是直接运行的脚本。使用此 skill 的 agent 应参考这些代码的结构和 API 调用方式，生成适合自己上下文的实现。

**Agent 使用方式**：

1. 阅读 `reference/describe_instance_bill.py` 了解 API 调用模式
2. 根据当前项目结构生成相应的实现代码
3. 不要直接复制运行，而是作为参考模板

**核心 API 调用模式**：

```python
from alibabacloud_bssopenapi20171214.client import Client as BssOpenApi20171214Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bssopenapi20171214 import models as bss_open_api_20171214_models

# 1. 创建客户端
config = open_api_models.Config(
    access_key_id=os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID"),
    access_key_secret=os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
)
config.endpoint = 'business.aliyuncs.com'
client = BssOpenApi20171214Client(config)

# 2. 调用 API（单次调用，带分页参数）
request = bss_open_api_20171214_models.DescribeInstanceBillRequest(
    billing_cycle="2024-03",
    max_results=300,
    next_token=None,  # 首次请求设为 None，后续使用响应中的 next_token
    product_code="ecs",  # 可选筛选条件
)
response = client.describe_instance_bill_with_options(request, util_models.RuntimeOptions())
```

## 常见查询场景

### 场景 1：查询某月全部账单

```python
all_items = fetch_all_bills(client, billing_cycle="2024-03", max_results=300)
```

### 场景 2：查询指定产品的账单

```python
all_items = fetch_all_bills(
    client,
    billing_cycle="2024-03",
    max_results=300,
    product_code="rds"
)
```

### 场景 3：查询后付费产品账单

```python
all_items = fetch_all_bills(
    client,
    billing_cycle="2024-03",
    max_results=300,
    subscription_type="PayAsYouGo"
)
```

### 场景 4：按天查询账单

```python
all_items = fetch_all_bills(
    client,
    billing_cycle="2024-03",
    max_results=300,
    granularity="DAILY",
    billing_date="2024-03-15"
)
```

## 错误处理建议

- `401/403`：AK/SK 无效、未配置或 RAM 权限不足
- `InvalidAccessKeyId`：AccessKeyId 错误
- `SignatureDoesNotMatch`：AccessKeySecret 错误或签名不一致
- 若异常包含 `Recommend` 字段，优先按诊断链接排查

## 使用流程

1. 检查当前工作目录的 `.env` 文件或环境变量，确认 AK/SK 已配置
2. 安装依赖
3. 阅读 `reference/describe_instance_bill.py`，理解 API 调用模式
4. 根据查询需求构建请求参数（筛选条件 + 分页参数）
5. **实现分页循环**，获取完整账单数据
6. 汇总并处理所有账单记录

## 注意事项

- `BillingCycle` 参数格式为 `YYYY-MM`（如 `2024-03`），调用时必须提供
- **必须实现分页逻辑**，单次调用最多返回 300 条记录
- 分页使用 `NextToken` 方式：首次请求 `next_token=None`，后续使用响应中的 `next_token` 值
- 分页终止条件：响应中 `next_token` 为空或不存在
- 筛选条件：`product_code`、`subscription_type`、`granularity` 等可有效减少返回数据量
- reference 代码是样例，用于帮助 agent 理解 API 调用方式
- agent 应根据实际需求生成代码，包括错误处理、参数传递等

