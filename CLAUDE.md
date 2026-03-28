# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Skills** collection for Alibaba Cloud (阿里云) services. Each skill provides Python-based scripts to interact with Alibaba Cloud OpenAPIs for domain management, OSS, CDN, SLS (log service), and billing.

## Skill Structure

Each skill follows a consistent directory pattern:

```
skill-name/
├── SKILL.md              # Skill documentation with API usage, parameters, examples
├── .env.example          # Environment variable template
├── reference/            # API contract definitions (YML format)
│   └── *.yml             # OpenAPI parameter/response schemas
└── scripts/              # Executable Python scripts
    ├── requirements.txt  # Python dependencies for this skill
    └── *.py              # Script implementations
```

## Skills Overview

| Skill | Path | Purpose |
|-------|------|---------|
| aliyun-deploy | `deploy/` | Orchestration skill for frontend static site deployment (coordinates domain, OSS, CDN) |
| aliyun-domain-skill | `domain/` | Domain registration, DNS records management |
| aliyun-oss-skill | `oss/` | OSS bucket operations, object upload |
| aliyun-cdn-skill | `cdn/` | CDN domain management, SSL certificates |
| aliyun-sls-skills | `log/` (published as `sls/`) | SLS log service queries |
| aliyun-billing-skills | `billing/` | Instance-level billing queries |

## Credential Configuration

All skills require Alibaba Cloud AccessKey credentials. Configuration priority:

1. Environment variables: `ALIBABA_CLOUD_ACCESS_KEY_ID`, `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
2. `.env` file in the skill directory (copied from `.env.example`)

Scripts follow this credential loading pattern:
```python
# Check env vars first, fall back to .env file via python-dotenv
access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "").strip()
if not access_key_id:
    load_dotenv()  # Loads from .env in working directory
```

## Python Dependencies

Each skill has its own `requirements.txt` in the `scripts/` directory:

```bash
# Install dependencies for a specific skill
pip install -r domain/scripts/requirements.txt
pip install -r oss/scripts/requirements.txt
pip install -r cdn/scripts/requirements.txt
```

Common dependencies across skills:
- `alibabacloud_credentials>=0.3.0`
- `alibabacloud_tea_openapi>=0.3.0`
- `alibabacloud_tea_util>=0.3.0`
- `python-dotenv>=1.0.0`

Service-specific SDKs:
- Domain: `alibabacloud_domain20180129`, `alibabacloud_alidns20150109`
- OSS: `alibabacloud_oss_v2`
- CDN: `alibabacloud_cdn20180510`
- SLS: `alibabacloud_sls20201230`
- Billing: `alibabacloud_bssopenapi20171214`

## Running Scripts

Scripts are designed to be run directly from the skill's `scripts/` directory:

```bash
# Domain management
cd domain/scripts
python query_domainlist.py
python describe_domain_records.py --domain example.com

# OSS operations
cd oss/scripts
python list_buckets.py --region cn-hangzhou
python put_object.py --bucket my-bucket --key path/file.txt --file ./local.txt

# CDN operations
cd cdn/scripts
python describe_user_domains.py
python describe_domain_cname.py --domain www.example.com
```

## Skill Metadata

Each `SKILL.md` contains YAML frontmatter defining the skill:

```yaml
---
name: skill-name
description: >-
  Multi-line description of what the skill does,
  its capabilities, and usage constraints.
---
```

## Key Implementation Patterns

### Error Handling
Scripts print error messages and diagnostic URLs from Alibaba Cloud API responses:
```python
print(getattr(error, "message", str(error)))
if hasattr(error, "data") and error.data:
    print(error.data.get("Recommend"))
```

### Client Initialization
All scripts follow the same client initialization pattern using Tea OpenAPI:
```python
config = open_api_models.Config(
    access_key_id=access_key_id,
    access_key_secret=access_key_secret
)
config.endpoint = 'service.aliyuncs.com'
client = ServiceClient(config)
```

### Reference YML Files
API contracts in `reference/*.yml` document:
- Parameter names, types, required status
- Response schemas with field descriptions
- Example request/response payloads

## Deployment Skill Orchestration

The `deploy/` skill is an orchestration skill that coordinates:
1. Domain selection/management (via aliyun-domain-skill)
2. OSS bucket creation and static website configuration
3. CDN domain setup with HTTPS certificates
4. DNS CNAME and TXT record management

It uses `.aliyun-config.json` in the target project to track deployment state and enable incremental updates (upload + CDN refresh only).

## Git Ignore

The repository ignores:
- `.env` files (credential files)
- `.claude/` and `.agents/` directories (Claude Code working directories)
- `skills-lock.json` (lock file for skill installations)
