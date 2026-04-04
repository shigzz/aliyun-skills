---
name: aliyun-deploy
description: >-
  编排将前端静态构建产物部署到阿里云（OSS + CDN）。**域名、Bucket 必须由用户指定**，Agent 仅查询展示供用户选择；支持全量部署与增量更新（上传+刷新）。默认采用「OSS 私有 Bucket + CDN 私有回源」安全模式。流程含 CNAME/TXT 解析、Let's Encrypt 证书配置、缓存刷新。
  依赖 aliyun-domain/oss/cdn skills；遇权限不足立即停止。
---

## 适用场景

静态站点（SPA 或多页）通过 **阿里云 OSS 存储 + CDN 加速** 提供 **HTTPS** 访问。

**资源范围**：域名、DNS 解析、OSS、CDN 均在阿里云同一账号下。若域名托管在第三方，需自行映射 DNS 步骤。

## 依赖

| 能力 | 路径 |
|------|------|
| 域名/DNS | [aliyun-domain-skills/SKILL.md](aliyun-domain-skills/SKILL.md) |
| OSS | [aliyun-oss-skills/SKILL.md](aliyun-oss-skills/SKILL.md) |
| CDN | [aliyun-cdn-skills/SKILL.md](aliyun-cdn-skills/SKILL.md) |

**环境**：Node.js（构建）、Python 3（调用脚本）、certbot（申请证书）。

执行前确保已安装各 skill 的 `requirements.txt`。

## 前置检查

1. **凭证**：检查环境变量 `ALIBABA_CLOUD_ACCESS_KEY_ID/SECRET`，或项目根目录 `.env`。
2. **权限**：需 OSS（读写 Bucket/对象）、CDN（域名管理/证书/刷新）权限；403 报错时立即停止，待用户补全 RAM 策略后再继续。

## 项目配置（`.aliyun-config.json`）

部署信息写入项目根目录，用于幂等续跑。支持两种格式：

### 单项目配置（对象格式）

```json
{
  "version": 1,
  "domain_apex": "example.com",
  "cdn_domain": "www.example.com",
  "oss_bucket": "my-app-static",
  "oss_region": "oss-cn-hangzhou",
  "cdn_cname_target": "xxx.w.kunlunsl.com",
  "origin_mode": "private_with_cdn_auth",
  "last_deploy_at": "2026-03-24T12:00:00Z"
}
```

### 多项目配置（数组格式）

支持在同一仓库中管理多个部署目标（如多环境或多应用）：

```json
[
  {
    "project": "my-app-prod",
    "version": 1,
    "domain_apex": "example.com",
    "cdn_domain": "www.example.com",
    "oss_bucket": "my-app-prod",
    "oss_region": "oss-cn-hangzhou",
    "cdn_cname_target": "xxx.w.kunlunsl.com",
    "origin_mode": "private_with_cdn_auth",
    "last_deploy_at": "2026-03-24T12:00:00Z"
  },
  {
    "project": "my-app-staging",
    "version": 1,
    "domain_apex": "example.com",
    "cdn_domain": "staging.example.com",
    "oss_bucket": "my-app-staging",
    "oss_region": "oss-cn-hangzhou",
    "cdn_cname_target": "yyy.w.kunlunsl.com",
    "origin_mode": "private_with_cdn_auth",
    "last_deploy_at": "2026-03-24T10:00:00Z"
  }
]
```

**字段说明**：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `project` | string | **多项目时必需** | 项目标识名，用于区分不同配置 |
| `version` | int | 是 | 配置格式版本，当前为 1 |
| `domain_apex` | string | 是 | 根域名，用于 DNS 解析 |
| `cdn_domain` | string | 是 | CDN 加速域名（完整主机名） |
| `oss_bucket` | string | 是 | OSS Bucket 名称 |
| `oss_region` | string | 是 | OSS 区域，如 `oss-cn-hangzhou` |
| `cdn_cname_target` | string | 是 | CDN 分配的 CNAME 目标地址 |
| `origin_mode` | string | 否 | 源站模式：`private_with_cdn_auth`（默认私有回源）或 `public` |
| `last_deploy_at` | string | 否 | ISO 8601 格式最后部署时间 |

### 增量更新

- **对象格式**：若配置存在且字段完整（Bucket、region、CDN 域名等），本次仅执行：**构建 → 上传 OSS → 刷新 CDN**
- **数组格式**：提示用户选择要部署的项目（按 `project` 字段区分），选定后仅更新该项目配置

若用户要求更换域名/Bucket/CDN/证书，或新增项目配置，则走完整流程。

## 用户确认项（Agent 禁止代决）

| 类别 | 确认内容 |
|------|----------|
| 域名 | 部署域名、证书覆盖的 FQDN |
| OSS | Bucket 名称、region、上传路径前缀 |
| CDN | 加速域名（完整主机名） |
| 安全 | 私有 Bucket + CDN 回源（默认）或公开读 |

**流程**：查询账号内已有资源 → 展示列表 → 用户选定 → 执行。

## 主流程

### 1. 域名
- 使用 domain-skill 查询账号域名列表
- 用户选定后，后续 CNAME/TXT 记录添加至该域名的云解析 DNS

### 2. OSS Bucket
- 使用 oss-skill 查询/创建 Bucket
- **默认私有 ACL**，配合 CDN 私有回源
- 开启静态网站：默认首页 `index.html`，404 页同首页（SPA）

### 3. 构建与上传
- 执行构建（`npm run build` 等）
- 上传产物到 Bucket 指定路径，确保 `index.html` 在根路径
- **部署后刷新 CDN** 缓存

### 4. CDN 加速域名
- 使用 cdn-skill 添加/配置加速域名
- **业务类型**：`web`（图片小文件）
- **源站**：OSS 域名，开启私有回源
- **根路径**：确保访问 `/` 返回 `index.html`
- 添加前检查 ICP 备案（国内加速）

### 5. DNS 配置

**5A — CNAME 接入**
- 获取 CDN 分配的 CNAME 目标
- 云解析 DNS 添加 CNAME 记录指向该目标

**5B — 证书验证（DNS-01）**
- certbot 申请：`certbot certonly --manual --preferred-challenges dns -d <域名>`
- 按提示添加 `_acme-challenge` TXT 记录
- 验证通过后获取 `fullchain.pem` 和 `privkey.pem`

### 6. HTTPS 配置
- 使用 cdn-skill 上传证书并启用 HTTPS
- 建议开启强制 HTTPS、HTTP/2
- **证书有效期 90 天**，到期前需重新申请

### 7. 启用与验收
- 启用加速域名（若处于停用状态）
- 访问 `https://<加速域名>/` 验证根路径返回 `index.html`
- 检查 CNAME、证书链无告警

### 8. 收尾
- 更新 `.aliyun-config.json`（对象格式直接更新；数组格式更新对应项目条目，或追加新配置）
- 返回 HTTPS 访问地址，提示证书续期与后续发版流程（上传+刷新）

## 故障排查

| 现象 | 原因 | 处理 |
|------|------|------|
| 403 | RAM 权限不足 | 立即停止，补全策略 |
| 403 | 私有 Bucket 回源配置错误 | 检查 OSS 权限与 CDN 源站配置 |
| 访问 `/` 404 | 根路径未映射到 `index.html` | 检查 OSS 默认首页配置与文件位置 |
| 页面空白 | SPA 路由 404 | OSS 错误页设为 `index.html` |
| 旧资源 | CDN 缓存未刷新 | 执行缓存刷新 |
| 证书错误 | 证书与域名不匹配 | 检查 SAN、证书链完整性 |
| CNAME 不生效 | DNS 传播延迟 | `dig`/`nslookup` 核对 |

## 计费提示

可能产生费用：OSS 存储/请求、CDN 流量/HTTPS、域名续费。Let’s Encrypt 证书免费。
