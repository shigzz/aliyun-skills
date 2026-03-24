# 阿里云 OpenAPI Skills 集合

这是一个基于阿里云 OpenAPI 的 Claude Code Skills 集合，用于与阿里云服务进行交互。

## 项目结构

```
.
├── billing/                          # 账单相关 Skills
│   └── aliyun-instance-bill/         # 实例账单查询 Skill
│       ├── SKILL.md                  # Skill 使用文档
│       ├── requirements.txt          # Python 依赖
│       ├── .env.example              # 环境变量模板
│       └── reference/                # 参考代码
│           └── describe_instance_bill.py
├── domain/                           # 域名相关 Skills
│   ├── SKILL.md                      # 域名查询 Skill 文档
│   ├── .env.example                  # 环境变量模板
│   ├── scripts/                      # Python 脚本
│   │   ├── query_domainlist.py       # 域名列表查询
│   │   ├── check_domain.py           # 域名检查
│   │   └── requirements.txt          # Python 依赖
│   └── reference/                    # 工作流定义
│       ├── query_domainlist.yml
│       └── check_domain.yml
└── log/                              # 日志服务相关 Skills
    ├── SKILL.md                      # SLS 日志查询 Skill 文档
    └── reference/                    # 参考代码
        ├── list_logstores.py
        ├── list_logstores.yml
        ├── get_logs_v2.py
        └── get_logs_v2.yml
```

## 已包含 Skills

### 1. 阿里云实例账单查询 (billing/aliyun-instance-bill)

通过阿里云 BSS OpenAPI 查询实例级账单信息。

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

---

### 2. 阿里云域名查询 (domain/)

通过阿里云 Domain OpenAPI 查询当前账号下的域名列表和域名详情。

**功能特性：**
- 查询账号下所有域名
- 查询单个域名详细信息
- 支持按域名名称搜索
- 支持按到期时间筛选（即将到期域名）
- 支持按注册时间筛选
- 支持按域名状态筛选（急需续费/赎回）
- 支持按资源组、标签筛选
- 支持排序（注册时间/到期时间）

**核心 API：**
- `QueryDomainList` - 查询域名列表
- `QueryDomainByDomainName` - 查询域名详情

**使用场景：**
- 域名资产管理
- 查询即将到期的域名
- 按条件筛选域名
- 域名信息核对

---

### 3. 阿里云 SLS 日志查询 (log/)

通过阿里云 SLS (Simple Log Service) API 查询日志。

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

## 快速开始

### 1. 安装

使用 Claude Code 的 skills 命令安装：

```bash
npx skills add https://github.com/shigzz/aliyun-skills
```

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
cp billing/aliyun-instance-bill/.env.example billing/aliyun-instance-bill/.env
# 或
cp domain/.env.example domain/.env
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
查询我 2024 年 3 月的阿里云账单
列出我账号下的所有域名
查询 SLS 日志 project 为 my-project 的日志
```

#### 方式二：直接运行 Python 脚本

各 Skill 目录下的 `reference/` 文件夹包含可运行的示例代码：

**账单查询：**
```bash
cd billing/aliyun-instance-bill/reference
python describe_instance_bill.py
```

**域名查询：**
```bash
cd domain/scripts
python query_domainlist.py
python check_domain.py
```

**日志查询：**
```bash
cd log/reference
python list_logstores.py
python get_logs_v2.py
```

## 各 Skill 详细文档

| Skill | 文档 | 说明 |
|-------|------|------|
| 实例账单查询 | [billing/aliyun-instance-bill/SKILL.md](billing/aliyun-instance-bill/SKILL.md) | BSS 账单 API 使用文档 |
| 域名查询 | [domain/SKILL.md](domain/SKILL.md) | Domain API 使用文档 |
| SLS 日志查询 | [log/SKILL.md](log/SKILL.md) | SLS 日志服务 API 使用文档 |

## 开发指南

### 添加新的 Skill

1. 在对应服务目录下创建新的 Skill 文件夹
2. 编写 `SKILL.md` 文档，包含：
   - Skill 名称和描述
   - 前置检查（AK/SK 配置等）
   - API 使用说明
   - 参数说明
   - 示例代码
3. 在 `reference/` 目录添加参考代码
4. 创建 `.env.example` 环境变量模板

### 依赖管理

每个 Skill 应包含自己的 `requirements.txt`，列出所需的阿里云 SDK：

```
# 账单查询依赖
alibabacloud_bssopenapi20171214>=1.0.0

# 域名查询依赖
alibabacloud_domain20180129>=1.0.0

# 日志查询依赖
alibabacloud_sls20201230>=1.0.0

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
- [BSS OpenAPI 文档](https://help.aliyun.com/document_detail/100392.html)
- [Domain OpenAPI 文档](https://help.aliyun.com/document_detail/42875.html)
- [SLS OpenAPI 文档](https://help.aliyun.com/document_detail/29007.html)

## 许可证

MIT License
