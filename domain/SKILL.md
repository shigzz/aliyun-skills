---
name: aliyun-domain-skill
description: >-
  通过 Python 代码调用阿里云 Domain OpenAPI 查询域名列表（QueryDomainList）和检查域名是否可注册（CheckDomain）。
  适用于"查询阿里云域名列表""列出账号下域名""检查域名资产""检查域名是否可注册"等场景。
  API 入参与返回值见 reference/ 下 YML；可运行示例见 scripts/；初次使用需安装 scripts/requirements.txt 中的依赖。
---

## 能力概述

## 目录结构

```
aliyun-domain-skills/
├── SKILL.md
├── reference/                    # API 定义（YML），含入参与返回值
│   ├── check_domain.yml
│   └── query_domainlist.yml
└── scripts/                      # 可执行脚本与依赖清单
    ├── check_domain.py
    ├── query_domainlist.py
    └── requirements.txt
```

- **reference/**：存放 API 相关信息，包括入参、返回值等（YML），供查阅契约与字段含义。
- **scripts/**：可直接运行的 Python 脚本（例如 `python scripts/query_domainlist.py`）；也可阅读其实现，在此基础上编写或改写新代码。
- **依赖**：`requirements.txt` 位于 `scripts/` 目录；初次使用请先执行 `pip install -r aliyun-domain-skills/scripts/requirements.txt` 安装依赖。

本 skill 提供以下**独立能力**，可根据实际需求单独调用或组合使用：

| 能力 | API | 用途 | 使用场景 |
|------|-----|------|----------|
| **查询域名列表** | QueryDomainList | 查询账号下的域名列表 | 列出账号域名、检查域名资产、筛选即将到期的域名 |
| **检查域名可注册性** | CheckDomain | 检查域名是否可注册及价格 | 域名注册前检查、批量域名可用性评估 |

**重要说明**：
- 每个能力都是**完全独立**的 API，不存在调用顺序或依赖关系
- 可以只调用其中一个能力，也可以根据需求组合调用多个能力
- 例如：
  - 只需查询账号域名？→ 调用 QueryDomainList
  - 只需检查某个域名能否注册？→ 调用 CheckDomain
  - 需要先查账号域名，再检查其中某些域名的续费价格？→ 先调用 QueryDomainList，再对选中的域名调用 CheckDomain（fee_command=renew）

---

# 查询域名列表（QueryDomainList）

通过 Python SDK `alibabacloud_domain20180129` 调用阿里云 Domain OpenAPI，查询当前账号下的域名列表。

## 前置检查（必须首先执行）

执行任何查询前，必须先确认 AK/SK 已配置。

### 检查顺序

**1. 优先检查环境变量**

```bash
echo "AK_ID: ${ALIBABA_CLOUD_ACCESS_KEY_ID:+已设置}"
echo "AK_SECRET: ${ALIBABA_CLOUD_ACCESS_KEY_SECRET:+已设置}"
```

**2. 如果未设置，检查当前工作目录的 `.env` 文件**

```bash
find . -maxdepth 1 -name ".env" -exec cat {} \;
```

`.env` 文件格式：

```dotenv
ALIBABA_CLOUD_ACCESS_KEY_ID=your-access-key-id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-access-key-secret
```

**3. Python 代码中加载凭证**

```python
from dotenv import load_dotenv
import os

# 先尝试从环境变量读取
access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

# 如果未设置，尝试从 .env 文件加载
if not access_key_id or not access_key_secret:
    load_dotenv()  # 从当前工作目录的 .env 文件加载
    access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

if not access_key_id or not access_key_secret:
    raise RuntimeError("缺少阿里云凭证。请先设置 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET")
```

未通过凭证检查时，不应继续执行查询步骤。

## 安装依赖

```bash
pip install -r aliyun-domain-skills/scripts/requirements.txt
```

或手动安装：

```bash
pip install alibabacloud_domain20180129 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util python-dotenv
```

## QueryDomainList 用法

### 请求参数

#### 必填参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| PageNum | integer | 分页页码 | 1 |
| PageSize | integer | 每页大小 | 10 |

#### 可选参数（筛选条件）

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| DomainName | string | 域名，可在域名列表中搜索 | test.com |
| StartExpirationDate | integer (int64) | 域名到期日期的开始时间（UTC 1970年1月1日0点距离查询时间的毫秒数） | 1522080000000 |
| EndExpirationDate | integer (int64) | 域名到期日期的结束时间（毫秒时间戳） | 1522080000000 |
| StartRegistrationDate | integer (int64) | 域名注册日期的开始时间（毫秒时间戳） | 1522080000000 |
| EndRegistrationDate | integer (int64) | 域名注册日期的结束时间（毫秒时间戳） | 1522080000000 |
| QueryType | string | 列表查询类型：1-急需续费, 2-急需赎回 | 1 |
| OrderKeyType | string | 排序字段：RegistrationDate（注册时间）/ ExpirationDate（到期时间） | RegistrationDate |
| OrderByType | string | 排序顺序：ASC（升序）/ DESC（倒序），默认 DESC | ASC |
| ProductDomainType | string | 域名类型：New gTLD（新顶级域）/ gTLD（通用顶级域）/ ccTLD（国别域） | New gTLD |
| DomainGroupId | string | 域名分组编号 | 123456 |
| ResourceGroupId | string | 资源组 ID | rg-aek2indvyxgpfti |
| Tag | array | 标签列表（最多 21 个） | [{Key: "备注", Value: "标签1"}] |
| Ccompany | string | 域名所有者名称 | 广州金烨再生资源回收有限公司 |
| Registrar | string | 注册商 | - |
| Dns | string | DNS | - |
| UserClientIp | string | 用户 IP，可设置为 127.0.0.1 | 127.0.0.1 |
| Lang | string | 接口返回错误信息语言：zh（中文）/ en（英文），默认 en | en |

### 响应结构

```python
{
    "PrePage": false,                    # 是否有上一页
    "CurrentPageNum": 0,                 # 当前页码
    "RequestId": "B7AB5469-5E38-4AA9-A920-C65B7A9C8E6E",  # 请求 ID
    "PageSize": 5,                       # 每页大小
    "TotalPageNum": 1,                   # 总页数
    "Data": {
        "Domain": [                      # 域名列表
            {
                "DomainAuditStatus": "FAILED",  # 实名认证状态：FAILED/SUCCEED/NONAUDIT/AUDITING
                "DomainGroupId": "123456",       # 域名分组编号
                "Remark": "测试备注",             # 域名备注
                "DomainGroupName": "测试分组",    # 域名分组名称
                "RegistrationDate": "2017-11-02 04:00:45",  # 注册时间
                "InstanceId": "ST20151102120031118",  # 实例编号
                "DomainName": "test.com",        # 域名
                "ExpirationDateStatus": "1",     # 过期状态：1-未过期, 2-已过期
                "ExpirationDate": "2017-11-02 04:00:45",  # 到期日期
                "RegistrantType": "1",           # 注册类型：1-个人, 2-企业
                "ExpirationDateLong": 1522080000000,  # 到期时长（毫秒时间戳）
                "ExpirationCurrDateDiff": -30,   # 到期日与当前时间的天数差
                "Premium": true,                 # 是否溢价域名
                "RegistrationDateLong": 1522080000000,  # 注册时长（毫秒时间戳）
                "ProductId": "2a",               # 产品 ID
                "DomainStatus": "3",             # 域名状态：1-急需续费, 2-急需赎回, 3-正常
                "DomainType": "gTLD",            # 域名类型
                "ResourceGroupId": "rg-aek2yyciz557g3q",  # 资源组 ID
                "Tag": {
                    "Tag": [
                        {"Key": "费用", "Value": "标签1"}
                    ]
                },
                "Ccompany": "广州森林广告装饰有限公司",  # 域名所有者名称
                "ChgholderStatus": "0",          # 域名过户状态：0-正常, 1-过户中, 2-过户失败
                "Registrar": "...",              # 注册商
                "DnsList": {
                    "DnsList": ["ns1.example.com", "ns2.example.com"]  # DNS 列表
                }
            }
        ]
    },
    "TotalItemNum": 1,                   # 域名总数
    "NextPage": false                    # 是否有下一页
}
```

### 核心流程

1. 从环境变量或 `.env` 文件读取 `ALIBABA_CLOUD_ACCESS_KEY_ID` / `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
2. 创建 `Domain20180129Client`
3. 构建 `QueryDomainListRequest`，设置必填参数和可选筛选条件
4. 调用 `query_domain_list_with_options`
5. 解析返回的域名列表 JSON

示例代码参考：[scripts/query_domainlist.py](scripts/query_domainlist.py)

完整的 API 参数和响应结构文档：[reference/query_domainlist.yml](reference/query_domainlist.yml)

### 常见查询场景

#### 场景 1：查询所有域名（基础查询）

```python
request = domain_20180129_models.QueryDomainListRequest(
    page_num=1,
    page_size=20
)
```

#### 场景 2：按域名搜索

```python
request = domain_20180129_models.QueryDomainListRequest(
    page_num=1,
    page_size=20,
    domain_name="test.com"
)
```

#### 场景 3：查询即将到期的域名

```python
import time

# 计算今天到未来30天的毫秒时间戳
today = int(time.time() * 1000)
thirty_days_later = today + 30 * 24 * 60 * 60 * 1000

request = domain_20180129_models.QueryDomainListRequest(
    page_num=1,
    page_size=20,
    start_expiration_date=today,
    end_expiration_date=thirty_days_later,
    order_key_type="ExpirationDate",
    order_by_type="ASC"
)
```

#### 场景 4：查询急需续费的域名

```python
request = domain_20180129_models.QueryDomainListRequest(
    page_num=1,
    page_size=20,
    query_type="1"  # 1-急需续费
)
```

#### 场景 5：按资源组筛选

```python
request = domain_20180129_models.QueryDomainListRequest(
    page_num=1,
    page_size=20,
    resource_group_id="rg-aek2indvyxgpfti"
)
```

#### 场景 6：按标签筛选

```python
request = domain_20180129_models.QueryDomainListRequest(
    page_num=1,
    page_size=20,
    tag=[
        {"Key": "环境", "Value": "生产"}
    ]
)
```

## 错误处理建议

- `401/403`：AK/SK 无效、未配置或 RAM 权限不足
- `InvalidAccessKeyId`：AccessKeyId 错误
- `SignatureDoesNotMatch`：AccessKeySecret 错误或签名不一致
- 若异常包含 `Recommend` 字段，优先按诊断链接排查

## 使用流程

1. 检查环境变量或 `.env` 文件，确认 AK/SK 已配置
2. 安装依赖
3. 根据查询需求构建请求参数（必填参数 + 可选筛选条件）
4. 调用 `query_domain_list_with_options`
5. 获取并解析返回的域名列表 JSON

## 注意事项

- **reference/** 中的 YML 用于查阅 API 入参与返回值；**scripts/** 中的脚本可直接运行，便于验证环境与 SDK 调用。
- 若业务场景与示例不同，可在阅读 YML 与脚本实现后自行改写或新建代码。
- 时间戳参数（如 `StartExpirationDate`）需要使用毫秒级时间戳
- 分页查询时，根据需要调整 `PageNum` 和 `PageSize`

---

# 检查域名可注册性（CheckDomain）

通过 Python SDK `alibabacloud_domain20180129` 调用阿里云 Domain OpenAPI，检查指定域名是否可注册以及获取价格信息。

### 前置检查（必须首先执行）

执行任何查询前，必须先确认 AK/SK 已配置。

**检查顺序**

1. 优先检查环境变量

```bash
echo "AK_ID: ${ALIBABA_CLOUD_ACCESS_KEY_ID:+已设置}"
echo "AK_SECRET: ${ALIBABA_CLOUD_ACCESS_KEY_SECRET:+已设置}"
```

2. 如果未设置，检查当前工作目录的 `.env` 文件

```bash
find . -maxdepth 1 -name ".env" -exec cat {} \;
```

`.env` 文件格式：

```dotenv
ALIBABA_CLOUD_ACCESS_KEY_ID=your-access-key-id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-access-key-secret
```

3. Python 代码中加载凭证

```python
from dotenv import load_dotenv
import os

# 先尝试从环境变量读取
access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

# 如果未设置，尝试从 .env 文件加载
if not access_key_id or not access_key_secret:
    load_dotenv()  # 从当前工作目录的 .env 文件加载
    access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

if not access_key_id or not access_key_secret:
    raise RuntimeError("缺少阿里云凭证。请先设置 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET")
```

未通过凭证检查时，不应继续执行查询步骤。

### 安装依赖

```bash
pip install -r aliyun-domain-skills/scripts/requirements.txt
```

或手动安装：

```bash
pip install alibabacloud_domain20180129 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util python-dotenv
```

### CheckDomain 用法

#### 请求参数

**必填参数**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| DomainName | string | 域名名称 | test**.xin |

**可选参数**

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| FeeCommand | string | 操作命令：create（新购）/ renew（续费）/ transfer（转入）/ restore（赎回） | create |
| FeeCurrency | string | 货币类型：USD（美元） | USD |
| FeePeriod | integer | 购买周期年限（1-10年） | 1 |
| Lang | string | 接口返回错误信息语言：zh（中文）/ en（英文），默认 en | en |

#### 响应结构

```python
{
    "RequestId": "BA7A4FD4-EB9A-4A20-BB0C-9AEB15634DC1",  # 唯一请求识别码
    "Avail": "1",                    # 域名是否可以注册：1-可注册, 3-预登记, 4-可删除预订, 0-不可注册, -1-异常, -2-暂停注册, -3-黑名单
    "Price": 1286,                   # 溢价词注册价格
    "DomainName": "test**.xin",      # 查询的域名名称
    "Premium": "true",               # 是否是溢价词：true/false
    "DynamicCheck": true,            # 是否动态询价
    "Reason": "In use",              # 由注册局返回的不可注册原因
    "StaticPriceInfo": {             # 静态价格信息
        "PriceInfo": [
            {
                "action": "activate",  # 操作类型（activate：新购）
                "money": 78.0,         # 金额，单位元
                "period": 12           # 周期，单位月
            }
        ]
    }
}
```

#### 核心流程

1. 从环境变量或 `.env` 文件读取 `ALIBABA_CLOUD_ACCESS_KEY_ID` / `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
2. 创建 `Domain20180129Client`
3. 构建 `CheckDomainRequest`，设置域名名称（必填）和可选参数
4. 调用 `check_domain_with_options`
5. 解析返回的域名检查结果 JSON

示例代码参考：[scripts/check_domain.py](scripts/check_domain.py)

完整的 API 参数和响应结构文档：[reference/check_domain.yml](reference/check_domain.yml)

#### 常见使用场景

#### 场景 1：检查域名是否可注册（基础查询）

```python
request = domain_20180129_models.CheckDomainRequest(
    domain_name="example.com"
)
```

#### 场景 2：检查域名新购价格

```python
request = domain_20180129_models.CheckDomainRequest(
    domain_name="example.com",
    fee_command="create",
    fee_currency="USD",
    fee_period=1
)
```

#### 场景 3：检查域名续费价格

```python
request = domain_20180129_models.CheckDomainRequest(
    domain_name="example.com",
    fee_command="renew",
    fee_currency="USD",
    fee_period=1
)
```

#### 场景 4：检查域名转入价格

```python
request = domain_20180129_models.CheckDomainRequest(
    domain_name="example.com",
    fee_command="transfer"
)
```

#### 场景 5：批量检查多个域名

```python
domains_to_check = ["example1.com", "example2.com", "example3.com"]

for domain in domains_to_check:
    request = domain_20180129_models.CheckDomainRequest(
        domain_name=domain
    )
    resp = client.check_domain_with_options(request, runtime)
    # 处理结果
```

### 错误处理建议

- `401/403`：AK/SK 无效、未配置或 RAM 权限不足
- `InvalidAccessKeyId`：AccessKeyId 错误
- `SignatureDoesNotMatch`：AccessKeySecret 错误或签名不一致
- 若异常包含 `Recommend` 字段，优先按诊断链接排查

### 使用流程

1. 检查环境变量或 `.env` 文件，确认 AK/SK 已配置
2. 安装依赖
3. 根据需求构建请求参数（必填参数 + 可选参数）
4. 调用 `check_domain_with_options`
5. 获取并解析返回的域名检查结果 JSON

### 注意事项

- 调用 CheckDomain 接口时有频率限制，同一阿里云账号及其 RAM 用户调用该接口的限制为 10QPS，接口总量限制为 100QPS
- 有关域名的合法性要求，请参考[域名合法性](~~67788~~)
- **reference/** 中的 YML 用于查阅 API 入参与返回值；**scripts/** 中的脚本可直接运行，便于验证环境与 SDK 调用。
- 若业务场景与示例不同，可在阅读 YML 与脚本实现后自行改写或新建代码。

---

所有新增能力都遵循"独立调用、按需组合"的原则。

