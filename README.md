# 阿里云 OpenAPI Skills 集合

这是一个基于阿里云 OpenAPI 的 Claude Code Skills 集合，用于与阿里云服务进行交互。

## 项目结构

```
.
├── deploy/                           # 前端部署编排 Skill（aliyun-deploy）
│   ├── SKILL.md                      # Skill 使用文档
│   ├── reference/                    # 参考文档
│   └── scripts/                      # 部署脚本
├── domain/                           # 域名相关 Skills
│   ├── SKILL.md                      # Skill 使用文档
│   ├── .env.example                  # 环境变量模板
│   ├── reference/                    # API 定义（YML）
│   │   ├── check_domain.yml
│   │   ├── query_domainlist.yml
│   │   ├── describe_domain_records.yml
│   │   └── update_domain_record.yml
│   └── scripts/                      # Python 脚本
│       ├── check_domain.py
│       ├── query_domainlist.py
│       ├── describe_domain_records.py
│       ├── update_domain_record.py
│       └── requirements.txt
├── oss/                              # OSS 对象存储相关 Skills
│   ├── SKILL.md                      # Skill 使用文档
│   ├── .env.example                  # 环境变量模板
│   ├── reference/                    # API 定义（YML）
│   │   ├── list_buckets.yml
│   │   ├── put_bucket.yml
│   │   └── put_object.yml
│   └── scripts/                      # Python 脚本
│       ├── oss_util.py
│       ├── list_buckets.py
│       ├── put_bucket.py
│       ├── put_object.py
│       └── requirements.txt
├── cdn/                              # CDN 相关 Skills
│   ├── SKILL.md                      # Skill 使用文档
│   ├── .env.example                  # 环境变量模板
│   ├── reference/                    # API 定义（YML）
│   │   ├── describe_user_domains.yml
│   │   ├── describe_cdndomain_detail.yml
│   │   ├── describe_cdndomain_configs.yml
│   │   ├── describe_domain_cname.yml
│   │   ├── check_cdndomain_icp.yml
│   │   ├── add_cdndomain.yml
│   │   ├── batch_update_cdndomain.yml
│   │   ├── start_cdndomain.yml
│   │   └── set_cdndomain_sslcertificate.yml
│   └── scripts/                      # Python 脚本
│       ├── describe_user_domains.py
│       ├── describe_cdndomain_detail.py
│       ├── describe_cdndomain_configs.py
│       ├── describe_domain_cname.py
│       ├── check_cdndomain_icp.py
│       ├── add_cdndomain.py
│       ├── batch_update_cdndomain.py
│       ├── start_cdndomain.py
│       ├── set_cdndomain_sslcertificate.py
│       └── requirements.txt
├── sls/                              # SLS 日志服务相关 Skills
│   ├── SKILL.md                      # Skill 使用文档
│   ├── .env.example                  # 环境变量模板
│   ├── reference/                    # API 定义（YML）
│   │   ├── list_logstores.yml
│   │   └── get_log_v2.yml
│   └── scripts/                      # Python 脚本
│       ├── sls_util.py
│       ├── list_logstores.py
│       ├── get_logs_v2.py
│       └── requirements.txt
└── billing/                          # 账单相关 Skills
    └── aliyun-instance-bill/         # 实例账单查询 Skill
        ├── SKILL.md                  # Skill 使用文档
        ├── requirements.txt          # Python 依赖
        ├── .env.example              # 环境变量模板
        └── reference/                # 参考代码
            └── describe_instance_bill.py
```

## 已包含 Skills

### 1. 阿里云前端部署 (deploy/)

**aliyun-deploy** 是一个编排式 Skill，用于将前端静态构建产物部署到阿里云。它整合了域名、DNS、OSS、CDN 等能力，实现完整的一站式部署流程。

**功能特性：**
- 自动判断增量更新（仅上传+刷新）或全量部署
- 支持 OSS 静态网站托管配置
- 支持 CDN 加速域名管理与 HTTPS 证书配置
- 支持 Let’s Encrypt DNS-01 证书申请与自动续期
- 项目绑定配置（`.aliyun-deploy.json`）支持幂等续跑
- 部署后自动刷新 CDN 缓存

**核心能力：**
- 前端工程构建与产物上传
- OSS Bucket 管理与静态网站配置
- CDN 加速域名添加与配置
- 阿里云云解析 DNS 记录管理
- HTTPS 证书申请与部署

**适用场景：**
- 单页应用（SPA）静态站点部署
- 多页静态网站托管
- OSS + CDN 架构的自动化部署

**详细文档：** [deploy/SKILL.md](deploy/SKILL.md)

---

### 2. 阿里云域名 (domain/)

通过阿里云 Domain 和 Alidns OpenAPI 查询域名列表、检查域名可注册性、管理 DNS 解析记录。

**功能特性：**
- 查询账号下所有域名
- 检查域名可注册性及价格
- 列出 DNS 解析记录
- 修改 DNS 解析记录（A/CNAME/MX 等）
- 支持按域名名称搜索
- 支持按到期时间筛选（即将到期域名）
- 支持按标签、资源组筛选

**核心 API：**
- `QueryDomainList` - 查询域名列表
- `CheckDomain` - 检查域名可注册性
- `DescribeDomainRecords` - 列出 DNS 解析记录
- `UpdateDomainRecord` - 修改解析记录

**使用场景：**
- 域名资产管理
- 查询即将到期的域名
- DNS 解析排查与修改
- 域名可注册性检查

**详细文档：** [domain/SKILL.md](domain/SKILL.md)

---

### 3. 阿里云 OSS (oss/)

通过 Python SDK `alibabacloud_oss_v2` 操作阿里云 OSS：列举 Bucket、创建 Bucket、上传 Object。

**功能特性：**
- 列举当前账号下的所有 Bucket
- 创建新的存储空间（Bucket）
- 上传本地文件到 OSS
- 支持按前缀、标签筛选 Bucket
- 支持设置 ACL 权限

**核心 API：**
- `ListBuckets` - 列举 Bucket
- `PutBucket` - 创建 Bucket
- `PutObject` - 上传 Object

**使用场景：**
- OSS 资产盘点
- 自动化创建存储空间
- 部署静态资源到 OSS
- 备份文件到云端

**详细文档：** [oss/SKILL.md](oss/SKILL.md)

---

### 4. 阿里云 CDN (cdn/)

通过 Python SDK `alibabacloud_cdn20180510` 调用阿里云 CDN OpenAPI，管理加速域名。

**功能特性：**
- 查询加速域名列表与详情
- 查询域名配置信息
- 检测 CNAME 解析状态
- 查询域名备案信息
- 添加新加速域名
- 批量更新域名配置
- 启用/停用加速域名
- 设置 HTTPS 证书

**核心 API：**
- `DescribeUserDomains` - 查询用户域名列表
- `DescribeCdnDomainDetail` - 查询域名详情
- `DescribeCdnDomainConfigs` - 查询域名配置
- `DescribeDomainCname` - 检测 CNAME
- `CheckCdnDomainICP` - 查询备案信息
- `AddCdnDomain` - 添加域名
- `BatchUpdateCdnDomain` - 批量更新
- `StartCdnDomain` - 启用域名
- `SetCdnDomainSSLCertificate` - 设置证书

**使用场景：**
- CDN 域名资产管理
- 新域名接入 CDN
- HTTPS 证书配置
- CNAME 解析排查

**详细文档：** [cdn/SKILL.md](cdn/SKILL.md)

---

### 5. 阿里云 SLS (sls/)

通过 Python SDK `alibabacloud_sls20201230` 调用阿里云 SLS (Simple Log Service) API 查询日志。

**功能特性：**
- 列出指定 Project 下的所有 LogStore
- 查询指定 LogStore 中的日志
- 支持 SLS 查询语句（搜索和 SQL 分析）
- 支持时间范围查询
- 支持分页查询
- 支持 scan 模式查询大量数据

**核心 API：**
- `ListLogStores` - 列出日志库
- `GetLogsV2` - 查询日志（V2 版本）

**使用场景：**
- 查询应用日志
- 日志分析和排查问题
- 列出可用日志库
- 统计日志数据

**详细文档：** [sls/SKILL.md](sls/SKILL.md)

---

### 6. 阿里云账单 (billing/aliyun-instance-bill)

通过 Python SDK `alibabacloud_bssopenapi20171214` 调用阿里云 BSS OpenAPI，查询实例级账单。

**功能特性：**
- 支持查询最近 18 个月的账单数据
- 支持按产品类型筛选（ECS、RDS、OSS 等）
- 支持按订阅类型筛选（预付费/后付费）
- 支持月/日两种粒度查询
- 自动分页获取完整数据
- 支持实例维度或计费项维度查看

**核心 API：**
- `DescribeInstanceBill` - 查询实例级账单详情

**使用场景：**
- 月度费用对账
- 资源消费分析
- 按产品/按天统计费用
- 实例级成本追踪

**详细文档：** [billing/aliyun-instance-bill/SKILL.md](billing/aliyun-instance-bill/SKILL.md)

---

## 快速开始

### 1. 安装 Skills

你可以安装整个技能集合，也可以按需安装单个 skill。

#### 方式一：安装整个技能集合（推荐）

```bash
npx skills add https://github.com/shigzz/aliyun-skills
```

#### 方式二：按需安装单个 Skill

| Skill | 安装命令 |
|-------|----------|
| 前端部署 | `npx skills add https://github.com/shigzz/aliyun-skills --skill aliyun-deploy` |
| 域名管理 | `npx skills add https://github.com/shigzz/aliyun-skills --skill aliyun-domain-skill` |
| OSS 存储 | `npx skills add https://github.com/shigzz/aliyun-skills --skill aliyun-oss-skill` |
| CDN 加速 | `npx skills add https://github.com/shigzz/aliyun-skills --skill aliyun-cdn-skill` |
| SLS 日志 | `npx skills add https://github.com/shigzz/aliyun-skills --skill aliyun-sls-skills` |
| 实例账单查询 | `npx skills add https://github.com/shigzz/aliyun-skills --skill aliyun-instance-bill` |

### 2. 配置阿里云访问凭据

所有 Skill 都需要配置阿里云 AccessKey。支持以下方式：

**方式一：环境变量（推荐）**

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
```

**方式二：项目 .env 文件**

在对应 Skill 目录创建 `.env` 文件：

```bash
cp domain/.env.example domain/.env
# 或
cp oss/.env.example oss/.env
# 或
cp cdn/.env.example cdn/.env
# 或
cp sls/.env.example sls/.env
# 或
cp billing/aliyun-instance-bill/.env.example billing/aliyun-instance-bill/.env
```

编辑 `.env` 文件：

```dotenv
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

获取阿里云访问密钥：[阿里云文档](https://help.aliyun.com/document_detail/53045.html)

### 3. 使用 Skill

#### 方式一：作为 Claude Code Skill 使用

如果你的 Claude Code 已配置 Skills 目录，可以直接调用：

```
部署前端项目到阿里云
列出我账号下的所有域名
查询我的 OSS Bucket 列表
列出我的 CDN 加速域名
查询 SLS 日志 project 为 my-project 的日志
查询我 2024 年 3 月的阿里云账单
```

#### 方式二：直接运行 Python 脚本

各 Skill 目录下的 `scripts/` 文件夹包含可运行的示例代码：

**前端部署（编排式 Skill）：**

aliyun-deploy 是编排式 Skill，通过 Claude Code 调用时会自动协调 domain、OSS、CDN 等子 Skill 完成部署。也可直接参考各子 Skill 脚本手动执行：

**域名管理：**
```bash
cd domain/scripts
python query_domainlist.py
python check_domain.py
python describe_domain_records.py
python update_domain_record.py
```

**OSS 存储：**
```bash
cd oss/scripts
python list_buckets.py --region cn-hangzhou
python put_bucket.py --bucket my-bucket --region cn-hangzhou
python put_object.py --bucket my-bucket --key path/to/file.txt --file ./local.txt --region cn-hangzhou
```

**CDN 加速：**
```bash
cd cdn/scripts
python describe_user_domains.py
python describe_cdndomain_detail.py
python describe_domain_cname.py
```

**SLS 日志：**
```bash
cd sls/scripts
python list_logstores.py --region cn-hangzhou --project your-project
python get_logs_v2.py --region cn-hangzhou --project your-project --logstore your-logstore --recent-minutes 15
```

**账单查询：**
```bash
cd billing/aliyun-instance-bill/reference
python describe_instance_bill.py
```

## 各 Skill 详细文档

| Skill | 文档 | 说明 |
|-------|------|------|
| 前端部署 | [deploy/SKILL.md](deploy/SKILL.md) | 静态站点部署编排文档 |
| 域名管理 | [domain/SKILL.md](domain/SKILL.md) | Domain/DNS API 使用文档 |
| OSS 存储 | [oss/SKILL.md](oss/SKILL.md) | OSS API 使用文档 |
| CDN 加速 | [cdn/SKILL.md](cdn/SKILL.md) | CDN API 使用文档 |
| SLS 日志 | [sls/SKILL.md](sls/SKILL.md) | SLS 日志服务 API 使用文档 |
| 实例账单查询 | [billing/aliyun-instance-bill/SKILL.md](billing/aliyun-instance-bill/SKILL.md) | BSS 账单 API 使用文档 |

## 开发指南

### 添加新的 Skill

1. 在对应服务目录下创建新的 Skill 文件夹（编排式 Skill 如 `deploy/` 可直接放在根目录）
2. 编写 `SKILL.md` 文档，包含：
   - Skill 名称和描述
   - 前置检查（AK/SK 配置等）
   - API 使用说明
   - 参数说明
   - 示例代码
3. 在 `reference/` 目录添加 API 定义（YML）
4. 在 `scripts/` 目录添加示例脚本（编排式 Skill 可引用其他 Skill 的脚本）
5. 创建 `.env.example` 环境变量模板

### 依赖管理

每个 Skill 应包含自己的 `requirements.txt`，列出所需的阿里云 SDK：

```
# 前端部署依赖（编排式，依赖以下子 Skill）
# - aliyun-domain-skills
# - aliyun-oss-skills
# - aliyun-cdn-skills
# 以及 certbot（用于 Let's Encrypt 证书申请）

# 域名管理依赖
alibabacloud_domain20180129>=1.0.0
alibabacloud_alidns20150109>=1.0.0

# OSS 依赖
alibabacloud_oss_v2>=1.0.0

# CDN 依赖
alibabacloud_cdn20180510>=1.0.0

# SLS 日志依赖
alibabacloud_sls20201230>=1.0.0

# 账单查询依赖
alibabacloud_bssopenapi20171214>=1.0.0

# 通用依赖
alibabacloud_credentials>=1.0.0
alibabacloud_tea_openapi>=1.0.0
alibabacloud_tea_util>=1.0.0
python-dotenv>=1.0.0
```

## 安全注意事项

1. **切勿将 AK/SK 提交到代码仓库**，使用 `.env` 文件并在 `.gitignore` 中排除
2. 建议使用 RAM 子账号，并授予最小必要权限
3. 定期轮换 AccessKey
4. 生产环境建议使用 [无 AK 方式](https://help.aliyun.com/document_detail/378659.html) 调用 API

## 相关资源

- [阿里云 API 门户](https://api.aliyun.com/)
- [阿里云 SDK 文档](https://help.aliyun.com/document_detail/53090.html)
- [Domain OpenAPI 文档](https://help.aliyun.com/document_detail/42875.html)
- [OSS 开发者文档](https://help.aliyun.com/zh/oss/)
- [CDN OpenAPI 文档](https://help.aliyun.com/document_detail/27152.html)
- [SLS OpenAPI 文档](https://help.aliyun.com/document_detail/29007.html)
- [BSS OpenAPI 文档](https://help.aliyun.com/document_detail/100392.html)

## 许可证

MIT License
