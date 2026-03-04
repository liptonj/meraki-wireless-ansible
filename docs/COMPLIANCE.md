# Meraki Wireless Compliance and Drift Detection

This document explains how to use the compliance checking and drift detection features for Meraki wireless networks.

## Overview

The compliance check playbook compares actual SSID configurations in Meraki Dashboard against a desired state defined in `group_vars`. It detects configuration drift (manual changes made in Dashboard) and generates detailed compliance reports.

## Quick Start

### 1. Configure Desired State

Define your desired SSID configurations in `group_vars/all.yml` or `group_vars/compliance.yml`:

```yaml
meraki_desired_ssids:
  - network_name: "Corporate-Office"
    network_id: "N_1234567890abcdef"
    ssids:
      - name: "Corporate"
        enabled: true
        authMode: "8021x"
        encryptionMode: "wpa2-eap"
        visible: true
        broadcast: true
        minBitrate: 11
        bandSelection: "Dual band operation"
```

### 2. Run Compliance Check

```bash
# Basic compliance check
ansible-playbook playbooks/compliance_check.yml

# Dry-run mode (check for drift without changes)
ansible-playbook playbooks/compliance_check.yml --check --diff

# Check specific network
ansible-playbook playbooks/compliance_check.yml --limit Corporate-Office
```

### 3. Review Report

Compliance reports are saved to `reports/compliance_report_{timestamp}.md` with:
- Executive summary (networks/SSIDs checked, compliant/non-compliant counts)
- Per-network compliance matrix
- Detailed drift detection showing current vs desired values
- Remediation recommendations

## Use Cases

### Drift Detection

Detect when someone manually changes SSID settings in Meraki Dashboard:

```bash
# Run check mode to see drift without generating full report
ansible-playbook playbooks/compliance_check.yml --check
```

### Scheduled Compliance Checks

Schedule daily compliance checks with cron:

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/repo && ansible-playbook playbooks/compliance_check.yml >> /var/log/meraki_compliance.log 2>&1
```

### CI/CD Integration

Integrate compliance checks into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Compliance Check
  run: |
    ansible-playbook playbooks/compliance_check.yml
    # Fail build if non-compliant networks found
    if grep -q "Non-Compliant" reports/compliance_report_*.md; then
      exit 1
    fi
```

## Configuration

### Desired State Structure

The `meraki_desired_ssids` variable defines your source of truth:

```yaml
meraki_desired_ssids:
  - network_name: "Network1"      # Must match inventory hostname
    network_id: "N_..."           # Meraki network ID
    ssids:                        # List of desired SSID configs
      - name: "SSID Name"
        enabled: true
        authMode: "8021x"         # Options: open, psk, 8021x, ipsk
        encryptionMode: "wpa2-eap" # Options: wpa, wpa-eap, wpa2, wpa2-eap
        visible: true
        broadcast: true
        minBitrate: 11            # Options: 1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54
        bandSelection: "Dual band operation"  # Options: "Dual band operation", "5 GHz band only", etc.
```

### Compliance Settings

Control compliance check behavior:

```yaml
compliance_check_enabled: true      # Enable/disable compliance checking
compliance_strict_mode: false       # If true, any deviation fails compliance

# Fields to check (empty list = check all fields)
compliance_check_fields:
  - name
  - enabled
  - authMode
  - encryptionMode
  - visible
  - broadcast
  - minBitrate
  - bandSelection
```

## Understanding the Report

### Executive Summary

High-level metrics:
- Networks checked/compliant/non-compliant
- SSIDs checked/compliant/non-compliant
- Overall compliance status

### Network Details

For each network:
- Compliance status (✅ COMPLIANT or ⚠️ NON-COMPLIANT)
- Drift detection status
- SSID compliance matrix showing pass/fail for each SSID and field

### Drift Detection

When drift is detected, the report shows:
- Which SSIDs have drift
- Which fields differ
- Current value vs desired value
- Remediation command to restore compliance

## Troubleshooting

### No Desired Config Found

If a network doesn't have a desired config defined:
- The compliance check will skip that network
- Add the network to `meraki_desired_ssids` in group_vars

### SSID Not Found in Desired State

If an SSID exists in Meraki but not in desired state:
- It will be marked as non-compliant (no desired config to compare)
- Add the SSID to the desired state for that network

### API Errors

If you see API errors:
- Verify `MERAKI_API_KEY` environment variable is set
- Check network_id matches actual Meraki network ID
- Verify API key has read permissions for networks

## Best Practices

1. **Version Control**: Store desired state in version control (group_vars)
2. **Regular Checks**: Schedule compliance checks daily or weekly
3. **Alert on Drift**: Set up alerts when drift is detected
4. **Document Changes**: Update desired state when making intentional changes
5. **Review Reports**: Regularly review compliance reports for trends

## Integration with SSID Management

After detecting drift, restore compliance using the SSID management playbook:

```bash
# Detect drift
ansible-playbook playbooks/compliance_check.yml

# Restore compliance for non-compliant networks
ansible-playbook playbooks/ssid_management.yml --limit Corporate-Office
```

## See Also

- [SSID Management Documentation](SSID_MANAGEMENT.md)
- [Getting Started Guide](GETTING_STARTED.md)
- [Architecture Documentation](ARCHITECTURE.md)
