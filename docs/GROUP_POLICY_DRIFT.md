# Group Policy Configuration Drift Detection

## Overview

This playbook implements automated detection and remediation of Meraki Group Policy configuration drift. It establishes a "golden network" baseline defined in your source of truth (`group_vars/all.yml`) and continuously monitors for deviations from this baseline.

**Key Benefits:**
- Detect unauthorized or accidental configuration changes
- Maintain security compliance for firewall rules and bandwidth policies
- Automatically remediate drift or generate reports for manual review
- Integrate with CI/CD for continuous compliance monitoring

## What is Configuration Drift?

Configuration drift occurs when the actual state of your network deviates from the desired baseline. This can happen due to:

- Manual changes made directly in the Meraki Dashboard
- Emergency fixes that bypass change management
- Testing or troubleshooting that wasn't reverted
- Multiple administrators making conflicting changes

**Example Scenario:**

If someone accidentally changes a group policy's bandwidth limit from 10 Mbps to 20 Mbps in the Dashboard, running this playbook will:
1. Detect the drift by comparing current state vs. desired state
2. Report the deviation in detail
3. Automatically revert to 10 Mbps (in remediation mode)
4. Document the change in a timestamped report

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Source of Truth                            │
│              (group_vars/all.yml)                           │
│                                                             │
│  meraki_group_policies:                                     │
│    - name: "Standard User Policy"                          │
│      bandwidth: { limitUp: 10000, limitDown: 50000 }      │
│      vlanTagging: { vlanId: "10" }                        │
│      firewallAndTrafficShaping: { ... }                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Drift Detection Playbook                       │
│         (playbooks/group_policy_drift.yml)                  │
│                                                             │
│  1. Query current state from Meraki API                     │
│  2. Compare against source of truth                         │
│  3. Detect differences (drift)                              │
│  4. Generate detailed report                                │
│  5. Remediate (if not in check mode)                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│   Meraki Dashboard   │      │  Markdown Report     │
│   (via API)          │      │  (reports/)          │
│                      │      │                      │
│  Current State:      │      │  - Drift detected    │
│  - Policies          │      │  - Differences       │
│  - Settings          │      │  - Recommendations   │
└──────────────────────┘      └──────────────────────┘
```

## Source of Truth Configuration

Group policies are defined in `group_vars/all.yml`. This file serves as the single source of truth for your network configuration.

### Example Configuration

```yaml
meraki_group_policies:
  # Standard User Policy - Corporate employees
  - name: "Standard User Policy"
    bandwidth:
      settings: "custom"
      bandwidthLimits:
        limitUp: 10000    # 10 Mbps upload
        limitDown: 50000  # 50 Mbps download
    firewallAndTrafficShaping:
      settings: "custom"
      l3FirewallRules:
        - comment: "Allow HTTP/HTTPS"
          policy: "allow"
          protocol: "tcp"
          destPort: "80,443"
          destCidr: "Any"
        - comment: "Deny all other traffic"
          policy: "deny"
          protocol: "Any"
          destPort: "Any"
          destCidr: "Any"
    vlanTagging:
      settings: "custom"
      vlanId: "10"
    bonjourForwarding:
      settings: "disabled"
    splashAuthSettings: "bypass"
  
  # Guest Policy - Limited access
  - name: "Guest Policy"
    bandwidth:
      settings: "custom"
      bandwidthLimits:
        limitUp: 1000     # 1 Mbps upload
        limitDown: 5000   # 5 Mbps download
    vlanTagging:
      settings: "custom"
      vlanId: "100"
```

### What Gets Monitored

The drift detection monitors these group policy settings:

| Setting | Description | Impact if Drifted |
|---------|-------------|-------------------|
| **Bandwidth Limits** | Upload/download speed caps | Users may get unexpected speeds |
| **VLAN Tagging** | Network segmentation | Traffic may route incorrectly |
| **L3 Firewall Rules** | IP-based access control | Security vulnerabilities |
| **Bonjour Forwarding** | mDNS service discovery | Service discovery may fail |
| **Splash Auth Settings** | Captive portal behavior | Guest access may break |

## Usage Examples

### 1. Report Mode (Check for Drift)

Run in check mode to detect drift without making any changes. Safe to run in production.

```bash
# Check for drift without remediation
ansible-playbook playbooks/group_policy_drift.yml --check --diff

# Check specific network
ansible-playbook playbooks/group_policy_drift.yml --check --limit sandbox

# Verbose output for debugging
ansible-playbook playbooks/group_policy_drift.yml --check -vv
```

**Output:**
```
Group Policy Drift Detection Results:
Total Policies Checked: 2
Policies In Compliance: 1
Policies With Drift: 1

Policies with drift:
- Standard User Policy: Bandwidth mismatch: current={'limitUp': 20000} desired={'limitUp': 10000}
```

### 2. Auto-Remediation Mode

Run without `--check` to automatically correct detected drift.

```bash
# Detect and auto-remediate drift
ansible-playbook playbooks/group_policy_drift.yml

# Remediate with detailed logging
ansible-playbook playbooks/group_policy_drift.yml -v
```

**Behavior:**
- Detects all drift
- Applies corrections to match source of truth
- Reports success/failure for each policy
- Generates detailed report in `reports/` directory

### 3. Scheduled Monitoring

Set up continuous compliance monitoring with cron.

```bash
# Daily at 2 AM - check mode only (no auto-fix)
0 2 * * * cd /path/to/meraki-wireless-ansible && ansible-playbook playbooks/group_policy_drift.yml --check

# Weekly remediation - Sundays at 3 AM
0 3 * * 0 cd /path/to/meraki-wireless-ansible && ansible-playbook playbooks/group_policy_drift.yml

# Hourly check with email alerts
0 * * * * cd /path/to/meraki-wireless-ansible && ansible-playbook playbooks/group_policy_drift.yml --check 2>&1 | mail -s "Group Policy Drift Report" netops@company.com
```

### 4. CI/CD Integration

The playbook is automatically validated in the CI/CD pipeline:

```yaml
# .github/workflows/validate.yml includes:
- Run drift detection in check mode against DevNet sandbox
- Validate playbook syntax and logic
- Ensure reports are generated correctly
```

Every pull request and push to main triggers drift detection validation.

## Drift Report

Each run generates a timestamped markdown report in `reports/`:

```
reports/
├── group_policy_drift_1707174000.md
├── group_policy_drift_1707260400.md
└── group_policy_drift_1707346800.md
```

### Report Contents

1. **Executive Summary**
   - Total policies checked
   - Compliance statistics
   - Overall status

2. **Detailed Analysis**
   - Per-policy drift findings
   - Specific configuration differences
   - Impact assessment

3. **Recommendations**
   - How to update source of truth
   - Commands to remediate
   - Best practices

4. **Next Steps**
   - Action items checklist
   - Documentation updates needed

## Testing Approach

### Manual Drift Creation (for Testing)

1. **Create baseline state:**
   ```bash
   ansible-playbook playbooks/group_policy_drift.yml
   ```

2. **Manually modify a policy in Meraki Dashboard:**
   - Navigate to Network-wide > Group policies
   - Edit "Standard User Policy"
   - Change bandwidth from 10 Mbps to 20 Mbps
   - Save changes

3. **Detect drift:**
   ```bash
   ansible-playbook playbooks/group_policy_drift.yml --check
   ```
   
   **Expected output:**
   ```
   Policies With Drift: 1
   - Standard User Policy: Bandwidth mismatch detected
   ```

4. **Auto-remediate:**
   ```bash
   ansible-playbook playbooks/group_policy_drift.yml
   ```
   
   **Expected output:**
   ```
   Remediation Complete:
   - Successfully remediated: 1 policy
   - Standard User Policy: CORRECTED
   ```

5. **Verify compliance:**
   ```bash
   ansible-playbook playbooks/group_policy_drift.yml --check
   ```
   
   **Expected output:**
   ```
   All policies are compliant with source of truth
   ```

### Automated Testing

The playbook includes these safety features:

- **Variable validation** - Fails early if required variables missing
- **API retry logic** - Handles transient API failures (3 retries with 5s delay)
- **Idempotency** - Safe to run multiple times
- **Error handling** - Detailed error messages with remediation suggestions
- **Check mode support** - Works correctly with `--check` and `--diff`

## Operational Best Practices

### 1. Regular Drift Detection Schedule

```bash
# Recommended: Check daily, remediate weekly
0 2 * * * ansible-playbook playbooks/group_policy_drift.yml --check
0 3 * * 0 ansible-playbook playbooks/group_policy_drift.yml
```

### 2. Change Management Integration

**Always update the source of truth first:**

```bash
# 1. Edit source of truth
vim group_vars/all.yml

# 2. Test in check mode
ansible-playbook playbooks/group_policy_drift.yml --check

# 3. Apply changes
ansible-playbook playbooks/group_policy_drift.yml

# 4. Commit to version control
git add group_vars/all.yml
git commit -m "Update group policy bandwidth limits"
git push
```

### 3. Incident Response Workflow

**When drift is detected:**

1. **Review the drift report** - Understand what changed
2. **Determine if intentional** - Was this an approved change?
3. **Choose action:**
   - If intentional: Update source of truth
   - If accidental: Auto-remediate to revert
   - If malicious: Investigate security incident

### 4. Multi-Environment Strategy

Use environment-specific overrides:

```yaml
# group_vars/all.yml - Global baseline
meraki_group_policies:
  - name: "Standard User Policy"
    bandwidth: { limitUp: 10000, limitDown: 50000 }

# group_vars/production.yml - Production overrides
meraki_group_policies:
  - name: "Standard User Policy"
    bandwidth: { limitUp: 20000, limitDown: 100000 }  # Higher limits in prod

# group_vars/sandbox.yml - Sandbox overrides
meraki_group_policies:
  - name: "Standard User Policy"
    bandwidth: { limitUp: 5000, limitDown: 25000 }   # Lower limits in sandbox
```

## Troubleshooting

### Issue: "Required variables missing"

**Cause:** `meraki_network_id` or API key not set

**Solution:**
```bash
# Set network ID in inventory or pass as extra var
ansible-playbook playbooks/group_policy_drift.yml -e "meraki_network_id=L_123456789"

# Ensure API key is in environment or vault
export MERAKI_DASHBOARD_API_KEY="your_api_key_here"
```

### Issue: "No group policies found"

**Cause:** Network has no group policies configured, or API permission issue

**Solution:**
1. Verify network ID is correct
2. Check API key has read access to group policies
3. Create initial policies manually or via other playbook

### Issue: "Remediation failed"

**Cause:** API rate limit, invalid configuration, or permission issue

**Solution:**
1. Check error message for specific cause
2. Verify API key has write permissions
3. Increase retry delay: `-e "drift_api_retry_delay=10"`
4. Validate configuration syntax in source of truth

### Issue: False Positive Drift Detection

**Cause:** Meraki API returns slightly different format than what was configured

**Solution:**
1. Review drift report to see exact differences
2. Adjust source of truth to match API format
3. Update drift sensitivity settings in role defaults

## Advanced Configuration

### Customize Drift Detection Sensitivity

Edit `roles/meraki_group_policy_drift/defaults/main.yml`:

```yaml
# Selectively disable certain checks
drift_check_bandwidth: true
drift_check_vlan: true
drift_check_firewall: true
drift_check_bonjour: false  # Ignore Bonjour drift
drift_check_splash: true

# Adjust API retry behavior
drift_api_retries: 5        # More retries for flaky networks
drift_api_retry_delay: 10   # Longer delay between retries
```

### Integrate with Monitoring Systems

**Send alerts on drift detection:**

```bash
# Wrapper script: check_group_policy_drift.sh
#!/bin/bash
OUTPUT=$(ansible-playbook playbooks/group_policy_drift.yml --check 2>&1)
DRIFT_COUNT=$(echo "$OUTPUT" | grep "Policies With Drift:" | awk '{print $4}')

if [ "$DRIFT_COUNT" -gt 0 ]; then
  # Send to Slack, PagerDuty, email, etc.
  curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"⚠️ Group Policy Drift Detected: $DRIFT_COUNT policies\"}" \
    "$SLACK_WEBHOOK_URL"
fi
```

### Custom Report Formats

Modify `roles/meraki_group_policy_drift/templates/drift_report.md.j2` or create additional templates:

```jinja2
# drift_report.json.j2 - JSON format for tooling
{
  "timestamp": "{{ drift_results.timestamp }}",
  "total_policies": {{ drift_results.total_policies }},
  "drift_detected": {{ drift_results.drift_detected }},
  "policies": {{ drift_results.policies | to_json }}
}
```

## Related Documentation

- **Getting Started**: `docs/GETTING_STARTED.md` - Initial setup
- **Architecture**: `docs/ARCHITECTURE.md` - System design patterns
- **Troubleshooting**: `docs/TROUBLESHOOTING.md` - Common issues
- **Compliance Overview**: `docs/COMPLIANCE.md` - SSID compliance checking

## Future Enhancements

Planned features not yet implemented:

- ServiceNow/Jira ticket creation for drift alerts
- Slack/Teams notifications
- L7 firewall rule drift detection
- MX appliance L3 firewall drift
- SSID access policy drift detection
- Historical drift trending and analytics

## Support

For questions or issues:

1. Check this documentation first
2. Review `docs/TROUBLESHOOTING.md`
3. Check GitHub Issues
4. Contact your network operations team

---

**Last Updated:** February 5, 2026  
**Maintainer:** Meraki Automation Team  
**Playbook Version:** 1.0.0
