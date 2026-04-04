---
name: aliyun-cdn-skill
description: >-
  通过 Python SDK（alibabacloud_cdn20180510）调用阿里云 CDN OpenAPI：查询加速域名列表与详情、域名配置、CNAME 解析检测、备案查询、域名归属校验（查询校验内容/校验数据、提交校验）、添加域名、批量更新、批量设置域名功能配置、缓存刷新、启用域名、HTTPS 证书设置等。
  适用于「列出 CDN 加速域名」「查详情与配置」「检测 CNAME」「查备案」「域名归属验证」「加域名/批量改配/批量设功能项/刷缓存/启停/配证书」等场景。
  默认采用阿里云 OSS 私有 Bucket 回源方式（源站类型为 OSS 时开启私有 Bucket 回源），保障源站安全性。
  API 契约见 reference/ 下 YML；可运行示例见 scripts/；初次使用请安装 scripts/requirements.txt 中的依赖。
---

## 能力概述

## 目录结构

```
aliyun-cdn-skills/
├── SKILL.md
├── reference/                    # API 定义（YML），含入参与返回值
│   ├── describe_user_domains.yml
│   ├── describe_cdndomain_detail.yml
│   ├── describe_cdndomain_configs.yml
│   ├── describe_domain_cname.yml
│   ├── check_cdndomain_icp.yml
│   ├── describe_verify_content.yml
│   ├── describe_domain_verify_data.yml
│   ├── verify_domain_owner.yml
│   ├── add_cdndomain.yml
│   ├── batch_update_cdndomain.yml
│   ├── batch_set_cdndomain_config.yml
│   ├── refresh_object_caches.yml
│   ├── start_cdndomain.yml
│   └── set_cdndomain_sslcertificate.yml
└── scripts/                      # 可执行脚本与依赖清单
    ├── describe_user_domains.py
    ├── describe_cdndomain_detail.py
    ├── describe_cdndomain_configs.py
    ├── describe_domain_cname.py
    ├── check_cdndomain_icp.py
    ├── describe_verify_content.py
    ├── describe_domain_verify_data.py
    ├── verify_domain_owner.py
    ├── add_cdndomain.py
    ├── batch_update_cdndomain.py
    ├── batch_set_cdndomain_config.py
    ├── refresh_object_caches.py
    ├── start_cdndomain.py
    ├── set_cdndomain_sslcertificate.py
    └── requirements.txt
```

- **reference/**：存放 API 相关信息，包括入参、返回值等（YML），供查阅契约与字段含义。
- **scripts/**：可直接运行的 Python 脚本（例如 `python scripts/describe_user_domains.py`）；也可阅读其实现，在此基础上编写或改写新代码。
- **依赖**：`requirements.txt` 位于 `scripts/` 目录；初次使用请先执行 `pip install -r aliyun-cdn-skills/scripts/requirements.txt` 安装依赖。

本 skill 提供以下**独立能力**，可根据实际需求单独调用或组合使用：

| 能力 | API | 类型 | 用途 | reference | scripts |
|------|-----|------|------|-----------|---------|
| 查询用户域名列表 | DescribeUserDomains | 读 | 分页查询账号下加速域名及状态，支持筛选 | [describe_user_domains.yml](reference/describe_user_domains.yml) | [describe_user_domains.py](scripts/describe_user_domains.py) |
| 查询域名详情 | DescribeCdnDomainDetail | 读 | 查询指定加速域名的基本配置（源站、CNAME、状态等） | [describe_cdndomain_detail.yml](reference/describe_cdndomain_detail.yml) | [describe_cdndomain_detail.py](scripts/describe_cdndomain_detail.py) |
| 查询域名功能配置 | DescribeCdnDomainConfigs | 读 | 按功能名或 ConfigId 查询域名上的功能配置 | [describe_cdndomain_configs.yml](reference/describe_cdndomain_configs.yml) | [describe_cdndomain_configs.py](scripts/describe_cdndomain_configs.py) |
| 检测 CNAME | DescribeDomainCname | 读 | 检测加速域名 CNAME 是否解析到预期 | [describe_domain_cname.yml](reference/describe_domain_cname.yml) | [describe_domain_cname.py](scripts/describe_domain_cname.py) |
| 查询备案 | CheckCdnDomainICP | 读 | 查询域名是否备案 | [check_cdndomain_icp.yml](reference/check_cdndomain_icp.yml) | [check_cdndomain_icp.py](scripts/check_cdndomain_icp.py) |
| 查询归属校验内容 | DescribeVerifyContent | 读 | 查询域名归属校验所需内容（单域名） | [describe_verify_content.yml](reference/describe_verify_content.yml) | [describe_verify_content.py](scripts/describe_verify_content.py) |
| 查询域名校验数据 | DescribeDomainVerifyData | 读 | 按全球资源计划等返回对应校验数据（单域名） | [describe_domain_verify_data.yml](reference/describe_domain_verify_data.yml) | [describe_domain_verify_data.py](scripts/describe_domain_verify_data.py) |
| 校验域名归属 | VerifyDomainOwner | 写 | 对域名归属权进行校验（单域名） | [verify_domain_owner.yml](reference/verify_domain_owner.yml) | [verify_domain_owner.py](scripts/verify_domain_owner.py) |
| 添加加速域名 | AddCdnDomain | 写 | 新增加速域名 | [add_cdndomain.yml](reference/add_cdndomain.yml) | [add_cdndomain.py](scripts/add_cdndomain.py) |
| 批量更新域名 | BatchUpdateCdnDomain | 写 | 批量更新加速域名基本信息 | [batch_update_cdndomain.yml](reference/batch_update_cdndomain.yml) | [batch_update_cdndomain.py](scripts/batch_update_cdndomain.py) |
| 批量设置域名配置 | BatchSetCdnDomainConfig | 写 | 批量为多个域名设置功能配置（域名数与功能项数乘积等限制见 YML） | [batch_set_cdndomain_config.yml](reference/batch_set_cdndomain_config.yml) | [batch_set_cdndomain_config.py](scripts/batch_set_cdndomain_config.py) |
| 刷新缓存 | RefreshObjectCaches | 写 | URL/目录批量刷新，使节点缓存立即失效并回源 | [refresh_object_caches.yml](reference/refresh_object_caches.yml) | [refresh_object_caches.py](scripts/refresh_object_caches.py) |
| 启用域名 | StartCdnDomain | 写 | 启用处于停用状态的加速域名 | [start_cdndomain.yml](reference/start_cdndomain.yml) | [start_cdndomain.py](scripts/start_cdndomain.py) |
| 设置 HTTPS 证书 | SetCdnDomainSSLCertificate | 写 | 设置证书开关与证书内容（上传/CAS 等） | [set_cdndomain_sslcertificate.yml](reference/set_cdndomain_sslcertificate.yml) | [set_cdndomain_sslcertificate.py](scripts/set_cdndomain_sslcertificate.py) |

**重要说明**：

- 每个能力对应一个独立 API，**无固定调用顺序**；可按业务组合（例如先列表再详情、加域名前做备案检查）。
- **写操作**（添加、批量更新、批量设配置、刷新缓存、归属校验提交、启用、证书等）需要账号或 RAM 用户具备相应 CDN **写权限**；生产环境变更前建议先在控制台或测试域名验证。**RefreshObjectCaches** 会使缓存立即失效、回源量增加，请控制批量与频率。

---

## 前置检查（必须首先执行）

执行任何调用前，必须先确认 AK/SK 已配置。

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

access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

if not access_key_id or not access_key_secret:
    load_dotenv()
    access_key_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
    access_key_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "").strip()

if not access_key_id or not access_key_secret:
    raise RuntimeError("缺少阿里云凭证。请先设置 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET")
```

未通过凭证检查时，不应继续执行后续步骤。

## 安装依赖

```bash
pip install -r aliyun-cdn-skills/scripts/requirements.txt
```

或手动安装：

```bash
pip install alibabacloud_cdn20180510 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util python-dotenv
```

## 客户端初始化（CDN）

使用凭据链初始化 `Cdn20180510Client`，endpoint 固定为 `cdn.aliyuncs.com`（与现有脚本一致）：

```python
from alibabacloud_cdn20180510.client import Client as Cdn20180510Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models

credential = CredentialClient()
config = open_api_models.Config(credential=credential)
config.endpoint = "cdn.aliyuncs.com"
client = Cdn20180510Client(config)
```

各 API 的请求模型位于 `alibabacloud_cdn20180510.models`，调用形态为 `client.<api>_with_options(request, runtime)`，具体见对应 `scripts/*.py`。

## 分页（DescribeUserDomains）

[reference/describe_user_domains.yml](reference/describe_user_domains.yml) 中 `PageSize` 取值 **1～500**（默认 20），`PageNumber` 为页码。需要拉取**全量域名**时，应在代码中循环递增 `PageNumber`，直到返回数据不足一页或达到总页数。

仓库内 [scripts/describe_user_domains.py](scripts/describe_user_domains.py) 为最小示例（未填分页参数）；生产或全量同步需自行实现分页循环。

## 常见组合（非强制）

- 运维排查：DescribeUserDomains → DescribeCdnDomainDetail / DescribeCdnDomainConfigs。
- 接入与解析：DescribeDomainCname 验证 CNAME；DescribeCdnDomainDetail 查看分配的 CNAME。
- 新域名上线前：CheckCdnDomainICP 与业务要求核对后，再 AddCdnDomain 或后续改配。
- 域名归属：DescribeVerifyContent / DescribeDomainVerifyData 获取校验方式与数据，按控制台或文档完成 DNS/文件等验证后，再 **VerifyDomainOwner** 提交校验（具体参数与流程以 YML、官方文档为准）。
- 批量改功能项：BatchSetCdnDomainConfig 与 BatchUpdateCdnDomain 关注点不同（前者偏域名上的 **Functions** 批量配置），按 YML 限制控制单次域名数与功能项数。
- 发布与缓存：**RefreshObjectCaches** 在资源更新后刷新 URL/目录；注意单次任务 URL 域名个数等配额（见 YML）。
- HTTPS：DescribeCdnDomainDetail 看证书状态后，SetCdnDomainSSLCertificate 更新证书或开关。

## 错误处理建议

- `401/403`：AK/SK 无效、未配置或 RAM 权限不足。
- `InvalidAccessKeyId`：AccessKeyId 错误。
- `SignatureDoesNotMatch`：AccessKeySecret 错误或签名不一致。
- 若异常包含 `data` 且其中有 `Recommend`，优先按诊断链接排查。

---

# 各 API 说明（简要）

以下仅作索引；**请求/响应字段以对应 YML 为准**，示例调用以 **scripts** 为准。

## DescribeUserDomains

查询账号下加速域名列表，支持域名模糊匹配、状态等筛选。详见 [reference/describe_user_domains.yml](reference/describe_user_domains.yml)，示例：[scripts/describe_user_domains.py](scripts/describe_user_domains.py)。

## DescribeCdnDomainDetail

查询单个加速域名的基本信息（源站、CNAME、业务类型、运行状态等）。详见 [reference/describe_cdndomain_detail.yml](reference/describe_cdndomain_detail.yml)，示例：[scripts/describe_cdndomain_detail.py](scripts/describe_cdndomain_detail.py)。

## DescribeCdnDomainConfigs

查询域名上已配置的功能项（如 `FunctionNames` 逗号分隔）。详见 [reference/describe_cdndomain_configs.yml](reference/describe_cdndomain_configs.yml)，示例：[scripts/describe_cdndomain_configs.py](scripts/describe_cdndomain_configs.py)。

## DescribeDomainCname

对加速域名做 CNAME 解析检测（单次最多域名个数见 YML 说明）。详见 [reference/describe_domain_cname.yml](reference/describe_domain_cname.yml)，示例：[scripts/describe_domain_cname.py](scripts/describe_domain_cname.py)。

## CheckCdnDomainICP

查询域名备案相关信息。**读接口**，用于合规核对。详见 [reference/check_cdndomain_icp.yml](reference/check_cdndomain_icp.yml)，示例：[scripts/check_cdndomain_icp.py](scripts/check_cdndomain_icp.py)。

## DescribeVerifyContent

查询加速域名**归属校验**所需内容（单域名）。**读接口**。详见 [reference/describe_verify_content.yml](reference/describe_verify_content.yml)，示例：[scripts/describe_verify_content.py](scripts/describe_verify_content.py)。

## DescribeDomainVerifyData

根据域名及是否开启**全球资源计划**等条件，返回对应的校验数据/内容（单域名）。**读接口**。详见 [reference/describe_domain_verify_data.yml](reference/describe_domain_verify_data.yml)，示例：[scripts/describe_domain_verify_data.py](scripts/describe_domain_verify_data.py)。

## VerifyDomainOwner

对域名归属权进行校验（单域名）。OpenAPI 标记为写类操作，调用前通常需先完成 DNS/文件等验证步骤。**写接口**。详见 [reference/verify_domain_owner.yml](reference/verify_domain_owner.yml)，示例：[scripts/verify_domain_owner.py](scripts/verify_domain_owner.py)。

## AddCdnDomain

新增加速域名。**写接口**，需具备创建与配置权限；参数较多（源站、加速区域、业务类型等），务必对照 YML 填写。详见 [reference/add_cdndomain.yml](reference/add_cdndomain.yml)，示例：[scripts/add_cdndomain.py](scripts/add_cdndomain.py)。

## BatchUpdateCdnDomain

批量更新加速域名基本信息。**写接口**，变更前建议确认影响范围。详见 [reference/batch_update_cdndomain.yml](reference/batch_update_cdndomain.yml)，示例：[scripts/batch_update_cdndomain.py](scripts/batch_update_cdndomain.py)。

## BatchSetCdnDomainConfig

对多个加速域名**批量设置功能配置**（`Functions` 等）。**写接口**；单次域名个数、与功能项数量的乘积上限等以 YML 为准。详见 [reference/batch_set_cdndomain_config.yml](reference/batch_set_cdndomain_config.yml)，示例：[scripts/batch_set_cdndomain_config.py](scripts/batch_set_cdndomain_config.py)。

## RefreshObjectCaches

按 URL 或目录**刷新**节点缓存，使对应对象缓存失效并回源拉取最新内容；支持批量，**写接口**。注意回源与配额（单次 URL 中域名个数等见 YML）。详见 [reference/refresh_object_caches.yml](reference/refresh_object_caches.yml)，示例：[scripts/refresh_object_caches.py](scripts/refresh_object_caches.py)。

## StartCdnDomain

将**停用**状态的加速域名启用为 Online。**写接口**，需域名与账户状态正常。详见 [reference/start_cdndomain.yml](reference/start_cdndomain.yml)，示例：[scripts/start_cdndomain.py](scripts/start_cdndomain.py)。

## SetCdnDomainSSLCertificate

配置 HTTPS 证书开关（`SSLProtocol`）及证书内容或 CAS 证书引用等。**写接口**；涉及证书与私钥时注意保密与权限。详见 [reference/set_cdndomain_sslcertificate.yml](reference/set_cdndomain_sslcertificate.yml)，示例：[scripts/set_cdndomain_sslcertificate.py](scripts/set_cdndomain_sslcertificate.py)。

---

## 注意事项

- **reference/** 中的 YML 用于查阅 API 入参与返回值；**scripts/** 中的脚本可直接运行以验证环境与 SDK 调用。
- 若业务场景与示例不同，在阅读 YML 与脚本后自行改写或新建代码。
- 写操作类 API 请遵循最小权限原则，为 RAM 用户配置所需动作即可。

## 能力扩展

本 skill 可继续增加其他 CDN OpenAPI（例如停用域名、预热等），建议同样以「reference YML + scripts 示例 + 本表追加一行」的方式扩展，保持与 [aliyun-domain-skills](../aliyun-domain-skills/SKILL.md) 一致的使用体验。

