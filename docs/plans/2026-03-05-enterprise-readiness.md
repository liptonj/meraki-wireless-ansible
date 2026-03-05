# Enterprise Readiness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove all sandbox/DevNet/demo/YouTube references and make the repo look enterprise-ready with production-first defaults, corporate naming, and no insecure config flags.

**Architecture:** Restructure inventory from sandbox-centric to production-first (`labnet`/`lab_site1` naming). Sweep all group_vars, workflows, scripts, playbooks, and docs to eliminate non-enterprise terminology. Remove insecure config toggles entirely.

**Tech Stack:** Ansible, YAML, Bash, Markdown (no new dependencies)

---

## Context

**Organization:** LabNet  
**Network:** Lab-Site1  
**Environment naming:** production (default), development.yml.example for non-prod  
**SSID naming:** Corp-Secure, Corp-Guest  
**AP pattern:** `{site}-{network}-AP-{serial[-6:]}`

### Translation Table

| Current | New |
|---|---|
| `meraki_sandbox` (host) | `labnet` |
| `sandbox_network` (host) | `lab_site1` |
| `meraki_environment: sandbox` | `meraki_environment: production` |
| SSID `Sandbox-Test` | `Corp-Secure` |
| SSID `Sandbox-Open` | `Corp-Guest` |
| AP pattern `SANDBOX-{network_name}-AP-{serial[-6:]}` | `{site}-{network}-AP-{serial[-6:]}` |
| AP tags `sandbox`, `devnet` | removed (keep only `managed-by-ansible`) |
| `vault_sandbox_test_psk` / `TestPassword123!` | `vault_corp_secure_psk` / `"your_corp_secure_psk_here"` |
| `meraki_test_mode: true` | removed entirely |
| `meraki_allow_insecure_configs: true` | removed entirely |
| `meraki_skip_validations` | removed entirely |
| `meraki_environment_type: "test"` | removed entirely |
| `sandbox_changes_` in log path | `meraki_changes_` |
| `ENVIRONMENT=sandbox` | `ENVIRONMENT=production` |
| `inventory/sandbox.yml` | `inventory/production.yml` |
| `inventory/sandbox_compliance.yml` | `inventory/production_compliance.yml` |

---

### Task 1: Restructure Inventory Files

**Files:**
- Delete: `inventory/sandbox.yml`
- Delete: `inventory/sandbox_compliance.yml`
- Delete: `inventory/production.yml.example`
- Create: `inventory/production.yml`
- Create: `inventory/production_compliance.yml`
- Create: `inventory/development.yml.example`

**Step 1: Create `inventory/production.yml`**

Write this file:

```yaml
---
# Meraki Production Inventory
# Control node: localhost (connects to Meraki API, no SSH)

all:
  children:
    meraki_orgs:
      hosts:
        labnet:
          meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('YOUR_ORG_ID', true)) }}"
          meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
          meraki_base_url: "https://api.meraki.com/api/v1"
          meraki_environment: production
          meraki_network_ids:
            - "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID_1', true)) }}"

      vars:
        meraki_api_timeout: 60
        meraki_api_retries: 3
        meraki_api_retry_delay: 2
        meraki_rate_limit: 4

localhost:
  ansible_connection: local
  ansible_host: localhost
  ansible_python_interpreter: auto_silent
```

**Step 2: Create `inventory/production_compliance.yml`**

Write this file:

```yaml
---
# Compliance Check Inventory
# Maps individual Meraki networks as hosts for per-network compliance checks

all:
  children:
    meraki_networks:
      hosts:
        lab_site1:
          meraki_network_id: "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID', true)) }}"
          meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('YOUR_ORG_ID', true)) }}"
          meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
          meraki_base_url: "https://api.meraki.com/api/v1"
          meraki_environment: production
          ansible_connection: local
          ansible_python_interpreter: auto_silent

    meraki_orgs:
      hosts:
        labnet:
          meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('YOUR_ORG_ID', true)) }}"
          meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
          meraki_base_url: "https://api.meraki.com/api/v1"
          meraki_environment: production
          meraki_network_ids:
            - "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID', true)) }}"
```

**Step 3: Create `inventory/development.yml.example`**

Write this file:

```yaml
---
# Development Inventory Template
#
# 1. Copy: cp inventory/development.yml.example inventory/development.yml
# 2. Replace placeholder values with your development environment values
# 3. Store sensitive values in vault/secrets.yml (encrypted)
# 4. Do NOT commit development.yml to version control

all:
  children:
    meraki_orgs:
      hosts:
        dev_org:
          meraki_org_id: "{{ vault_meraki_org_id_dev }}"
          meraki_api_key: "{{ vault_meraki_api_key_dev }}"
          meraki_base_url: "https://api.meraki.com/api/v1"
          meraki_environment: development
          meraki_network_ids:
            - "{{ vault_meraki_network_id_dev_1 }}"

      vars:
        meraki_api_timeout: 60
        meraki_api_retries: 5
        meraki_api_retry_delay: 3
        meraki_rate_limit: 3

localhost:
  ansible_connection: local
  ansible_host: localhost
  ansible_python_interpreter: auto_silent
```

**Step 4: Delete old inventory files**

Run:
```bash
rm inventory/sandbox.yml inventory/sandbox_compliance.yml inventory/production.yml.example
```

**Step 5: Verify new inventory files parse**

Run: `ansible-inventory --list -i inventory/production.yml 2>&1 | head -5`
Expected: JSON output showing `labnet` host (may show warnings about undefined vault vars — that's OK)

**Step 6: Commit**

```bash
git add inventory/
git commit -m "refactor(inventory): replace sandbox with production-first inventory

- production.yml as default (labnet org, lab_site1 network)
- production_compliance.yml for compliance checks
- development.yml.example template for non-prod environments
- Remove sandbox.yml, sandbox_compliance.yml, production.yml.example"
```

---

### Task 2: Update Group Variables

**Files:**
- Modify: `group_vars/meraki_orgs.yml` (full rewrite)
- Modify: `group_vars/meraki_networks.yml` (full rewrite)

**Step 1: Rewrite `group_vars/meraki_orgs.yml`**

Replace the entire file with:

```yaml
---
# SSID Deployment Config — applies to hosts in the `meraki_orgs` inventory group
# (used by ssid_management.yml). Defines what SSIDs to deploy and operational settings.

meraki_environment: production

# API Configuration
meraki_api_timeout: 60
meraki_api_retries: 5
meraki_api_retry_delay: 3
meraki_rate_limit: 3

# Organization and Network IDs
meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('YOUR_ORG_ID', true)) }}"

meraki_network_ids:
  - "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID_1', true)) }}"

# SSID Configuration
meraki_ssids:
  - name: "Corp-Secure"
    enabled: true
    authMode: "psk"
    encryptionMode: "wpa2"
    psk: "{{ vault_corp_secure_psk }}"
    minBitrate: 11
    bandSelection: "Dual band operation"
    perClientBandwidthLimitUp: 0
    perClientBandwidthLimitDown: 0
    visible: true
    availableOnAllAps: true

  - name: "Corp-Guest"
    enabled: false
    authMode: "open"
    encryptionMode: "wpa"
    minBitrate: 11
    bandSelection: "Dual band operation"
    visible: true
    availableOnAllAps: true

# AP Configuration
meraki_ap_name_pattern: "{site}-{network_name}-AP-{serial[-6:]}"

meraki_ap_tags:
  - "managed-by-ansible"

# Operational Settings
meraki_dry_run: false
meraki_validate_changes: true
meraki_log_changes: true
meraki_change_log_path: "./logs/meraki_changes_{{ ansible_date_time.epoch }}.json"

# Compliance Rules
meraki_compliance_rules:
  - name: "encryption_standard"
    check: "all_ssids_use_wpa2_or_wpa3"
    severity: "error"
```

**Step 2: Rewrite `group_vars/meraki_networks.yml`**

Replace the entire file with:

```yaml
---
# Compliance Desired State — applies to hosts in the `meraki_networks` inventory group
# (used by compliance_check.yml and config_snapshot.yml). Any deviation is flagged as drift.

meraki_desired_ssids:
  - network_name: "lab_site1"
    network_id: "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID', true)) }}"
    ssids:
      - name: "Corp-Secure"
        enabled: true
        authMode: "psk"
        encryptionMode: "wpa2"
        visible: true
        broadcast: true
        minBitrate: 11
        bandSelection: "Dual band operation"
```

**Step 3: Verify syntax**

Run: `ansible-playbook --syntax-check playbooks/ssid_management.yml -i inventory/production.yml 2>&1 | tail -3`
Expected: "playbook: playbooks/ssid_management.yml" (syntax OK)

**Step 4: Commit**

```bash
git add group_vars/
git commit -m "refactor(group_vars): enterprise naming and remove insecure flags

- SSIDs: Corp-Secure / Corp-Guest (replaces Sandbox-Test / Sandbox-Open)
- AP pattern: {site}-{network}-AP-{serial} (replaces SANDBOX prefix)
- Remove meraki_test_mode, meraki_allow_insecure_configs, meraki_skip_validations
- Remove hardcoded TestPassword123! fallback
- Compliance severity: error (was warning)"
```

---

### Task 3: Update Configuration Files

**Files:**
- Modify: `ansible.cfg` (line 5)
- Modify: `.env.example` (line 7)
- Modify: `vault/secrets.yml.example` (lines 14, 18)

**Step 1: Update `ansible.cfg`**

Change line 5 from:
```
inventory = inventory/sandbox.yml
```
to:
```
inventory = inventory/production.yml
```

**Step 2: Update `.env.example`**

Change line 7 from:
```
ENVIRONMENT=sandbox
```
to:
```
ENVIRONMENT=production
```

**Step 3: Update `vault/secrets.yml.example`**

Replace the full file with:

```yaml
---
# Ansible Vault Encrypted Secrets - Example Template
#
# 1. Copy: cp vault/secrets.yml.example vault/secrets.yml
# 2. Fill in your actual secret values
# 3. Encrypt: ansible-vault encrypt vault/secrets.yml
#
# To edit: ansible-vault edit vault/secrets.yml
# To view: ansible-vault view vault/secrets.yml

# Meraki API Credentials
vault_meraki_api_key: "your_meraki_api_key_here"

# Organization and Network IDs
vault_meraki_org_id: "your_org_id_here"
vault_meraki_network_id_1: "your_network_id_1_here"
vault_meraki_network_id_2: "your_network_id_2_here"

# SSID Pre-Shared Keys
vault_corp_secure_psk: "your_corp_secure_psk_here"

# RADIUS Server Credentials
vault_radius_server_1_host: "radius1.example.com"
vault_radius_server_1_secret: "your_radius_shared_secret_here"
vault_radius_server_2_host: "radius2.example.com"
vault_radius_server_2_secret: "your_radius_shared_secret_2_here"
vault_radius_accounting_server_host: "radius-accounting.example.com"
vault_radius_accounting_server_secret: "your_radius_accounting_secret_here"

# SSID Passwords (PSK)
vault_guest_ssid_psk: "your_guest_network_password_here"
vault_corporate_byod_psk: "your_corporate_byod_password_here"
vault_iot_ssid_psk: "your_iot_network_password_here"

# Webhook / Notification Secrets
vault_webhook_url: "https://your-webhook-url.com/meraki-events"
vault_smtp_server: "smtp.example.com"
vault_smtp_username: "your_smtp_username"
vault_smtp_password: "your_smtp_password"
```

**Step 4: Commit**

```bash
git add ansible.cfg .env.example vault/secrets.yml.example
git commit -m "refactor(config): production defaults for ansible.cfg, .env, vault template

- Default inventory: production.yml
- Default environment: production
- Remove sandbox vault vars and TestPassword123!
- Add vault_corp_secure_psk placeholder"
```

---

### Task 4: Update Playbook Usage Comments

**Files:**
- Modify: `playbooks/ssid_management.yml` (lines 6-7)
- Modify: `playbooks/config_snapshot.yml` (line 6)
- Modify: `playbooks/compliance_check.yml` (line 117, inside the GitHub Issue body)

**Step 1: Update `playbooks/ssid_management.yml` header comments**

Change lines 6-7 from:
```yaml
#   ansible-playbook playbooks/ssid_management.yml -i inventory/sandbox.yml
#   ansible-playbook playbooks/ssid_management.yml -i inventory/sandbox.yml --check --diff
```
to:
```yaml
#   ansible-playbook playbooks/ssid_management.yml -i inventory/production.yml
#   ansible-playbook playbooks/ssid_management.yml -i inventory/production.yml --check --diff
```

**Step 2: Update `playbooks/config_snapshot.yml` header comment**

Change line 6 from:
```yaml
#   ansible-playbook playbooks/config_snapshot.yml -i inventory/sandbox_compliance.yml
```
to:
```yaml
#   ansible-playbook playbooks/config_snapshot.yml -i inventory/production_compliance.yml
```

**Step 3: Update `playbooks/compliance_check.yml` remediation command**

Change line 117 from:
```
            ansible-playbook playbooks/ssid_management.yml -i inventory/sandbox.yml
```
to:
```
            ansible-playbook playbooks/ssid_management.yml -i inventory/production.yml
```

**Step 4: Run syntax checks on all playbooks**

Run:
```bash
for playbook in playbooks/*.yml; do ansible-playbook --syntax-check "$playbook" -i inventory/production.yml; done
```
Expected: All three playbooks pass syntax check

**Step 5: Commit**

```bash
git add playbooks/
git commit -m "refactor(playbooks): update usage comments to production inventory paths"
```

---

### Task 5: Update CI/CD Workflows

**Files:**
- Modify: `.github/workflows/validate.yml`
- Modify: `.github/workflows/deploy-ssids.yml`
- Modify: `.github/workflows/compliance.yml`

**Step 1: Update `validate.yml`**

Make these changes:

1. Line 85: Change job name from `Dry Run Against DevNet Sandbox` to `Dry Run Validation`

2. Lines 130-132: Change the inventory selection logic from:
```yaml
              if [[ "$playbook" == *"compliance"* ]] || [[ "$playbook" == *"snapshot"* ]]; then
                INVENTORY="inventory/sandbox_compliance.yml"
              else
                INVENTORY="inventory/sandbox.yml"
```
to:
```yaml
              if [[ "$playbook" == *"compliance"* ]] || [[ "$playbook" == *"snapshot"* ]]; then
                INVENTORY="inventory/production_compliance.yml"
              else
                INVENTORY="inventory/production.yml"
```

**Step 2: Update `deploy-ssids.yml`**

Make these changes:

1. Lines 8-12: Change environment dropdown from:
```yaml
        default: 'sandbox'
        type: choice
        options:
          - sandbox
          - production
```
to:
```yaml
        default: 'production'
        type: choice
        options:
          - production
          - development
```

2. Line 75: Change from `inventory/sandbox.yml` to `inventory/production.yml`

3. Line 111: Change from `inventory/sandbox_compliance.yml` to `inventory/production_compliance.yml`

**Step 3: Update `compliance.yml`**

Make these changes:

1. Lines 8-12: Change environment dropdown from:
```yaml
        default: 'sandbox'
        type: choice
        options:
          - sandbox
          - production
```
to:
```yaml
        default: 'production'
        type: choice
        options:
          - production
          - development
```

2. Line 89: Change from `inventory/sandbox_compliance.yml` to `inventory/production_compliance.yml`

3. Line 104: Change from `inventory/sandbox_compliance.yml` to `inventory/production_compliance.yml`

**Step 4: Commit**

```bash
git add .github/workflows/
git commit -m "refactor(ci): production-first CI/CD workflows

- Default environment: production (was sandbox)
- Inventory paths: production.yml / production_compliance.yml
- Rename dry-run job: 'Dry Run Validation' (was DevNet Sandbox)"
```

---

### Task 6: Update Scripts and Makefile

**Files:**
- Modify: `scripts/smoke_test.sh` (lines 114-115, 122)
- Modify: `Makefile` (lines 9, 54)

**Step 1: Update `scripts/smoke_test.sh`**

1. Lines 114-115: Change from:
```bash
if [ -f "inventory/sandbox.yml" ]; then
    if ansible-inventory --list -i inventory/sandbox.yml > /dev/null 2>&1; then
```
to:
```bash
if [ -f "inventory/production.yml" ]; then
    if ansible-inventory --list -i inventory/production.yml > /dev/null 2>&1; then
```

2. Line 122: Change from:
```bash
    warning "Inventory file not found: inventory/sandbox.yml"
```
to:
```bash
    warning "Inventory file not found: inventory/production.yml"
```

**Step 2: Update `Makefile`**

1. Line 9: Change from:
```
	@echo "  make smoke-test - Run validation tests against DevNet sandbox"
```
to:
```
	@echo "  make smoke-test - Run validation tests against target environment"
```

2. Line 54: Change from:
```
	@echo "Running smoke tests against DevNet sandbox..."
```
to:
```
	@echo "Running smoke tests..."
```

**Step 3: Commit**

```bash
git add scripts/smoke_test.sh Makefile
git commit -m "refactor(scripts): update smoke test and Makefile for production inventory

- smoke_test.sh validates inventory/production.yml
- Makefile removes DevNet sandbox references"
```

---

### Task 7: Update README.md

**Files:**
- Modify: `README.md` (full rewrite)

**Step 1: Rewrite README.md**

Replace the entire file with:

```markdown
# Meraki Wireless Ansible Automation

[![Ansible](https://img.shields.io/badge/Ansible-2.20.2-EE0000?logo=ansible)](https://www.ansible.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automate Cisco Meraki wireless network management with Ansible playbooks. This project provides production-ready automation for SSID management, bulk AP deployment, and compliance checking.

## Quick Start

### Prerequisites

- **Python 3.12+** (required for Ansible 2.20.2)
- **Git** for cloning the repository
- **Meraki API Key** (get one from [Meraki Dashboard](https://dashboard.meraki.com/) — see [Getting Started](docs/GETTING_STARTED.md) for details)
- **Meraki Organization ID** (found in your Meraki Dashboard URL or API)

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/meraki-wireless-ansible.git
cd meraki-wireless-ansible
```

### 2. Setup Environment

```bash
make setup
source venv/bin/activate
```

### 3. Configure API Credentials

```bash
cp .env.example .env
# Edit .env and add your credentials:
# MERAKI_DASHBOARD_API_KEY=your_api_key_here
# MERAKI_ORG_ID=your_org_id_here
```

### 4. Run Your First Playbook

```bash
ansible-playbook --syntax-check playbooks/ssid_management.yml
ansible-playbook playbooks/ssid_management.yml
```

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Setup guide with GitHub Actions configuration
- **[Architecture](docs/ARCHITECTURE.md)** - Project structure and data flow
- **[Compliance](docs/COMPLIANCE.md)** - SSID compliance checking and security baselines
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common errors and solutions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## What This Project Does

### Playbooks

- **`ssid_management.yml`** - Deploy and configure wireless SSIDs across networks
- **`compliance_check.yml`** - Validate SSID configurations against desired state and security baselines
- **`config_snapshot.yml`** - Capture live Meraki config and store as GitOps baseline

### Key Features

- **GitOps for Wireless** - Config stored in Git, drift detected automatically
- **Security Baselines** - No open auth, WPA2 minimum, guest bandwidth limits
- **Automated Alerting** - GitHub Issues + Webex Teams on compliance violations
- **CI/CD Native** - Everything runs in GitHub Actions (deploy, check, alert, snapshot)
- **Idempotent Operations** - Safe to run multiple times
- **Environment-Aware** - Separate configs for production and development

## Available Commands

```bash
make setup      # Initial project setup
make lint       # Check code quality
make test       # Validate playbook syntax
make smoke-test # Run validation tests
make clean      # Remove virtual environment
```

## Project Structure

```
meraki-wireless-ansible/
├── .github/workflows/  # GitHub Actions CI/CD
│   ├── validate.yml        # Lint, syntax check, security scan
│   ├── deploy-ssids.yml    # SSID deployment workflow
│   └── compliance.yml      # Compliance check + snapshot workflow
├── playbooks/          # Main Ansible playbooks
│   ├── ssid_management.yml
│   ├── compliance_check.yml
│   └── config_snapshot.yml
├── roles/              # Reusable Ansible roles
│   ├── meraki_ssid/
│   ├── meraki_compliance/
│   └── meraki_snapshot/
├── inventory/          # Host and group definitions
│   ├── production.yml
│   └── production_compliance.yml
├── group_vars/         # Environment-specific variables
│   ├── all.yml
│   ├── meraki_orgs.yml
│   └── meraki_networks.yml
├── baselines/          # GitOps config snapshots (auto-updated)
├── vault/              # Encrypted secrets (Ansible Vault)
│   └── secrets.yml.example
├── reports/            # Generated compliance reports
└── docs/               # Documentation
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed explanation.

## Security Best Practices

- **Never commit API keys** - Use `.env` files (gitignored) or Ansible Vault
- **Use environment variables** - Load secrets from `.env` files
- **Encrypt sensitive data** - Use `ansible-vault encrypt` for production secrets
- **Review before running** - Always check playbooks before executing

## Troubleshooting

Common issues and solutions:

- **Rate Limiting** - Meraki API has rate limits. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#rate-limiting)
- **Authentication Errors** - Verify API key and organization ID. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#authentication-errors)
- **API Issues** - Check API status and endpoint configuration. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#api-issues)

For detailed troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make lint && make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Cisco Meraki** for the excellent Dashboard API
- **Ansible Community** for the powerful automation framework

---

**Ready to get started?** Head over to [GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed setup instructions!
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "refactor(readme): enterprise-ready README

- Remove YouTube section, video timestamps, video description template, video tags
- Remove sandbox/DevNet references
- Update project structure to show production inventory
- Clean, professional tone throughout"
```

---

### Task 8: Update Documentation Files

**Files:**
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/COMPLIANCE.md`
- Modify: `docs/GETTING_STARTED.md`
- Modify: `docs/TROUBLESHOOTING.md`
- Modify: `CONTRIBUTING.md`

This is the largest task — all five docs need sandbox/DevNet references replaced. For each file, apply these global replacements:

| Find | Replace |
|------|---------|
| `sandbox.yml` | `production.yml` |
| `sandbox_compliance.yml` | `production_compliance.yml` |
| `sandbox` (as host name) | `labnet` |
| `sandbox_network` (as host name) | `lab_site1` |
| `meraki_environment: sandbox` | `meraki_environment: production` |
| `Sandbox-Test` | `Corp-Secure` |
| `Sandbox-Open` | `Corp-Guest` |
| `DevNet sandbox` | the target environment |
| `DevNet` | (remove or rephrase) |
| `test/sandbox` | the target environment |
| `test/lab environment` | a dedicated test network |
| `ENVIRONMENT=sandbox` | `ENVIRONMENT=production` |

**Step 1: Update `docs/ARCHITECTURE.md`**

Apply these specific changes throughout the file:

1. Line 63: Change `sandbox.yml            # DevNet sandbox inventory (meraki_orgs)` to `production.yml          # Production inventory (meraki_orgs)`
2. Line 64: Change `sandbox_compliance.yml # Compliance inventory (meraki_networks)` to `production_compliance.yml # Compliance inventory (meraki_networks)`
3. Line 65: Change `production.yml.example # Production inventory template` to `development.yml.example  # Development inventory template`
4. Line 144: Change `inventory/sandbox.yml` example to show `inventory/production.yml` with host `labnet`
5. Line 150: Change `sandbox` host reference to `labnet`
6. Line 156: Change `sandbox`, `production-org-1` examples to `labnet`, `secondary-org`
7. Lines 173-174: Change `environment: sandbox` to `meraki_environment: production` and remove comment about sandbox override
8. Line 183: Change `inventory = inventory/sandbox.yml` to `inventory = inventory/production.yml`
9. Line 209: Change `(sandbox.yml)` to `(production.yml)`
10. Lines 255-259: Change all `sandbox` references in the step-by-step to `labnet`/`production`
11. Lines 327/329: Change `inventory/sandbox.yml` to `inventory/production.yml` in host vars examples
12. Lines 393-394: Change the execution flow `sandbox` references to `labnet`
13. Lines 405-408: Change variable loading examples from sandbox to production
14. Lines 417-418: Change playbook execution target from sandbox to labnet
15. Lines 467-469: Change environment separation section to show `production.yml` and `development.yml`

**Step 2: Update `docs/COMPLIANCE.md`**

1. Lines 22/25: Change `sandbox_network` to `lab_site1`
2. Line 25: Change `Sandbox-Test` to `Corp-Secure`
3. Lines 38/41: Change `inventory/sandbox_compliance.yml` to `inventory/production_compliance.yml`
4. Line 122: Change `inventory/sandbox_compliance.yml` to `inventory/production_compliance.yml`
5. Line 157: Change `inventory/sandbox.yml` to `inventory/production.yml`

**Step 3: Update `docs/GETTING_STARTED.md`**

1. Line 1 description: Change `test/lab environment` to `a Meraki organization with API enabled`
2. Lines 104-110: Rewrite test environment section to say "dedicated test network" instead of sandbox
3. Lines 215-216: Change `ENVIRONMENT=sandbox` to `ENVIRONMENT=production`
4. Line 387: Change `inventory/sandbox.yml` reference in ansible.cfg discussion to `inventory/production.yml`

**Step 4: Update `docs/TROUBLESHOOTING.md`**

1. Lines 9/194-246: Rename the "Sandbox Limitations" section to "API Limitations" and rewrite to remove all sandbox-specific language
2. Lines 21/108/199-200/208/253/460/531: Change all `[sandbox]` host references in error messages to `[labnet]`
3. Lines 342/387: Change `inventory/sandbox.yml` references to `inventory/production.yml`
4. Line 483: Change `ansible-inventory --host sandbox` to `ansible-inventory --host labnet`
5. Line 605: Change `Environment (sandbox vs production)` to `Environment details`

**Step 5: Update `CONTRIBUTING.md`**

1. Line 80: Change `Edit .env with your DevNet sandbox credentials` to `Edit .env with your Meraki API credentials`
2. Line 141: Remove `Test against sandbox (if applicable)` line, replace with `Test against your environment (if applicable)`
3. Line 153: Change `Changes work in sandbox environment` to `Changes work in target environment`
4. Lines 261/337: Change `Tested in sandbox` to `Tested in target environment` and `Sandbox/Production` to `Environment name`
5. Line 280: Change `Update getting started guide with DevNet instructions` to `Update getting started guide`
6. Lines 412-413: Change `environment: sandbox` example to `meraki_environment: production`

**Step 6: Verify no remaining sandbox references in docs**

Run:
```bash
grep -ri "sandbox" docs/ CONTRIBUTING.md README.md || echo "Clean — no sandbox references found"
```
Expected: "Clean — no sandbox references found"

**Step 7: Commit**

```bash
git add docs/ CONTRIBUTING.md
git commit -m "refactor(docs): enterprise terminology across all documentation

- Replace sandbox/DevNet with production-first language
- Update all inventory paths, host names, SSID names
- Rename 'Sandbox Limitations' to 'API Limitations'
- Remove test/lab/demo framing"
```

---

### Task 9: Final Cleanup and Validation

**Files:**
- Delete: `docs/plans/2026-03-04-30min-demo-closed-loop-compliance.md`

**Step 1: Delete the demo plan**

Run:
```bash
rm docs/plans/2026-03-04-30min-demo-closed-loop-compliance.md
```

**Step 2: Full-repo scan for remaining sandbox/DevNet references**

Run:
```bash
grep -ri "sandbox\|devnet\|TestPassword123\|meraki_test_mode\|meraki_allow_insecure" \
  --include="*.yml" --include="*.yaml" --include="*.md" --include="*.sh" \
  --include="*.cfg" --include="*.json" \
  --exclude-dir=.git --exclude-dir=venv \
  . || echo "Clean — no non-enterprise references found"
```
Expected: Only this plan file (the one you're reading) should appear, or "Clean"

**Step 3: Run full validation suite**

Run:
```bash
make lint && make test
```
Expected: All lint and syntax checks pass

**Step 4: Commit cleanup**

```bash
git add -A
git commit -m "chore: remove demo plan and verify enterprise readiness

- Delete 30min-demo-closed-loop-compliance plan
- Verified: zero sandbox/DevNet/test references in codebase"
```

---

## Summary of All Changes

| Category | Files Changed | Key Changes |
|----------|--------------|-------------|
| Inventory | 5 files (3 deleted, 2 created, 1 new example) | sandbox → production.yml with labnet/lab_site1 |
| Group Vars | 2 files | Corp-Secure/Corp-Guest SSIDs, remove insecure flags |
| Config | 3 files | Default to production inventory and environment |
| Playbooks | 3 files | Update usage comments |
| CI/CD | 3 workflows | Production-first defaults, rename jobs |
| Scripts | 2 files | Update inventory paths, remove DevNet language |
| README | 1 file | Full rewrite, strip YouTube/demo content |
| Docs | 5 files | Replace sandbox/DevNet throughout |
| Cleanup | 1 file deleted | Remove demo plan |

**Total: ~25 files touched across 9 tasks**
