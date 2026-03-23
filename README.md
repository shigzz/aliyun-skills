# 阿里云 OpenAPI Skills 集合

这是一个基于阿里云 OpenAPI 的 Claude Code Skills 集合，用于与阿里云服务进行交互。

## 项目结构

```
.
├── billing/                          # 账单相关 Skills
│   ├── aliyun-instance-bill/         # 实例账单查询 Skill
│   │   ├── SKILL.md                  # Skill 使用文档
│   │   ├── requirements.txt          # Python 依赖
│   │   └── reference/                # 参考代码
│   │       └── describe_instance_bill.py
│   └── .claude/skills/aliyun-billing/# Claude Code Skill 格式
│       ├── skill.json                # Skill 定义文件
│       ├── main.py                   # 主程序入口
│       └── requirements.txt          # 依赖配置
└── .env.example                      # 环境变量模板
```

## 已包含 Skills

### 1. 阿里云实例账单查询 (aliyun-billing)

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

## 快速开始

### 1. 配置阿里云访问凭据

复制环境变量模板并填写你的 AK/SK：

```bash
cp billing/.env.example billing/.env
```

编辑 `.env` 文件：

```dotenv
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

获取阿里云访问密钥：[阿里云文档](https://help.aliyun.com/document_detail/53045.html)

### 2. 安装依赖

```bash
# 进入对应的 Skill 目录
cd billing/aliyun-instance-bill

# 安装依赖
pip install -r requirements.txt
```

### 3. 使用 Skill

#### 方式一：作为 Claude Code Skill 使用

如果你的 Claude Code 已配置 Skills 目录，可以直接调用：

```
查询我 2024 年 3 月的阿里云账单
```

#### 方式二：直接运行 Python 脚本

```bash
cd billing/.claude/skills/aliyun-billing

# 查询指定账期账单
python main.py --billing-cycle 2024-03

# 查询指定产品（如 ECS）的后付费账单
python main.py --billing-cycle 2024-03 --product-code ecs --subscription-type PayAsYouGo

# 按天查询特定日期的账单
python main.py --billing-cycle 2024-03 --granularity DAILY --billing-date 2024-03-01

# 按计费项维度查询，限制最多查询 5 页
python main.py --billing-cycle 2024-03 --is-billing-item true --max-pages 5
```

### 4. 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--billing-cycle` | string | 是 | 账期，格式 YYYY-MM，如 `2024-03` |
| `--product-code` | string | 否 | 产品代码，如 `ecs`、`rds`、`oss` |
| `--subscription-type` | string | 否 | 订阅类型：`Subscription`(预付费) / `PayAsYouGo`(后付费) |
| `--is-billing-item` | boolean | 否 | 是否按计费项维度，默认 `false` |
| `--granularity` | string | 否 | 查询粒度：`MONTHLY`(月) / `DAILY`(日) |
| `--billing-date` | string | 否 | 账单日期，格式 YYYY-MM-DD，Granularity=DAILY 时必填 |
| `--page-size` | integer | 否 | 每页数量，默认 100，最大 300 |
| `--max-pages` | integer | 否 | 最大查询页数，默认 0 表示查询所有 |
| `--is-hide-zero-charge` | boolean | 否 | 是否隐藏零费用账单，默认 `false` |

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
4. （可选）在 `.claude/skills/` 创建 Claude Code Skill 格式文件

### 依赖管理

每个 Skill 应包含自己的 `requirements.txt`，列出所需的阿里云 SDK：

```
alibabacloud_bssopenapi20171214>=1.0.0
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

## 许可证

MIT License
