# Meraki Wireless Compliance and Security Baselines

This document explains how to use the compliance checking, security baselines, and drift detection features for Meraki wireless networks.

## Overview

The compliance system has two layers:

1. **Drift Detection** — Compares actual SSID configurations in Meraki Dashboard against a desired state defined in `group_vars/meraki_networks.yml`. Detects manual changes made in Dashboard.
2. **Security Baselines** — Policy checks applied to ALL enabled SSIDs regardless of desired state. Enforces minimum security standards (no open auth, WPA2 minimum, guest bandwidth limits).

When violations are detected, alerts are sent via **GitHub Issues** and **Webex Teams** webhooks.

## Quick Start

### 1. Configure Desired State

Define your desired SSID configurations in `group_vars/meraki_networks.yml`:

```yaml
meraki_desired_ssids:
  - network_name: "lab_site1"
    network_id: "{{ vault_meraki_network_id_1 }}"
    ssids:
      - name: "Corp-Secure"
        enabled: true
        authMode: "psk"
        encryptionMode: "wpa2"
        visible: true
        minBitrate: 11
        bandSelection: "Dual band operation"
```

### 2. Run Compliance Check

```bash
# Run compliance check with the compliance inventory
ansible-playbook playbooks/compliance_check.yml -i inventory/production_compliance.yml

# Dry-run mode (check for drift without changes)
ansible-playbook playbooks/compliance_check.yml -i inventory/production_compliance.yml --check --diff
```

### 3. Review Report

Compliance reports are saved to `reports/compliance_report_{timestamp}.md`.

## Security Baseline Checks

Security baselines are defined in `roles/meraki_compliance/defaults/main.yml` and apply to all enabled SSIDs automatically:

| Rule | Severity | Description |
|------|----------|-------------|
| `no_open_auth` | Critical | Enabled SSIDs must not use open authentication |
| `minimum_encryption` | Critical | Enabled SSIDs must use WPA2 or higher encryption |
| `guest_bandwidth_limits` | Warning | Guest SSIDs (matching `(?i)guest` pattern) must have bandwidth limits |
| `disabled_ssid_broadcast` | Warning | Disabled SSIDs should not be broadcasting |

Critical violations trigger the alerting pipeline (GitHub Issues + Webex Teams).

### Customizing Security Rules

Override in `group_vars/meraki_networks.yml` or via extra vars:

```yaml
security_baseline_rules:
  no_open_auth:
    enabled: true
    severity: "critical"
  minimum_encryption:
    enabled: true
    severity: "critical"
    minimum: "wpa2"
  guest_bandwidth_limits:
    enabled: true
    severity: "warning"
    guest_ssid_pattern: "(?i)guest"
  disabled_ssid_broadcast:
    enabled: true
    severity: "warning"
```

## Alerting

### GitHub Issues

When compliance fails, a GitHub Issue is auto-created with violation details and a remediation command. Configure via:

```yaml
compliance_github_alert_enabled: true
compliance_github_repo: "your-username/meraki-wireless-ansible"
compliance_github_token: "{{ lookup('env', 'GITHUB_TOKEN') }}"
```

### Webex Teams

A Webex Teams webhook message is sent with a markdown summary. Configure via:

```yaml
compliance_webex_alert_enabled: true
compliance_webex_webhook_url: "{{ lookup('env', 'WEBEX_WEBHOOK_URL') }}"
```

## GitHub Actions Integration

The `compliance.yml` workflow runs compliance checks automatically:

- **On schedule** — Every 6 hours (`0 */6 * * *`)
- **On manual dispatch** — Via the GitHub Actions UI
- **On webhook** — Triggered by `repository_dispatch` (Meraki config change)
- **After SSID deployment** — Called by `deploy-ssids.yml` after live deploys

After the compliance check, the workflow snapshots the live config to `baselines/` and commits it back to the repo for GitOps drift detection.

## GitOps Configuration Baseline

The `config_snapshot.yml` playbook pulls live SSID configuration from Meraki, filters out sensitive fields (like PSK), and stores it as YAML in `baselines/<network_id>/ssids.yml`.

On subsequent runs, the snapshot is compared against the stored baseline. Any difference indicates drift from manual Dashboard changes.

```bash
ansible-playbook playbooks/config_snapshot.yml -i inventory/production_compliance.yml
```

## Configuration Reference

### Compliance Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `compliance_check_enabled` | `true` | Enable/disable compliance checking |
| `compliance_strict_mode` | `false` | If true, any deviation fails compliance |
| `compliance_alerting_enabled` | `true` | Enable/disable all alerting |
| `security_baseline_enabled` | `true` | Enable/disable security baseline checks |

### Desired State Structure

```yaml
meraki_desired_ssids:
  - network_name: "Network1"       # Must match inventory hostname
    network_id: "N_..."            # Meraki network ID
    ssids:
      - name: "SSID Name"
        enabled: true
        authMode: "psk"            # Options: open, psk, 8021x, ipsk
        encryptionMode: "wpa2"     # Options: wpa, wpa2, wpa3
        visible: true
        minBitrate: 11
        bandSelection: "Dual band operation"
```

## Remediation

After detecting drift, restore compliance by re-deploying SSIDs:

```bash
ansible-playbook playbooks/ssid_management.yml -i inventory/production.yml
```

Or trigger the deploy workflow via GitHub Actions.

## See Also

- [Getting Started Guide](GETTING_STARTED.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
