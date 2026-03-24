---
name: aliyun-deploy
description: >-
  编排将前端静态构建产物部署到阿里云：假设域名、云解析 DNS、OSS、CDN 等云资源均在同一阿里云账号下。**部署域名、CDN 加速域名、OSS Bucket 必须由用户指定，Agent 不得擅自确定**；可先查询账号内现有资源或创建新资源作为候选，**列出供用户选择后再执行**。若 `.aliyun-deploy.json` 已记录完整部署上下文，可判定为**增量更新**，仅上传 OSS 并刷新 CDN。遇 OpenAPI **权限不足**须**立即停止**，待用户配置 RAM 后再继续。流程含 CNAME 与证书 TXT 分离、Let’s Encrypt（certbot DNS-01）上传至 CDN、缓存刷新与验收。
  依赖本仓库 aliyun-domain-skills、aliyun-oss-skills、aliyun-cdn-skills 的能力说明与脚本；执行 API 前须完成凭证检查。
---

## 资源范围说明（重要）

本 SKILL 默认 **域名、DNS 解析、OSS、CDN 及相关云资源均在阿里云**（同一账号或已明确归属的阿里云资源），便于用 OpenAPI/控制台统一操作与排错：

- **域名**：在阿里云注册或由用户转入后在 **阿里云域名** 控制台管理（与 [aliyun-domain-skills](aliyun-domain-skills/SKILL.md) 查询范围一致）。
- **解析**：在 **阿里云云解析 DNS** 为加速域名配置记录（CDN 所需 **CNAME**、Let’s Encrypt 所需 **`_acme-challenge` TXT** 等均在此添加）。
- **存储与加速**：**对象存储 OSS**、**内容分发网络 CDN** 均为阿里云产品。

若域名或解析托管在第三方，需自行将下列 DNS 步骤映射到对应 DNS 控制台；本 SKILL 仍以阿里云侧产品与 API 为主叙述。

## 适用场景与非目标

**适用**：单页应用（SPA）或多页静态站点，构建产出为 HTML/CSS/JS 等静态文件，通过 **阿里云 OSS 存放 + 阿里云 CDN 加速** 对外提供 **HTTPS** 访问。

**非目标**（本 SKILL 不覆盖）：ECS 自建 Nginx、容器/K8s 发布、服务端渲染宿主部署、仅 OSS 公网 Endpoint 直连且无 CDN 的复杂替代方案（可按需裁剪流程）。

## 依赖的子 SKILL 与工具

**本仓库内**请直接阅读并遵循各目录下的 `SKILL.md`（路径相对 skills 根目录）：

| 能力 | 路径 |
|------|------|
| 域名列表与资产 | [aliyun-domain-skills/SKILL.md](aliyun-domain-skills/SKILL.md) |
| OSS Bucket / 上传 | [aliyun-oss-skills/SKILL.md](aliyun-oss-skills/SKILL.md) |
| CDN 域名、CNAME 检测、备案、证书、启停 | [aliyun-cdn-skills/SKILL.md](aliyun-cdn-skills/SKILL.md) |

**环境与工具**：

- **Node.js**：能执行 `npm run build` / `pnpm build` / `yarn build`（以项目为准）。
- **certbot**：用于 Let’s Encrypt **DNS-01** 申请证书（需本机或 CI 可执行；TXT 默认在 **阿里云云解析 DNS** 控制台添加，与上述资源范围一致）。
- **Python 3**（调用本仓库 `aliyun-*-skills/scripts/` 时）：按各 skill 安装 `requirements.txt`，例如：
  - `pip install -r aliyun-cdn-skills/scripts/requirements.txt`
  - `pip install -r aliyun-oss-skills/scripts/requirements.txt`

**从外部 registry 安装**（若使用 `npx skills add` 等）：以发布方文档中的 **skill id** 为准；名称可能与本地目录 `aliyun-*-skills` 不一致。

## 凭证检查（必须首先执行）

在调用任何阿里云 OpenAPI 或运行上述脚本前，必须先确认 AccessKey 已配置。

**摘要**：

1. 检查环境变量 `ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`。
2. 若未设置，检查项目根目录 `.env` 中同名变量。
3. 未通过检查则**停止**，提示用户配置后再继续。

## RAM 权限提示

执行本流程至少需要（或等价自定义策略）对 **OSS** 与 **CDN** 的读写能力；若通过 API 管理解析，还需 **云解析 DNS** 等相关权限。例如：

- OSS：列举/创建 Bucket、上传 Object、（按需）静态网站与 Bucket 策略相关权限。
- CDN：查询域名、添加/更新加速域名、配置 HTTPS 证书、启用域名、刷新缓存等。
- 域名 / DNS：查询域名列表、解析记录增删改（按你是否自动化 DNS 而定；手动在控制台操作时可不授予 DNS API）。

生产环境建议使用 **最小权限** RAM 用户；具体 Action 以官方文档与控制台策略生成器为准。

### OpenAPI 报权限不足时

若在调用 **OpenAPI** 或运行本仓库脚本时出现 **权限不足**、**拒绝访问**、**RAM 策略未授权** 等报错（常见如 HTTP **403**、错误码含 `Forbidden`、`NoPermission`、`AccessDenied` 等，具体以响应为准）：

1. **立即停止**当前部署任务的后续步骤，**不得**假定可忽略或仅靠重试绕过。
2. 向用户说明 **失败的接口/操作**、**错误码与关键信息**，并提示在 **RAM 访问控制** 中为当前使用的 AK 对应身份（主账号或 RAM 用户/角色）**补齐策略**后重试。
3. **待用户明确反馈已配置好权限**后，再从合适步骤继续（由用户决定是否从失败点续跑或重来）。

## 计费与风险

部署可能产生：**OSS 存储与请求费用**、**CDN 流量与 HTTPS 费用**、**域名续费**。Let’s Encrypt 签发免费，但 Agent/用户需自行承担 certbot 与 DNS 操作成本。变更前向用户说明可能产生费用；生产变更建议先在测试域名验证。

## 项目绑定配置（`.aliyun-deploy.json`）

将本次部署绑定的信息写入**项目根目录**下的 `.aliyun-deploy.json`（仅本机/仓库是否提交由团队规范决定；勿提交密钥）。

**说明**：历史文档或 [CLAUDE.md](../CLAUDE.md) 中若出现 `.aliyun-cdn-config.json`，表示偏 CDN 单能力场景；**本编排 SKILL 以 `.aliyun-deploy.json` 为准**，可包含 OSS 与域名等全量字段。

**建议字段**（可按实际增减）：

```json
{
  "version": 1,
  "domain_apex": "example.com",
  "cdn_domain": "www.example.com",
  "oss_bucket": "my-app-static",
  "oss_region": "oss-cn-hangzhou",
  "oss_endpoint": "oss-cn-hangzhou.aliyuncs.com",
  "cdn_cname_target": "xxx.w.kunlunsl.com",
  "origin_mode": "private_with_cdn_auth",
  "last_deploy_at": "2026-03-24T12:00:00Z",
  "notes": "可选备注"
}
```

Agent 应在关键步骤后更新该文件，便于下次幂等续跑。

### 增量更新判定

**含义**：仅 **上传 OSS** 与 **刷新 CDN**，不重做域名/CDN/DNS/证书等基建。

若项目根目录已存在 **`.aliyun-deploy.json`**，且从中读取到的字段表明 **上一轮全量部署已完成、资源齐备**（至少包含用户曾确认的 **`oss_bucket`**、**`oss_region`**（及可推导或已写的 **`oss_endpoint`**）、**`cdn_domain`**、**`cdn_cname_target`**、**`origin_mode`** 等关键信息，并与本次用户意图一致），则可将本次任务判定为 **增量更新**：

- **跳过**：§1 域名开通与选择、§2 新建 Bucket、§4 新增加速域名、§5 DNS/CNAME/证书 TXT、§6 HTTPS 初次配置等「基建」步骤（除非用户明确要求变更其中任一项或文件明显过期）。
- **执行**：**前端构建** → 按文件中记录的 Bucket / 路径前缀将产物 **上传 OSS** → 对相应 URL 或目录执行 **CDN 刷新/预热**（见 §3）→ 更新 **`last_deploy_at`**。

**注意**：若用户要求改域名、换 Bucket、重建 CDN 或证书，则 **不得** 套用增量路径，须按完整主流程并重新确认 [须向用户确认的信息](#须向用户确认的信息)。可选：用 OpenAPI **快速核对** 当前账号下该 Bucket、该加速域名仍存在且与文件一致，再执行上传与刷新。

## 前端工程检查（构建前）

1. 确认是静态前端项目，**构建命令成功**（如 `npm run build`），产出目录明确（常见 `dist/`、`build/`、`out/`）。
2. **SPA**：确认 `base` / `publicPath` / `assetPrefix` 与最终访问路径一致；路由为 History 模式时，需 **404 回退到 `index.html`**（见下文 OSS 静态网站或 CDN 自定义错误页）。
3. 若静态页需调用**跨域 API**，评估 OSS/CORS 与 CDN 响应头（本仓库 OSS skill 能力与控制台文档）。

## 须向用户确认的信息

### 硬性规则（用户指定，禁止代决）

以下三项 **只能由用户明确指定**，Agent **不得**根据项目名、猜测或「默认值」擅自选定：

1. **部署所用域名**（含 apex / 业务域、证书涉及的 FQDN）。
2. **CDN 加速域名**（完整主机名，如 `www.example.com`）。
3. **OSS Bucket**（名称与 **region**；以及是否使用某前缀路径上传）。

**允许的做法**：调用 API **查询**账号下已有域名列表、Bucket 列表、CDN 加速域名列表，**展示给用户**；若用户需要新建，可先按规范 **创建** Bucket 或 **添加** CDN 域名等，使新资源出现在候选中，但 **仍须用户从「现有列表 + 新建结果」中明确选定** 后再继续绑定、上传或切流量。**禁止**在未获用户点名确认的情况下，自行选用某一域名、某一加速域名或某一 Bucket 作为部署目标。

**勿擅自假定**：任何创建、绑定或可能影响生产访问的变更，均须在用户确认后进行；**不得**在未确认时把生产流量指到新资源或误绑他人域名。

### 建议与用户逐项确认的内容

| 类别 | 须询问或确认的内容 |
|------|-------------------|
| 域名 | 使用哪几个域名（如 apex `example.com`、是否含 `www`）；注册/转入是否在阿里云完成；证书要覆盖的 **FQDN 列表**（与 certbot `-d` 一致）。 |
| CDN | **加速域名**（完整主机名）；**从已有加速域名中选**还是 **新建后再由用户确认**；源站是否与用户选定的 OSS 一致。 |
| OSS | **Bucket 名称**与 **region**；**从已有 Bucket 中选**还是 **新建后再由用户确认**；静态文件上传的**路径前缀**（根目录或 `prefix/`）。 |
| 安全与访问 | **公开读**还是 **私有 Bucket + CDN 私有回源**（见 §2）；是否接受由此带来的权限与费用影响。 |

用户确认后，将结果写入 `.aliyun-deploy.json` 并在后续步骤中保持一致；若用户中途变更，须重新确认并更新配置。

## 主流程（有序）

**入口分支**：开始前读取 **`.aliyun-deploy.json`**。若满足上文 **[增量更新判定](#增量更新判定)**，且用户本次仅为发版/更新静态资源，则 **直接从 [§3 构建与上传](#3-构建与上传) 执行**（上传 OSS + 刷新 CDN，并更新 `last_deploy_at`），无需重复走域名/CDN/DNS/证书全流程。

否则，以下各步均在 **[须向用户确认的信息](#须向用户确认的信息)** 已落实的前提下执行（全量或配置变更）。

### 1. 域名

- **部署所用域名以用户在 [须向用户确认的信息](#须向用户确认的信息) 中的指定为准**；可先列举账号内域名供用户选择，或引导注册/转入后再由用户确认，**不得**代用户选定域名。
- 使用 [aliyun-domain-skills](aliyun-domain-skills/SKILL.md) 查看 **当前阿里云账号下** 域名列表，**由用户从列表中选定或确认**拟部署域名（与上文询问结果一致）。
- 若无合适域名，引导在 [阿里云域名注册](https://wanwang.aliyun.com/domain) 注册或 **将域名转入阿里云**，以便与 **云解析 DNS**、CDN、备案等在同一生态闭环。
- 后续 **CNAME / TXT** 均在 **阿里云云解析 DNS** 中为该域名配置（参见 §5）。

### 2. OSS Bucket

- **Bucket 与 region 以用户在 [须向用户确认的信息](#须向用户确认的信息) 中的指定为准**；可先列举已有 Bucket 供用户选择，或在用户同意新建时创建 Bucket，**仍须用户最终确认目标 Bucket 与 region** 后再上传。Bucket 名须符合 OSS 全局命名规范（小写、长度等见 OSS 文档）。
- 列举、创建与上传等操作参考 aliyun-oss-skills。
- **安全模型（必须先与用户确认）**：
  - **公开静态站（常见）**：Bucket 或对象对匿名读开放（或经 Bucket 策略允许 `GetObject`），CDN 回源可拉取对象。
  - **私有 Bucket + CDN**：需配置 **私有回源 / OSS 授权给 CDN** 等，错误配置会导致 **403**；不要将「私有回源」当作唯一默认项。

### 3. 构建与上传

- 执行项目构建；将产物 **同步上传到** 目标 Bucket 路径（如根目录或 `prefix/`）。
- **静态网站托管**（若使用 OSS 静态网站域名或需默认首页/错误页）：在 OSS 侧开启静态网站、设置 **默认首页**（`index.html`）与 **404 页**（SPA 常设为同一 `index.html`）。
- **部署后刷新**：上传完成后，对 CDN 执行 **刷新/预热**（如 RefreshObjectCaches 等，见 CDN OpenAPI/控制台），否则用户可能长期看到旧资源。

### 4. CDN 加速域名

- **加速域名以用户在 [须向用户确认的信息](#须向用户确认的信息) 中的指定为准**；可先列举已有加速域名或按用户要求新增域名，再经用户选定后配置。
- 使用已有加速域名或 **添加加速域名**（参考 [aliyun-cdn-skills](aliyun-cdn-skills/SKILL.md) 中 AddCdnDomain 等）。
- **业务类型（必设）**：新增加速域名时，控制台 **业务类型** 请选择 **「图片小文件」**；调用 OpenAPI 时参数 **`CdnType` 填 `web`**（与静态前端 HTML/JS/CSS 及小体积资源匹配）。勿默认选「大文件下载」「视音频点播」等，除非用户明确有对应场景。字段说明见 [add_cdndomain.yml — CdnType](aliyun-cdn-skills/reference/add_cdndomain.yml)。
- **源站**：选 OSS 域名，回源 HOST、协议等与控制台要求一致。
- **中国内地加速**：添加前用 **CheckCdnDomainICP**（见 aliyun-cdn-skills）等确认 **ICP 备案** 要求；海外加速按产品与地域策略处理。
- 用户指定加速域名形态（如 `www.example.com` 或子域）；与 OSS 公共读/私有回源选择一致。

### 5. DNS：CNAME（加速接入）与 TXT（证书验证）分离

**5A — CDN 接入（必做）**

- 在 **阿里云 CDN** 控制台或 API 取得该加速域名的 **CNAME 目标**（形如 `*.w.kunlun*.com`，以实际为准）。
- 在 **阿里云云解析 DNS** 中为加速域名添加 **CNAME** 记录，**指向上述 CDN CNAME**。
- 使用 [DescribeDomainCname](aliyun-cdn-skills/SKILL.md) 等检测是否解析生效。

**5B — Let’s Encrypt DNS 验证（certbot DNS-01）**

- Let’s Encrypt **DNS-01** 需在 **云解析 DNS** 中添加 **`_acme-challenge.<your-domain>` 的 TXT** 记录；**不要**与 5A 的 CNAME 混为一步说明。
- 若 apex 与 `www` 均要证书，需按 certbot 提示为 **每个 `-d` 主机名** 添加对应 TXT（或合并在同一次申请中由 certbot 依次提示）。

### 6. HTTPS：Let’s Encrypt + certbot → CDN

1. 安装 `certbot`（以操作系统包管理器或官方文档为准）。
2. 使用 **manual + DNS** 申请，示例（按实际 FQDN 替换；多个主机名用多次 `-d`）：

   ```bash
   sudo certbot certonly --manual --preferred-challenges dns \
     -d www.example.com -d example.com
   ```

3. 按 certbot 提示在 **阿里云云解析 DNS** 添加 **`_acme-challenge` 的 TXT**，等待传播后回车完成验证。
4. 取得 `fullchain.pem` 与 `privkey.pem`，通过 CDN API **上传并启用 HTTPS**（[SetCdnDomainSSLCertificate](aliyun-cdn-skills/SKILL.md) 等，见 aliyun-cdn-skills）。
5. 明确告知用户证书 **有效期**（通常 90 天）：需在到期前 **重新执行 DNS-01**，或使用配置了 **云解析 DNS 等自动 DNS 插件** 的 `certbot renew`；纯手动模式下续期仍需按提示在 **云解析 DNS** 更新 TXT。

配置完成后建议开启 **强制 HTTPS**、**HTTP/2**（以 CDN 控制台选项为准）。

### 7. CDN 行为与缓存（部署后检查）

- **缓存**：HTML 宜较短缓存或需随刷新失效；带 **hash** 的 JS/CSS 可较长缓存。
- **压缩**：开启 Gzip/Brotli（若产品支持）。
- 再次 **刷新热点 URL**（首页、`index.html`、重要静态资源）以确保立即生效。

### 8. 启用与验收

- 若域名为停用状态，执行 **启用加速域名**（StartCdnDomain，见 aliyun-cdn-skills）。
- **验收**：浏览器访问 `https://<加速域名>`；可选 `curl -I` 检查状态码与跳转；CNAME 与证书链无告警。

### 9. 收尾

- 更新 `.aliyun-deploy.json`。
- 向用户返回 **HTTPS 访问地址**，并提示 **证书续期**、**费用**与 **后续发版时重新上传 OSS + 刷新 CDN**。

## 故障排查简表

| 现象 | 可能原因 | 处理方向 |
|------|----------|----------|
| OpenAPI 403 / Forbidden / NoPermission 等 | 当前 AK 对应 RAM 策略未授权该 API | **立即停止任务**；告知用户补全 RAM 权限，**待用户配置完成后再继续**（见上文「OpenAPI 报权限不足时」） |
| 403 | Bucket 私有且未正确配置 CDN 回源鉴权 / 策略过严 | 检查 OSS 权限与 CDN 源站配置 |
| 页面空白或路由 404 | SPA 未将 404 指回 `index.html` | OSS 静态网站错误页或 CDN 自定义页 |
| 样式/脚本报错旧版本 | CDN 缓存未失效 | 刷新/预热对应 Object 或目录 |
| 证书错误 | 证书与域名不匹配或未部署完整链 | 检查 SAN、fullchain、CDN 证书配置 |
| CNAME 不生效 | DNS 传播延迟或记录错误 | 用 DescribeDomainCname 与 dig/nslookup 核对 |

