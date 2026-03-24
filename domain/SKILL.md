---
name: aliyun-domain-skill
description: >-
  通过 Python 调用阿里云 OpenAPI：（1）域名注册/查询侧：QueryDomainList、CheckDomain（alibabacloud_domain20180129）；
  （2）云解析 DNS 侧：DescribeDomainRecords、AddDomainRecord、UpdateDomainRecord（alibabacloud_alidns20150109）。
  适用于「列出账号域名」「查可注册性与价格」「查/增/改 DNS 解析记录」「新增 A/CNAME 等」「按 RecordId 更新记录」场景；DNS 与域名列表/可注册性为不同产品面，可按需组合。
  API 契约见 reference/ 下 YML；示例见 scripts/；依赖见 scripts/requirements.txt。
---

## 能力概述

本 skill 同时覆盖 **域名信息服务（Domain）** 与 **云解析 DNS（Alidns）** 两类 API，SDK 与 endpoint 不同，请勿混用。

## 目录结构

```
aliyun-domain-skills/
├── SKILL.md
├── reference/                    # API 定义（YML），含入参与返回值
│   ├── check_domain.yml
│   ├── query_domainlist.yml
│   ├── describe_domain_records.yml
│   ├── add_domain_record.yml
│   └── update_domain_record.yml
└── scripts/                      # 可执行脚本与依赖清单
    ├── check_domain.py
    ├── query_domainlist.py
    ├── describe_domain_records.py
    ├── add_domain_record.py
    ├── update_domain_record.py
    └── requirements.txt
```

- **reference/**：存放 API 相关信息，包括入参、返回值等（YML），供查阅契约与字段含义。
- **scripts/**：可直接运行的 Python 脚本（例如 `python scripts/query_domainlist.py`）；也可阅读其实现，在此基础上编写或改写新代码。
- **依赖**：`requirements.txt` 位于 `scripts/` 目录；初次使用请先执行 `pip install -r aliyun-domain-skills/scripts/requirements.txt` 安装依赖。

本 skill 提供以下**独立能力**，可根据实际需求单独调用或组合使用：

| 能力 | API | 产品/SDK | 用途 | 使用场景 |
|------|-----|----------|------|----------|
| **查询域名列表** | QueryDomainList | Domain / domain20180129 | 查询账号下的域名列表 | 列出账号域名、检查域名资产、筛选即将到期的域名 |
| **检查域名可注册性** | CheckDomain | Domain / domain20180129 | 检查域名是否可注册及价格 | 域名注册前检查、批量域名可用性评估 |
| **列出解析记录** | DescribeDomainRecords | Alidns / alidns20150109 | 按主域名分页查询解析记录 | 排查解析、获取 RecordId |
| **添加解析记录** | AddDomainRecord | Alidns / alidns20150109 | 在主域名下新增一条解析记录 | 新上线子域、新增 A/CNAME 等 |
| **修改解析记录** | UpdateDomainRecord | Alidns / alidns20150109 | 按 RecordId 更新 RR、类型、记录值等 | 切流量、改 IP、调整 TTL/线路 |

**重要说明**：
- **Domain** 与 **Alidns** 为不同产品与 SDK；QueryDomainList / CheckDomain 与 DescribeDomainRecords / AddDomainRecord / UpdateDomainRecord 之间无强制调用顺序，可按业务组合。
- QueryDomainList 与 CheckDomain 彼此独立；若需「先列域名再查价格」，可自行组合（例如先 QueryDomainList，再 CheckDomain，`fee_command=renew`）。
- **AddDomainRecord、UpdateDomainRecord 为写操作**：新增前建议用 DescribeDomainRecords 确认是否已存在同 RR+Type+线路，避免重复；更新前通常需先取得目标记录的 **RecordId**；执行前请确认影响范围。

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
pip install alibabacloud_domain20180129 alibabacloud_alidns20150109 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util python-dotenv
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
pip install alibabacloud_domain20180129 alibabacloud_alidns20150109 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util python-dotenv
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

# 列出解析记录（DescribeDomainRecords）

通过 Python SDK `alibabacloud_alidns20150109` 调用**云解析 DNS** OpenAPI，分页查询指定**主域名**下的解析记录列表（含 **RecordId**，供后续修改记录使用）。

## 产品与客户端

- **SDK 包**：`alibabacloud_alidns20150109`
- **客户端**：`Alidns20150109Client`
- **Endpoint**：`alidns.aliyuncs.com`（与 Domain 的 `domain20180129` 不同）

## 前置检查与依赖

AK/SK 的检查顺序与上文「查询域名列表（QueryDomainList）」章节中的「前置检查」一致。

安装依赖（`requirements.txt` 已包含 Domain 与 Alidns 两套 SDK）：

```bash
pip install -r aliyun-domain-skills/scripts/requirements.txt
```

或手动安装时至少包含：`alibabacloud_alidns20150109` 及凭证、Tea 相关包（与仓库内 `requirements.txt` 保持一致）。

## DescribeDomainRecords 用法

### 请求参数（摘要）

**必填**

| 参数 | 类型 | 说明 |
|------|------|------|
| DomainName | string | 主域名，如 `example.com` |

**常用可选**

| 参数 | 类型 | 说明 |
|------|------|------|
| PageNumber | integer | 页码，从 1 开始，默认 1 |
| PageSize | integer | 每页行数，最大 500，默认 20 |
| Lang | string | 请求/响应语言，`zh` / `en` 等 |
| KeyWord | string | 通用关键字 |
| RRKeyWord | string | 主机记录关键字（模糊，依 SearchMode） |
| TypeKeyWord | string | 解析类型关键字（全匹配） |
| ValueKeyWord | string | 记录值关键字（模糊，依 SearchMode） |
| SearchMode | string | `LIKE` / `EXACT` / `ADVANCED` / `COMBINATION` 等，与上述关键字字段配合方式见官方文档 |
| GroupId | integer | 域名分组 ID；`0`/`-1`/`-2` 等有特殊含义，见 YML |
| Type / Line / Status | string | 按记录类型、线路、状态（Enable/Disable）筛选 |

完整参数与响应字段见 [reference/describe_domain_records.yml](reference/describe_domain_records.yml)。

### 响应要点

- 返回体中的解析记录列表包含每条记录的 **RecordId**、**RR**、**Type**、**Value**、**TTL** 等字段；**RecordId** 为调用 `UpdateDomainRecord` 的必备参数。

### 核心流程

1. 配置 AK/SK（环境变量或 `.env`）
2. 创建 `Alidns20150109Client`，`config.endpoint = 'alidns.aliyuncs.com'`
3. 构建 `DescribeDomainRecordsRequest`，至少设置 `domain_name`
4. 调用 `describe_domain_records_with_options`
5. 解析分页结果，按需遍历 `PageNumber` 直至取全记录

示例代码参考：[scripts/describe_domain_records.py](scripts/describe_domain_records.py)

### 错误处理建议

- `401/403`：凭证无效或 RAM 无云解析相关权限
- `InvalidAccessKeyId` / `SignatureDoesNotMatch`：同前文
- 异常若含 `Recommend`，按诊断信息排查

---

# 添加解析记录（AddDomainRecord）

通过同一 SDK `alibabacloud_alidns20150109` 调用 **AddDomainRecord**，在指定**主域名**下**新增**一条解析记录（与 UpdateDomainRecord 不同：无需已有 RecordId，由接口返回新 RecordId）。

## 前置检查与依赖

与上文「列出解析记录（DescribeDomainRecords）」一节相同。写操作前请确认 **DomainName**、**RR**、**Type**、**Value** 正确，避免与已有记录冲突或误指生产流量。

## AddDomainRecord 用法

### 请求参数（摘要）

**必填**

| 参数 | 类型 | 说明 |
|------|------|------|
| DomainName | string | 主域名，如 `example.com`（可通过 DescribeDomains 等获取） |
| RR | string | 主机记录；解析主域名本身填 `@`，不要留空 |
| Type | string | 记录类型，如 `A`、`CNAME`、`MX` 等 |
| Value | string | 记录值 |

**常用可选**

| 参数 | 类型 | 说明 |
|------|------|------|
| TTL | integer | 生效时间（秒），默认 600，范围 1–86400 |
| Priority | integer | MX 优先级（MX 记录时常必填），范围见 YML |
| Line | string | 解析线路，默认 `default` |
| Lang / UserClientIp | string | 语言、客户端 IP |

完整参数与响应见 [reference/add_domain_record.yml](reference/add_domain_record.yml)。

### 响应要点

- 成功时返回 **RequestId** 与新建记录的 **RecordId**（后续可用 **UpdateDomainRecord** 按该 ID 修改）。

### 与 DescribeDomainRecords 的配合

1. 可选：对主域名调用 **DescribeDomainRecords**，确认不存在冲突的 RR + Type + 线路组合。
2. 构建 **AddDomainRecordRequest**，设置 DomainName、RR、Type、Value 及可选 TTL/Line 等。
3. 调用 **add_domain_record_with_options**，保存返回的 **RecordId** 供后续运维或更新使用。

### 核心流程

1. 配置 AK/SK
2. 创建 `Alidns20150109Client`（endpoint：`alidns.aliyuncs.com`）
3. 构建 `AddDomainRecordRequest`，设置必填与可选参数
4. 调用 `add_domain_record_with_options`

示例代码参考：[scripts/add_domain_record.py](scripts/add_domain_record.py)

### 错误处理建议

- 同 DescribeDomainRecords；写操作失败时注意是否因记录已存在、域名未在解析中、权限不足或参数不合法。

---

# 修改解析记录（UpdateDomainRecord）

通过同一 SDK `alibabacloud_alidns20150109` 调用 **UpdateDomainRecord**，按 **RecordId** 修改已有解析记录（主机记录、类型、记录值、TTL、线路等）。

## 前置检查与依赖

与上文「列出解析记录（DescribeDomainRecords）」一节相同；写操作前请再次确认目标 **RecordId** 与 **Value**，避免误改生产解析。

## UpdateDomainRecord 用法

### 请求参数（摘要）

**必填**

| 参数 | 类型 | 说明 |
|------|------|------|
| RecordId | string | 解析记录 ID，通常由 DescribeDomainRecords 返回 |
| RR | string | 主机记录；主域名解析填 `@` |
| Type | string | 记录类型，如 `A`、`CNAME`、`MX` 等 |
| Value | string | 记录值 |

**常用可选**

| 参数 | 类型 | 说明 |
|------|------|------|
| TTL | integer | 生效时间（秒），默认 600，范围 1–86400 |
| Priority | integer | MX 优先级（MX 记录时常必填），范围见 YML |
| Line | string | 解析线路，默认 `default` |
| Lang / UserClientIp | string | 语言、客户端 IP |

完整参数与响应见 [reference/update_domain_record.yml](reference/update_domain_record.yml)。

### 响应要点

- 成功时返回 **RequestId** 与 **RecordId**（与请求修改的记录一致）。

### 与 DescribeDomainRecords 的配合

1. 对主域名调用 **DescribeDomainRecords**，在结果中定位 **RR** + **Type**（及线路）对应的记录，读取 **RecordId**。
2. 使用同一 **RecordId** 调用 **UpdateDomainRecord**，更新 **Value** / **TTL** / **Line** 等。

### 核心流程

1. 配置 AK/SK
2. 创建 `Alidns20150109Client`（endpoint 同上）
3. 构建 `UpdateDomainRecordRequest`，设置 RecordId、RR、Type、Value 及可选参数
4. 调用 `update_domain_record_with_options`

示例代码参考：[scripts/update_domain_record.py](scripts/update_domain_record.py)

### 错误处理建议

- 同 DescribeDomainRecords；写操作失败时注意是否因记录不存在、权限不足或与当前解析状态冲突。

---

## 能力扩展

本 skill 已包含 **Domain**（QueryDomainList、CheckDomain）与 **Alidns**（DescribeDomainRecords、AddDomainRecord、UpdateDomainRecord）的契约与示例脚本。后续仍可继续追加其它独立 API（例如域名详情、注册任务、更多 DNS 操作等），建议仍以「reference YML + scripts 示例 + 能力表一行」的方式扩展。

所有能力均遵循「独立调用、按需组合」的原则。

