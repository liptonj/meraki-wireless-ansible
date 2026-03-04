# Closed-Loop Wireless Compliance Demo Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the repo into a 30-minute demo that deploys an SSID, runs compliance checks, and auto-alerts via GitHub Issue + Webex Teams when drift is detected — all orchestrated by GitHub Actions.

**Architecture:** Everything runs in GitHub Actions — no local Ansible execution needed for the demo. The `meraki_ssid` role is built out to create/update SSIDs via `cisco.meraki.networks_wireless_ssids`. The existing `meraki_compliance` role gets two new post-tasks for alerting (GitHub Issue creation via `community.general.github_issue`, Webex Teams via `ansible.builtin.uri`). Two GitHub Actions workflows orchestrate the automation: `deploy-ssids.yml` (deploys SSIDs on push to main or manual dispatch) and `compliance.yml` (checks compliance on schedule, webhook, or manual dispatch). Both workflows run Ansible inside the GitHub Actions runner.

**Tech Stack:** Ansible 2.20.2, `cisco.meraki` collection 2.22.0, `community.general` 9.0.0, GitHub Actions, Webex Teams Incoming Webhook, Meraki Dashboard API v1

---

## Task 0: Clean Up the Repo — Remove Unused Files

Delete stubs, Part 2 content, old docs, and example files that are no longer needed. This gives us a clean starting point.

**Files to delete:**
- `playbooks/bulk_ap_deploy.yml`
- `playbooks/group_policy_drift.yml`
- `roles/meraki_devices/` (entire directory)
- `roles/meraki_group_policy_drift/` (entire directory)
- `inventory/compliance_example.yml.example`
- `group_vars/compliance_example.yml.example`
- `docs/HOST_BRIEFING.md`
- `docs/GROUP_POLICY_DRIFT.md`
- `PROJECT_SUMMARY.md`

**Files to update (references to removed content):**
- `group_vars/all.yml` — remove the `meraki_group_policies` section (lines 116-176) since group policy drift is deleted
- `docs/ARCHITECTURE.md` — will be updated in a later task
- `README.md` — will be updated in a later task

### Step 1: Delete files and directories

```bash
rm -f playbooks/bulk_ap_deploy.yml
rm -f playbooks/group_policy_drift.yml
rm -rf roles/meraki_devices/
rm -rf roles/meraki_group_policy_drift/
rm -f inventory/compliance_example.yml.example
rm -f group_vars/compliance_example.yml.example
rm -f docs/HOST_BRIEFING.md
rm -f docs/GROUP_POLICY_DRIFT.md
rm -f PROJECT_SUMMARY.md
```

### Step 2: Clean up group_vars/all.yml

Remove the entire `# Group Policy Configuration - Source of Truth` section from `group_vars/all.yml` (the `meraki_group_policies` block from line ~116 through line ~176). Keep everything else.

### Step 3: Update README.md playbooks list

Replace the playbooks section in README.md:

```markdown
### Playbooks

- **`ssid_management.yml`** - Deploy and configure wireless SSIDs across networks
- **`compliance_check.yml`** - Validate SSID configurations against desired state and security baselines
- **`config_snapshot.yml`** - Capture live Meraki config and store as GitOps baseline
```

And update the key features:

```markdown
### Key Features

- ✅ **GitOps for Wireless** - Config stored in Git, drift detected automatically
- ✅ **Security Baselines** - No open auth, WPA2 minimum, guest bandwidth limits
- ✅ **Automated Alerting** - GitHub Issues + Webex Teams on compliance violations
- ✅ **CI/CD Native** - Everything runs in GitHub Actions (deploy, check, alert, snapshot)
- ✅ **Idempotent Operations** - Safe to run multiple times
- ✅ **Environment-Aware** - Separate configs for sandbox and production
```

### Step 4: Update README.md documentation links

Replace the documentation section:

```markdown
## 📚 Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Setup guide with GitHub Actions configuration
- **[Architecture](docs/ARCHITECTURE.md)** - Project structure and data flow
- **[Compliance](docs/COMPLIANCE.md)** - SSID compliance checking and security baselines
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common errors and solutions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
```

### Step 5: Update README.md project structure

Replace the project structure section:

```markdown
## 📖 Project Structure

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
│   ├── sandbox.yml
│   └── sandbox_compliance.yml
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
```

### Step 6: Verify no broken references

Run: `rg -l "bulk_ap_deploy\|group_policy_drift\|meraki_devices\|HOST_BRIEFING\|GROUP_POLICY_DRIFT\|PROJECT_SUMMARY" --glob '!docs/plans/*'`
Expected: No results (or only the files we plan to update in later tasks)

### Step 7: Commit

```bash
git add -A
git commit -m "chore: clean up repo — remove stubs, Part 2 content, and old docs

Removed:
- bulk_ap_deploy.yml playbook and meraki_devices role (stubs)
- group_policy_drift.yml playbook and meraki_group_policy_drift role (Part 2)
- HOST_BRIEFING.md, GROUP_POLICY_DRIFT.md, PROJECT_SUMMARY.md
- Old example inventory and group_vars files

Updated README.md with new project structure, features, and docs links.
Cleaned group_vars/all.yml of group policy config."
```

---

## Task 1: Build Out the `meraki_ssid` Role

The existing role is a stub. We need it to actually create/update SSIDs.

**Files:**
- Modify: `roles/meraki_ssid/defaults/main.yml`
- Modify: `roles/meraki_ssid/tasks/main.yml`
- Modify: `roles/meraki_ssid/handlers/main.yml`

### Step 1: Replace defaults with full SSID variable structure

Replace `roles/meraki_ssid/defaults/main.yml` with:

```yaml
---
meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('', true)) }}"
meraki_network_id: "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('', true)) }}"

meraki_ssid_configs: "{{ meraki_ssids | default([]) }}"

meraki_ssid_api_retries: "{{ meraki_api_retries | default(3) }}"
meraki_ssid_api_retry_delay: "{{ meraki_api_retry_delay | default(2) }}"
```

### Step 2: Replace tasks with working SSID management

Replace `roles/meraki_ssid/tasks/main.yml` with:

```yaml
---
- name: Validate required variables
  ansible.builtin.assert:
    that:
      - meraki_api_key | length > 0
      - meraki_org_id | length > 0
      - meraki_network_id | length > 0
      - meraki_ssid_configs | length > 0
    fail_msg: >-
      Missing required variables. Ensure MERAKI_DASHBOARD_API_KEY,
      meraki_org_id, meraki_network_id, and meraki_ssid_configs are set.
    quiet: true
  tags:
    - ssid
    - validate

- name: Display SSID deployment plan
  ansible.builtin.debug:
    msg: "Will configure {{ meraki_ssid_configs | length }} SSID(s) on network {{ meraki_network_id }}"
  tags:
    - ssid

- name: Get current SSIDs from Meraki
  cisco.meraki.networks_wireless_ssids_info:
    networkId: "{{ meraki_network_id }}"
    meraki_api_key: "{{ meraki_api_key }}"
  register: current_ssids_result
  retries: "{{ meraki_ssid_api_retries }}"
  delay: "{{ meraki_ssid_api_retry_delay }}"
  until: current_ssids_result is not failed
  tags:
    - ssid
    - gather

- name: Find matching SSID slot for each desired SSID
  ansible.builtin.set_fact:
    ssid_slot_map: >-
      {{
        ssid_slot_map | default([]) + [{
          'config': item,
          'number': (current_ssids_result.meraki_response | default([])
            | selectattr('name', 'equalto', item.name)
            | map(attribute='number') | first
            | default(
              current_ssids_result.meraki_response | default([])
              | selectattr('name', 'match', '^Unconfigured SSID')
              | map(attribute='number') | first
              | default(-1)
            ))
        }]
      }}
  loop: "{{ meraki_ssid_configs }}"
  loop_control:
    label: "{{ item.name }}"
  tags:
    - ssid

- name: Configure SSIDs on Meraki network
  cisco.meraki.networks_wireless_ssids:
    networkId: "{{ meraki_network_id }}"
    number: "{{ item.number }}"
    meraki_api_key: "{{ meraki_api_key }}"
    name: "{{ item.config.name }}"
    enabled: "{{ item.config.enabled | default(true) }}"
    authMode: "{{ item.config.authMode | default('psk') }}"
    encryptionMode: "{{ item.config.encryptionMode | default('wpa2') }}"
    psk: "{{ item.config.psk | default(omit) }}"
    wpaEncryptionMode: "{{ item.config.wpaEncryptionMode | default(omit) }}"
    minBitrate: "{{ item.config.minBitrate | default(omit) }}"
    bandSelection: "{{ item.config.bandSelection | default(omit) }}"
    perClientBandwidthLimitUp: "{{ item.config.perClientBandwidthLimitUp | default(omit) }}"
    perClientBandwidthLimitDown: "{{ item.config.perClientBandwidthLimitDown | default(omit) }}"
    visible: "{{ item.config.visible | default(true) }}"
    availableOnAllAps: "{{ item.config.availableOnAllAps | default(true) }}"
    splashPage: "{{ item.config.splashPage | default(omit) }}"
  loop: "{{ ssid_slot_map | default([]) }}"
  loop_control:
    label: "{{ item.config.name }} -> slot {{ item.number }}"
  when: item.number >= 0
  retries: "{{ meraki_ssid_api_retries }}"
  delay: "{{ meraki_ssid_api_retry_delay }}"
  register: ssid_results
  notify: log ssid changes
  tags:
    - ssid
    - configure

- name: Display SSID deployment results
  ansible.builtin.debug:
    msg: >-
      SSID "{{ item.config.name }}" configured successfully
      on slot {{ item.number }}
  loop: "{{ ssid_slot_map | default([]) }}"
  loop_control:
    label: "{{ item.config.name }}"
  when: item.number >= 0
  tags:
    - ssid

- name: Warn about SSIDs that could not be assigned a slot
  ansible.builtin.debug:
    msg: >-
      WARNING: SSID "{{ item.config.name }}" could not be assigned a slot.
      All 15 SSID slots may be in use. Free a slot in Meraki Dashboard first.
  loop: "{{ ssid_slot_map | default([]) }}"
  loop_control:
    label: "{{ item.config.name }}"
  when: item.number < 0
  tags:
    - ssid
```

### Step 3: Replace handler with a logging handler

Replace `roles/meraki_ssid/handlers/main.yml` with:

```yaml
---
- name: log ssid changes
  ansible.builtin.debug:
    msg: "SSID configuration changes have been applied to network {{ meraki_network_id }}"
```

### Step 4: Verify syntax

Run: `ansible-playbook --syntax-check playbooks/ssid_management.yml`
Expected: Syntax check passes

### Step 5: Commit

```bash
git add roles/meraki_ssid/
git commit -m "feat(ssid): build out meraki_ssid role with full SSID management

Replaces stub with working role that creates/updates SSIDs via
cisco.meraki.networks_wireless_ssids. Includes variable validation,
slot auto-detection, retry logic, and idempotent configuration."
```

---

## Task 2: Update the SSID Management Playbook

The playbook needs network-level targeting and proper variable wiring.

**Files:**
- Modify: `playbooks/ssid_management.yml`

### Step 1: Replace playbook with network-aware version

Replace `playbooks/ssid_management.yml` with:

```yaml
---
# SSID Management Playbook
# Deploys and configures wireless SSIDs across Meraki networks
#
# Usage:
#   ansible-playbook playbooks/ssid_management.yml -i inventory/sandbox.yml
#
#   # Dry-run mode
#   ansible-playbook playbooks/ssid_management.yml -i inventory/sandbox.yml --check --diff

- name: Deploy Meraki SSIDs
  hosts: meraki_orgs
  gather_facts: false
  become: false

  pre_tasks:
    - name: Load API key from environment
      ansible.builtin.set_fact:
        meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
      no_log: true
      tags: always

    - name: Verify API key is available
      ansible.builtin.assert:
        that:
          - meraki_api_key | length > 0
        fail_msg: "MERAKI_DASHBOARD_API_KEY environment variable or vault_meraki_api_key must be set"
        quiet: true
      tags: always

  roles:
    - role: meraki_ssid
      vars:
        meraki_ssid_configs: "{{ meraki_ssids | default([]) }}"

  post_tasks:
    - name: SSID deployment summary
      ansible.builtin.debug:
        msg: |
          SSID deployment complete!
          Network: {{ meraki_network_id | default('N/A') }}
          SSIDs configured: {{ meraki_ssids | default([]) | length }}
      tags: always
```

### Step 2: Verify syntax

Run: `ansible-playbook --syntax-check playbooks/ssid_management.yml`
Expected: Syntax check passes

### Step 3: Commit

```bash
git add playbooks/ssid_management.yml
git commit -m "feat(ssid): update ssid_management playbook with pre-task validation"
```

---

## Task 3: Add Compliance Alerting — GitHub Issue + Webex Teams

Extend the compliance playbook with two post-task alert mechanisms.

**Files:**
- Modify: `playbooks/compliance_check.yml`
- Modify: `roles/meraki_compliance/defaults/main.yml`

### Step 1: Add alerting defaults

Append to `roles/meraki_compliance/defaults/main.yml` after the existing content:

```yaml

# Alerting configuration
compliance_alerting_enabled: true

# GitHub Issue alerting
compliance_github_alert_enabled: true
compliance_github_repo: ""
compliance_github_token: "{{ lookup('env', 'GITHUB_TOKEN') | default('', true) }}"

# Webex Teams alerting
compliance_webex_alert_enabled: true
compliance_webex_webhook_url: "{{ lookup('env', 'WEBEX_WEBHOOK_URL') | default('', true) }}"
```

### Step 2: Add alerting post-tasks to the compliance playbook

Replace the `post_tasks` section in `playbooks/compliance_check.yml` (everything from line 55 `post_tasks:` onward) with:

```yaml
  post_tasks:
    - name: Display compliance summary
      ansible.builtin.debug:
        msg: |
          Compliance check completed!

          Total Networks Checked: {{ compliance_results.networks_checked | default(0) }}
          Networks Compliant: {{ compliance_results.networks_compliant | default(0) }}
          Networks Non-Compliant: {{ compliance_results.networks_non_compliant | default(0) }}
          Total SSIDs Checked: {{ compliance_results.ssids_checked | default(0) }}
          SSIDs Compliant: {{ compliance_results.ssids_compliant | default(0) }}
          SSIDs Non-Compliant: {{ compliance_results.ssids_non_compliant | default(0) }}

          Report saved to: {{ compliance_report_dir }}/{{ compliance_report_filename }}
      when: compliance_results is defined
      run_once: true
      tags: always

    - name: Set compliance failure flag
      ansible.builtin.set_fact:
        compliance_failed: "{{ (compliance_results.networks_non_compliant | default(0) | int) > 0 }}"
      when: compliance_results is defined
      run_once: true
      tags: always

    - name: Build violation summary for alerts
      ansible.builtin.set_fact:
        violation_summary: |
          Meraki Wireless Compliance Violation Detected

          Networks Checked: {{ compliance_results.networks_checked | default(0) }}
          Networks Non-Compliant: {{ compliance_results.networks_non_compliant | default(0) }}
          SSIDs Non-Compliant: {{ compliance_results.ssids_non_compliant | default(0) }}

          {% for network in compliance_results.network_details | default([]) %}
          {% if not network.compliant %}
          Network: {{ network.network_name }} ({{ network.network_id }})
          {% for ssid in network.ssids %}
          {% if ssid.drift_detected %}
            SSID "{{ ssid.name }}":
          {% for field, values in ssid.differences.items() %}
              {{ field }}: {{ values.current }} -> {{ values.desired }}
          {% endfor %}
          {% endif %}
          {% endfor %}
          {% endif %}
          {% endfor %}
      when:
        - compliance_results is defined
        - compliance_failed | default(false) | bool
      run_once: true
      tags: always

    - name: Create GitHub Issue for compliance violation
      community.general.github_issue:
        repo: "{{ compliance_github_repo }}"
        token: "{{ compliance_github_token }}"
        title: "Wireless Compliance Violation - {{ ansible_date_time.date }}"
        body: |
          ## Wireless Compliance Violation Detected

          **Date:** {{ ansible_date_time.iso8601 }}
          **Severity:** High

          ### Summary

          | Metric | Count |
          |--------|-------|
          | Networks Checked | {{ compliance_results.networks_checked }} |
          | Networks Non-Compliant | {{ compliance_results.networks_non_compliant }} |
          | SSIDs Non-Compliant | {{ compliance_results.ssids_non_compliant }} |

          ### Details

          {% for network in compliance_results.network_details | default([]) %}
          {% if not network.compliant %}
          #### Network: {{ network.network_name }}

          | SSID | Field | Current | Desired |
          |------|-------|---------|---------|
          {% for ssid in network.ssids %}
          {% if ssid.drift_detected %}
          {% for field, values in ssid.differences.items() %}
          | {{ ssid.name }} | `{{ field }}` | `{{ values.current }}` | `{{ values.desired }}` |
          {% endfor %}
          {% endif %}
          {% endfor %}
          {% endif %}
          {% endfor %}

          ### Remediation

          Run the SSID management playbook to restore compliance:
          ```
          ansible-playbook playbooks/ssid_management.yml -i inventory/sandbox.yml
          ```

          ---
          *Auto-generated by Ansible Compliance Check*
        labels:
          - compliance-violation
          - wireless
          - automated
        action: create
      delegate_to: localhost
      run_once: true
      when:
        - compliance_failed | default(false) | bool
        - compliance_github_alert_enabled | default(false) | bool
        - compliance_github_repo | default('') | length > 0
        - compliance_github_token | default('') | length > 0
      tags:
        - alerting
        - github

    - name: Send Webex Teams notification for compliance violation
      ansible.builtin.uri:
        url: "{{ compliance_webex_webhook_url }}"
        method: POST
        headers:
          Content-Type: "application/json"
        body_format: json
        body:
          markdown: |
            ## ⚠️ Wireless Compliance Violation

            **Date:** {{ ansible_date_time.iso8601 }}

            **{{ compliance_results.networks_non_compliant }} network(s)** and **{{ compliance_results.ssids_non_compliant }} SSID(s)** are non-compliant.

            {% for network in compliance_results.network_details | default([]) %}
            {% if not network.compliant %}
            **Network: {{ network.network_name }}**
            {% for ssid in network.ssids %}
            {% if ssid.drift_detected %}
            - SSID `{{ ssid.name }}`: {% for field, values in ssid.differences.items() %}`{{ field }}` changed from `{{ values.current }}` to `{{ values.desired }}`{% if not loop.last %}, {% endif %}{% endfor %}

            {% endif %}
            {% endfor %}
            {% endif %}
            {% endfor %}

            **Remediation:** `ansible-playbook playbooks/ssid_management.yml`
        status_code: 200
        validate_certs: true
      delegate_to: localhost
      run_once: true
      when:
        - compliance_failed | default(false) | bool
        - compliance_webex_alert_enabled | default(false) | bool
        - compliance_webex_webhook_url | default('') | length > 0
      tags:
        - alerting
        - webex

    - name: Compliance check passed - no alerts needed
      ansible.builtin.debug:
        msg: "All networks are compliant. No alerts triggered."
      when:
        - compliance_results is defined
        - not (compliance_failed | default(false) | bool)
      run_once: true
      tags: always
```

### Step 3: Verify syntax

Run: `ansible-playbook --syntax-check playbooks/compliance_check.yml`
Expected: Syntax check passes

### Step 4: Commit

```bash
git add playbooks/compliance_check.yml roles/meraki_compliance/defaults/main.yml
git commit -m "feat(compliance): add GitHub Issue + Webex Teams alerting on violations

When compliance check detects drift, automatically creates a GitHub
Issue with violation details and sends a Webex Teams webhook message.
Both alert channels are independently toggleable via variables."
```

---

## Task 4: Add Security Baseline Checks to Compliance Role

The compliance role currently only checks drift (desired vs. actual). Add security baseline checks that apply to ALL enabled SSIDs regardless of desired state.

**Files:**
- Create: `roles/meraki_compliance/tasks/security_baseline.yml`
- Modify: `roles/meraki_compliance/tasks/main.yml`
- Modify: `roles/meraki_compliance/defaults/main.yml`

### Step 1: Add security baseline defaults

Append to `roles/meraki_compliance/defaults/main.yml` after the alerting config block:

```yaml

# Security baseline checks (applied to all enabled SSIDs)
security_baseline_enabled: true

security_baseline_rules:
  no_open_auth:
    enabled: true
    severity: "critical"
    description: "Enabled SSIDs must not use open authentication"
  minimum_encryption:
    enabled: true
    severity: "critical"
    minimum: "wpa2"
    description: "Enabled SSIDs must use WPA2 or higher encryption"
  guest_bandwidth_limits:
    enabled: true
    severity: "warning"
    guest_ssid_pattern: "(?i)guest"
    description: "Guest SSIDs must have bandwidth limits configured"
  disabled_ssid_broadcast:
    enabled: true
    severity: "warning"
    description: "Disabled SSIDs should not be broadcasting"
```

### Step 2: Create the security baseline task file

Create `roles/meraki_compliance/tasks/security_baseline.yml`:

```yaml
---
- name: Initialize security baseline results
  ansible.builtin.set_fact:
    security_violations: []
  tags:
    - compliance
    - security

- name: Check for open authentication on enabled SSIDs
  ansible.builtin.set_fact:
    security_violations: >-
      {{ security_violations + [{
        'ssid_name': item.name | default('Unknown'),
        'ssid_number': item.number | default(0),
        'rule': 'no_open_auth',
        'severity': 'critical',
        'message': 'SSID "' + item.name | default('Unknown') + '" uses open authentication — no encryption protecting wireless traffic',
        'current_value': item.authMode | default('unknown'),
        'expected': 'psk, 8021x, or other authenticated mode'
      }] }}
  loop: "{{ current_ssids.data | default([]) }}"
  loop_control:
    label: "{{ item.name | default('SSID ' + (loop.index0 | string)) }}"
  when:
    - security_baseline_rules.no_open_auth.enabled | default(true)
    - item.enabled | default(false) | bool
    - item.authMode | default('') == 'open'
  tags:
    - compliance
    - security

- name: Check minimum encryption standard on enabled SSIDs
  ansible.builtin.set_fact:
    security_violations: >-
      {{ security_violations + [{
        'ssid_name': item.name | default('Unknown'),
        'ssid_number': item.number | default(0),
        'rule': 'minimum_encryption',
        'severity': 'critical',
        'message': 'SSID "' + item.name | default('Unknown') + '" uses weak encryption (' + item.encryptionMode | default('none') + ') — WPA2 minimum required',
        'current_value': item.encryptionMode | default('none'),
        'expected': 'wpa2 or higher'
      }] }}
  loop: "{{ current_ssids.data | default([]) }}"
  loop_control:
    label: "{{ item.name | default('SSID ' + (loop.index0 | string)) }}"
  when:
    - security_baseline_rules.minimum_encryption.enabled | default(true)
    - item.enabled | default(false) | bool
    - item.authMode | default('open') != 'open'
    - item.encryptionMode | default('none') not in ['wpa2', 'wpa3', 'wpa2-eap', 'wpa3-eap', 'wpa2-sha256']
  tags:
    - compliance
    - security

- name: Check guest SSIDs have bandwidth limits
  ansible.builtin.set_fact:
    security_violations: >-
      {{ security_violations + [{
        'ssid_name': item.name | default('Unknown'),
        'ssid_number': item.number | default(0),
        'rule': 'guest_bandwidth_limits',
        'severity': 'warning',
        'message': 'Guest SSID "' + item.name | default('Unknown') + '" has no bandwidth limits — guests could consume all available bandwidth',
        'current_value': 'Upload: ' + (item.perClientBandwidthLimitUp | default(0) | string) + ', Download: ' + (item.perClientBandwidthLimitDown | default(0) | string),
        'expected': 'Bandwidth limits > 0 for both upload and download'
      }] }}
  loop: "{{ current_ssids.data | default([]) }}"
  loop_control:
    label: "{{ item.name | default('SSID ' + (loop.index0 | string)) }}"
  when:
    - security_baseline_rules.guest_bandwidth_limits.enabled | default(true)
    - item.enabled | default(false) | bool
    - item.name | default('') | regex_search(security_baseline_rules.guest_bandwidth_limits.guest_ssid_pattern | default('(?i)guest'))
    - (item.perClientBandwidthLimitUp | default(0) | int) == 0
    - (item.perClientBandwidthLimitDown | default(0) | int) == 0
  tags:
    - compliance
    - security

- name: Check disabled SSIDs are not broadcasting
  ansible.builtin.set_fact:
    security_violations: >-
      {{ security_violations + [{
        'ssid_name': item.name | default('Unknown'),
        'ssid_number': item.number | default(0),
        'rule': 'disabled_ssid_broadcast',
        'severity': 'warning',
        'message': 'Disabled SSID "' + item.name | default('Unknown') + '" is still broadcasting — should be hidden',
        'current_value': 'visible: ' + (item.visible | default(false) | string),
        'expected': 'visible: false when SSID is disabled'
      }] }}
  loop: "{{ current_ssids.data | default([]) }}"
  loop_control:
    label: "{{ item.name | default('SSID ' + (loop.index0 | string)) }}"
  when:
    - security_baseline_rules.disabled_ssid_broadcast.enabled | default(true)
    - not (item.enabled | default(false) | bool)
    - item.visible | default(false) | bool
  tags:
    - compliance
    - security

- name: Display security baseline results
  ansible.builtin.debug:
    msg: |
      Security Baseline Check: {{ 'PASS' if (security_violations | length == 0) else 'FAIL' }}
      Critical violations: {{ security_violations | selectattr('severity', 'equalto', 'critical') | list | length }}
      Warning violations: {{ security_violations | selectattr('severity', 'equalto', 'warning') | list | length }}

      {% for violation in security_violations %}
      [{{ violation.severity | upper }}] {{ violation.message }}
        Current: {{ violation.current_value }}
        Expected: {{ violation.expected }}
      {% endfor %}
  tags:
    - compliance
    - security

- name: Merge security violations into compliance results
  ansible.builtin.set_fact:
    compliance_results: >-
      {{
        compliance_results | combine({
          'security_violations': security_violations,
          'security_critical_count': security_violations | selectattr('severity', 'equalto', 'critical') | list | length,
          'security_warning_count': security_violations | selectattr('severity', 'equalto', 'warning') | list | length,
          'security_passed': (security_violations | length == 0)
        })
      }}
  tags:
    - compliance
    - security

- name: Mark compliance as failed if critical security violations found
  ansible.builtin.set_fact:
    compliance_results: >-
      {{
        compliance_results | combine({
          'networks_non_compliant': compliance_results.networks_non_compliant + (1 if (security_violations | selectattr('severity', 'equalto', 'critical') | list | length > 0) else 0)
        })
      }}
  when: security_violations | selectattr('severity', 'equalto', 'critical') | list | length > 0
  tags:
    - compliance
    - security
```

### Step 3: Include security baseline in main tasks

Add the following at the end of `roles/meraki_compliance/tasks/main.yml` (after the existing "Display drift detection summary" task):

```yaml

- name: Run security baseline checks
  ansible.builtin.include_tasks: security_baseline.yml
  when:
    - security_baseline_enabled | default(true) | bool
    - current_ssids.data is defined
    - current_ssids.data | length > 0
  tags:
    - compliance
    - security
```

### Step 4: Verify syntax

Run: `ansible-playbook --syntax-check playbooks/compliance_check.yml`
Expected: Syntax check passes

### Step 5: Commit

```bash
git add roles/meraki_compliance/
git commit -m "feat(compliance): add security baseline checks for all enabled SSIDs

Checks applied independent of desired state:
- No open authentication on enabled SSIDs (critical)
- WPA2 minimum encryption required (critical)
- Guest SSIDs must have bandwidth limits (warning)
- Disabled SSIDs should not broadcast (warning)

Critical violations trigger the same alerting pipeline
(GitHub Issues + Webex Teams) as drift detection."
```

---

## Task 5: GitOps Configuration Baseline — Store Meraki Config in GitHub

Pull the live Meraki configuration, store it as YAML in the repo, and compare against it on future runs. Any change made outside the repo (manual Dashboard edits) is detected as drift.

**Files:**
- Create: `playbooks/config_snapshot.yml`
- Create: `roles/meraki_snapshot/tasks/main.yml`
- Create: `roles/meraki_snapshot/defaults/main.yml`
- Create: `baselines/.gitkeep`

### Step 1: Create role defaults

Create `roles/meraki_snapshot/defaults/main.yml`:

```yaml
---
meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('', true)) }}"
meraki_network_id: "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('', true)) }}"

snapshot_base_dir: "{{ playbook_dir }}/../baselines"
snapshot_api_retries: "{{ meraki_api_retries | default(3) }}"
snapshot_api_retry_delay: "{{ meraki_api_retry_delay | default(2) }}"

# Fields to capture in snapshot (sensitive fields like PSK are excluded)
snapshot_ssid_fields:
  - name
  - number
  - enabled
  - authMode
  - encryptionMode
  - wpaEncryptionMode
  - visible
  - bandSelection
  - minBitrate
  - perClientBandwidthLimitUp
  - perClientBandwidthLimitDown
  - splashPage
  - availableOnAllAps
```

### Step 2: Create role tasks

Create `roles/meraki_snapshot/tasks/main.yml`:

```yaml
---
- name: Validate required variables
  ansible.builtin.assert:
    that:
      - meraki_api_key | length > 0
      - meraki_network_id | length > 0
    fail_msg: "MERAKI_DASHBOARD_API_KEY and meraki_network_id must be set"
    quiet: true
  tags:
    - snapshot

- name: Ensure baselines directory exists
  ansible.builtin.file:
    path: "{{ snapshot_base_dir }}/{{ meraki_network_id }}"
    state: directory
    mode: '0755'
  delegate_to: localhost
  tags:
    - snapshot

- name: Pull current SSID configuration from Meraki
  cisco.meraki.networks_wireless_ssids_info:
    networkId: "{{ meraki_network_id }}"
    meraki_api_key: "{{ meraki_api_key }}"
  register: snapshot_ssids
  retries: "{{ snapshot_api_retries }}"
  delay: "{{ snapshot_api_retry_delay }}"
  until: snapshot_ssids is not failed
  tags:
    - snapshot

- name: Filter SSID data to safe fields only
  ansible.builtin.set_fact:
    filtered_ssids: >-
      {{
        snapshot_ssids.meraki_response | default([])
        | map('dict2items')
        | map('selectattr', 'key', 'in', snapshot_ssid_fields)
        | map('items2dict')
        | list
      }}
  tags:
    - snapshot

- name: Load previous baseline if it exists
  ansible.builtin.slurp:
    src: "{{ snapshot_base_dir }}/{{ meraki_network_id }}/ssids.yml"
  register: previous_baseline_raw
  failed_when: false
  delegate_to: localhost
  tags:
    - snapshot

- name: Parse previous baseline
  ansible.builtin.set_fact:
    previous_baseline: "{{ (previous_baseline_raw.content | default('') | b64decode | from_yaml).ssids | default([]) }}"
  when: previous_baseline_raw.content is defined
  failed_when: false
  tags:
    - snapshot

- name: Set empty baseline if none exists
  ansible.builtin.set_fact:
    previous_baseline: []
  when: previous_baseline is not defined
  tags:
    - snapshot

- name: Compare live config against stored baseline
  ansible.builtin.set_fact:
    baseline_drift_detected: "{{ filtered_ssids | to_json != previous_baseline | to_json }}"
  tags:
    - snapshot

- name: Report baseline comparison result
  ansible.builtin.debug:
    msg: >-
      {{ 'DRIFT DETECTED: Live config differs from stored baseline.'
         if baseline_drift_detected | bool
         else 'No drift: Live config matches stored baseline.' }}
  tags:
    - snapshot

- name: Save current config as new baseline
  ansible.builtin.copy:
    content: |
      ---
      # Meraki SSID Configuration Baseline
      # Network: {{ meraki_network_id }}
      # Captured: {{ ansible_date_time.iso8601 }}
      # Auto-generated by config_snapshot playbook — do not edit manually

      ssids:
      {{ filtered_ssids | to_nice_yaml(indent=2) | indent(2, first=true) }}
    dest: "{{ snapshot_base_dir }}/{{ meraki_network_id }}/ssids.yml"
    mode: '0644'
  delegate_to: localhost
  tags:
    - snapshot

- name: Set snapshot results for downstream use
  ansible.builtin.set_fact:
    snapshot_results:
      network_id: "{{ meraki_network_id }}"
      ssids_captured: "{{ filtered_ssids | length }}"
      baseline_drift_detected: "{{ baseline_drift_detected }}"
      baseline_path: "{{ snapshot_base_dir }}/{{ meraki_network_id }}/ssids.yml"
      timestamp: "{{ ansible_date_time.iso8601 }}"
  tags:
    - snapshot
```

### Step 3: Create the snapshot playbook

Create `playbooks/config_snapshot.yml`:

```yaml
---
# Configuration Snapshot Playbook
# Pulls live Meraki config and stores it in baselines/ for GitOps drift detection
#
# Usage:
#   ansible-playbook playbooks/config_snapshot.yml -i inventory/sandbox_compliance.yml
#
# This playbook is designed to run in GitHub Actions after compliance checks.
# The baselines/ directory is committed back to the repo automatically.

- name: Capture Meraki Configuration Baseline
  hosts: meraki_networks
  gather_facts: true
  become: false

  roles:
    - role: meraki_snapshot

  post_tasks:
    - name: Snapshot summary
      ansible.builtin.debug:
        msg: |
          Configuration snapshot complete!
          Network: {{ snapshot_results.network_id }}
          SSIDs captured: {{ snapshot_results.ssids_captured }}
          Baseline drift detected: {{ snapshot_results.baseline_drift_detected }}
          Saved to: {{ snapshot_results.baseline_path }}
      when: snapshot_results is defined
      tags: always
```

### Step 4: Create the baselines directory placeholder

Run: `mkdir -p baselines && touch baselines/.gitkeep`

### Step 5: Verify syntax

Run: `ansible-playbook --syntax-check playbooks/config_snapshot.yml`
Expected: Syntax check passes

### Step 6: Commit

```bash
git add roles/meraki_snapshot/ playbooks/config_snapshot.yml baselines/
git commit -m "feat(gitops): add config snapshot role for baseline drift detection

New meraki_snapshot role pulls live SSID config from Meraki, filters
to safe fields (excluding secrets like PSK), and stores as YAML in
baselines/<network_id>/ssids.yml. Compares against previous baseline
to detect drift from manual Dashboard changes.

Designed to run in GitHub Actions with auto-commit of baseline changes."
```

---

## Task 6: Create GitHub Actions Workflows — Deploy + Compliance

All Ansible playbooks run inside GitHub Actions runners. Two workflows:
- `deploy-ssids.yml` — deploys SSIDs when config changes are pushed or on manual dispatch
- `compliance.yml` — checks compliance on schedule, webhook, or manual dispatch

**Files:**
- Create: `.github/workflows/deploy-ssids.yml`
- Create: `.github/workflows/compliance.yml`

### Step 1: Create the SSID deployment workflow

Create `.github/workflows/deploy-ssids.yml`:

```yaml
name: Deploy SSIDs

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'sandbox'
        type: choice
        options:
          - sandbox
          - production
      dry_run:
        description: 'Dry run (check mode only)'
        required: true
        default: true
        type: boolean

  push:
    branches:
      - main
    paths:
      - 'group_vars/**'
      - 'roles/meraki_ssid/**'
      - 'playbooks/ssid_management.yml'

permissions:
  contents: read

jobs:
  deploy:
    name: Deploy SSIDs to Meraki
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Cache Ansible Galaxy collections
        uses: actions/cache@v4
        with:
          path: ~/.ansible/collections
          key: ${{ runner.os }}-ansible-galaxy-${{ hashFiles('requirements.yml') }}
          restore-keys: |
            ${{ runner.os }}-ansible-galaxy-

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          ansible-galaxy collection install -r requirements.yml

      - name: Deploy SSIDs
        env:
          MERAKI_DASHBOARD_API_KEY: ${{ secrets.MERAKI_DASHBOARD_API_KEY }}
          MERAKI_ORG_ID: ${{ secrets.MERAKI_ORG_ID }}
          MERAKI_NETWORK_ID: ${{ secrets.MERAKI_NETWORK_ID }}
        run: |
          EXTRA_ARGS=""
          if [ "${{ github.event.inputs.dry_run }}" = "true" ] || [ "${{ github.event_name }}" = "push" ]; then
            echo "Running in CHECK MODE (dry run)"
            EXTRA_ARGS="--check --diff"
          else
            echo "Running in LIVE MODE — SSIDs will be configured"
          fi

          ansible-playbook playbooks/ssid_management.yml \
            -i inventory/sandbox.yml \
            -e "vault_meraki_api_key=${MERAKI_DASHBOARD_API_KEY}" \
            -e "vault_meraki_org_id=${MERAKI_ORG_ID}" \
            -e "vault_meraki_network_id_1=${MERAKI_NETWORK_ID}" \
            -e "meraki_network_id=${MERAKI_NETWORK_ID}" \
            $EXTRA_ARGS

  compliance:
    name: Post-Deploy Compliance Check
    needs: deploy
    if: github.event.inputs.dry_run != 'true'
    uses: ./.github/workflows/compliance.yml
    secrets: inherit
```

### Step 2: Create the compliance workflow

Create `.github/workflows/compliance.yml`:

```yaml
name: Wireless Compliance Check

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'sandbox'
        type: choice
        options:
          - sandbox
          - production

  workflow_call:
    secrets:
      MERAKI_DASHBOARD_API_KEY:
        required: true
      MERAKI_ORG_ID:
        required: true
      MERAKI_NETWORK_ID:
        required: true
      WEBEX_WEBHOOK_URL:
        required: false

  schedule:
    - cron: '0 */6 * * *'

  repository_dispatch:
    types: [meraki-config-change]

permissions:
  issues: write
  contents: write

jobs:
  compliance-check:
    name: Run Compliance Check
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Cache Ansible Galaxy collections
        uses: actions/cache@v4
        with:
          path: ~/.ansible/collections
          key: ${{ runner.os }}-ansible-galaxy-${{ hashFiles('requirements.yml') }}
          restore-keys: |
            ${{ runner.os }}-ansible-galaxy-

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          ansible-galaxy collection install -r requirements.yml

      - name: Determine trigger source
        id: trigger
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            echo "source=manual" >> "$GITHUB_OUTPUT"
          elif [ "${{ github.event_name }}" = "schedule" ]; then
            echo "source=scheduled" >> "$GITHUB_OUTPUT"
          elif [ "${{ github.event_name }}" = "repository_dispatch" ]; then
            echo "source=webhook (Meraki config change)" >> "$GITHUB_OUTPUT"
          elif [ "${{ github.event_name }}" = "workflow_call" ]; then
            echo "source=post-deploy" >> "$GITHUB_OUTPUT"
          fi

      - name: Run compliance check
        env:
          MERAKI_DASHBOARD_API_KEY: ${{ secrets.MERAKI_DASHBOARD_API_KEY }}
          MERAKI_ORG_ID: ${{ secrets.MERAKI_ORG_ID }}
          MERAKI_NETWORK_ID: ${{ secrets.MERAKI_NETWORK_ID }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          WEBEX_WEBHOOK_URL: ${{ secrets.WEBEX_WEBHOOK_URL }}
        run: |
          echo "Trigger: ${{ steps.trigger.outputs.source }}"
          echo ""

          ansible-playbook playbooks/compliance_check.yml \
            -i inventory/sandbox_compliance.yml \
            -e "vault_meraki_api_key=${MERAKI_DASHBOARD_API_KEY}" \
            -e "vault_meraki_org_id=${MERAKI_ORG_ID}" \
            -e "vault_meraki_network_id_1=${MERAKI_NETWORK_ID}" \
            -e "compliance_github_repo=${{ github.repository }}" \
            -e "compliance_github_token=${GITHUB_TOKEN}" \
            -e "compliance_webex_webhook_url=${WEBEX_WEBHOOK_URL}"

      - name: Snapshot current config to baselines
        env:
          MERAKI_DASHBOARD_API_KEY: ${{ secrets.MERAKI_DASHBOARD_API_KEY }}
          MERAKI_ORG_ID: ${{ secrets.MERAKI_ORG_ID }}
          MERAKI_NETWORK_ID: ${{ secrets.MERAKI_NETWORK_ID }}
        run: |
          ansible-playbook playbooks/config_snapshot.yml \
            -i inventory/sandbox_compliance.yml \
            -e "vault_meraki_api_key=${MERAKI_DASHBOARD_API_KEY}" \
            -e "vault_meraki_org_id=${MERAKI_ORG_ID}" \
            -e "vault_meraki_network_id_1=${MERAKI_NETWORK_ID}"

      - name: Commit baseline changes to repo
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add baselines/
          if git diff --cached --quiet; then
            echo "No baseline changes to commit"
          else
            git commit -m "chore(baselines): update config snapshot [skip ci]"
            git push
          fi

      - name: Upload compliance report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: compliance-report-${{ github.run_number }}
          path: reports/
          retention-days: 90
```

### Step 3: Verify both workflow YAML files are valid

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy-ssids.yml')); yaml.safe_load(open('.github/workflows/compliance.yml')); print('Valid')"`
Expected: `Valid`

### Step 4: Commit

```bash
git add .github/workflows/deploy-ssids.yml .github/workflows/compliance.yml
git commit -m "feat(ci): add deploy-ssids and compliance GitHub Actions workflows

deploy-ssids.yml:
- Triggers on push to main (SSID config changes) or manual dispatch
- Push triggers run in check mode; manual dispatch allows live mode
- Chains to compliance workflow after live deploys

compliance.yml:
- Triggers on schedule (every 6h), manual dispatch, repository_dispatch
  (Meraki webhook), or called by deploy-ssids after deployment
- Runs compliance playbook and alerts via GitHub Issues + Webex Teams
- Uploads compliance report as artifact (90-day retention)"
```

---

## Task 7: Add Webex Webhook URL and GitHub Repo to `.env.example`

**Files:**
- Modify: `.env.example`

### Step 1: Append alerting variables to `.env.example`

Add the following at the end of `.env.example`:

```
# ============================================================
# Alerting Configuration (OPTIONAL)
# ============================================================

# Webex Teams Incoming Webhook URL
# Create one at: https://apphub.webex.com/applications/incoming-webhooks-cisco-systems-38054-702
# WEBEX_WEBHOOK_URL=https://webexapis.com/v1/webhooks/incoming/your-webhook-id

# GitHub Repository (owner/repo format, for auto-creating Issues)
# COMPLIANCE_GITHUB_REPO=your-username/meraki-wireless-ansible
```

### Step 2: Commit

```bash
git add .env.example
git commit -m "docs: add alerting env vars to .env.example"
```

---

## Task 8: Update README with 30-Minute Demo Flow

**Files:**
- Modify: `README.md`

### Step 1: Update the video timestamps section

Replace the `**Video Timestamps:**` block (lines 13-21) with:

```markdown
**Video Timestamps:**
- `00:00` - Cold open: See compliance alerting in action
- `01:00` - Introduction: Why automate wireless with Ansible?
- `03:00` - Fork, clone, and configure GitHub secrets
- `09:00` - Deploy an SSID via GitHub Actions
- `14:00` - Compliance check runs automatically — all green
- `18:00` - Simulate a rogue change — compliance fails
- `21:00` - Alerts fire: GitHub Issue + Webex Teams notification
- `24:00` - Workflow triggers: schedule, webhook, and manual dispatch
- `27:00` - Recap and next steps
```

### Step 2: Update the video description template

Replace the `📺 Video Description Template` section's `📚 Chapters:` block with:

```markdown
📚 Chapters:
00:00 Cold Open — Compliance Alert Demo
01:00 Introduction — Why Automate Wireless?
03:00 Fork, Clone & Configure GitHub Secrets
09:00 Deploy an SSID via GitHub Actions
14:00 Compliance Check Runs Automatically
18:00 Simulate a Rogue Change
21:00 Alerts: GitHub Issue + Webex Teams
24:00 Workflow Triggers: Schedule, Webhook & Manual
27:00 Recap & Next Steps
```

### Step 3: Update the "What you'll learn" section in the video description template

Replace:
```
What you'll learn:
✅ Setting up Ansible for network automation
✅ Using the Cisco Meraki API with Ansible
✅ Creating reusable playbooks and roles
✅ Managing SSIDs, access points, and compliance checks
✅ Best practices for network automation
```

With:
```
What you'll learn:
✅ Deploy wireless SSIDs via GitHub Actions + Ansible + Meraki API
✅ Run automated compliance checks — no local tools needed
✅ Auto-alert on violations via GitHub Issues + Webex Teams
✅ Trigger workflows on push, schedule, or Meraki webhook
✅ Build a closed-loop wireless compliance system in CI/CD
```

### Step 4: Commit

```bash
git add README.md
git commit -m "docs: update README with 30-minute demo flow and timestamps"
```

---

## Task 9: Add `meraki_networks` Inventory Group for Compliance

The compliance playbook targets `meraki_networks` but the sandbox inventory only has `meraki_orgs`. We need a compliance-ready inventory.

**Files:**
- Create: `inventory/sandbox_compliance.yml`

### Step 1: Create the compliance inventory file

Create `inventory/sandbox_compliance.yml`:

```yaml
---
# Compliance Check Inventory
# Maps individual Meraki networks as Ansible hosts for per-network compliance checks
#
# Usage:
#   ansible-playbook playbooks/compliance_check.yml -i inventory/sandbox_compliance.yml

all:
  children:
    meraki_networks:
      hosts:
        # Replace with your actual network name from Meraki Dashboard
        # Query via: GET /organizations/{orgId}/networks
        sandbox_network:
          meraki_network_id: "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID', true)) }}"
          meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('YOUR_ORG_ID', true)) }}"
          meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
          meraki_base_url: "https://api.meraki.com/api/v1"
          environment: sandbox
          ansible_connection: local
          ansible_python_interpreter: auto_silent

    meraki_orgs:
      hosts:
        meraki_sandbox:
          meraki_org_id: "{{ vault_meraki_org_id | default(lookup('env', 'MERAKI_ORG_ID') | default('YOUR_ORG_ID', true)) }}"
          meraki_api_key: "{{ lookup('env', 'MERAKI_DASHBOARD_API_KEY') | default(vault_meraki_api_key | default(''), true) }}"
          meraki_base_url: "https://api.meraki.com/api/v1"
          environment: sandbox
          meraki_network_ids:
            - "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID', true)) }}"
```

### Step 2: Add desired SSID config for compliance checking

Create `group_vars/meraki_networks.yml`:

```yaml
---
# Desired SSID state for compliance checking
# This is the "source of truth" — any deviation is flagged as drift

meraki_desired_ssids:
  - network_name: "sandbox_network"
    network_id: "{{ vault_meraki_network_id_1 | default(lookup('env', 'MERAKI_NETWORK_ID') | default('YOUR_NETWORK_ID', true)) }}"
    ssids:
      - name: "Sandbox-Test"
        enabled: true
        authMode: "psk"
        encryptionMode: "wpa2"
        visible: true
        broadcast: true
        minBitrate: 11
        bandSelection: "Dual band operation"
```

### Step 3: Commit

```bash
git add inventory/sandbox_compliance.yml group_vars/meraki_networks.yml .github/workflows/compliance.yml
git commit -m "feat(inventory): add compliance inventory with meraki_networks group

Creates sandbox_compliance.yml with both meraki_networks and meraki_orgs
groups. Adds meraki_networks group_vars with desired SSID state as the
compliance source of truth."
```

---

## Task 10: Update Makefile with New Targets

**Files:**
- Modify: `Makefile`

### Step 1: Add new make targets

Append the following targets to the Makefile (after existing targets):

```makefile

## Run SSID deployment playbook (syntax check only)
deploy-ssid-check:
	ansible-playbook --syntax-check playbooks/ssid_management.yml

## Run compliance check (syntax check only)
compliance-check:
	ansible-playbook --syntax-check playbooks/compliance_check.yml

## Syntax check all playbooks including new ones
test-all:
	@echo "Checking all playbooks..."
	@for playbook in playbooks/*.yml; do \
		echo "Checking: $$playbook"; \
		ansible-playbook --syntax-check "$$playbook" || exit 1; \
	done
	@echo "All playbooks passed syntax check"
```

### Step 2: Commit

```bash
git add Makefile
git commit -m "feat(makefile): add deploy-ssid-check, compliance-check, and test-all targets"
```

---

## Task 11: Final Validation — Syntax Check Everything

### Step 1: Run full syntax check

Run: `make test-all`
Expected: All playbooks pass syntax check

### Step 2: Run lint

Run: `make lint`
Expected: No critical linting errors (warnings are OK)

### Step 3: Commit any fixes if needed

```bash
git add -A
git commit -m "fix: resolve lint and syntax issues from final validation"
```

---

## Summary of All New/Modified Files

| Action | File | Purpose |
|--------|------|---------|
| Modify | `roles/meraki_ssid/defaults/main.yml` | Full variable structure |
| Modify | `roles/meraki_ssid/tasks/main.yml` | Working SSID management |
| Modify | `roles/meraki_ssid/handlers/main.yml` | Logging handler |
| Modify | `playbooks/ssid_management.yml` | Pre-task validation, proper vars |
| Modify | `playbooks/compliance_check.yml` | GitHub Issue + Webex alerting |
| Modify | `roles/meraki_compliance/defaults/main.yml` | Alerting + security baseline defaults |
| Create | `roles/meraki_compliance/tasks/security_baseline.yml` | Security policy checks (no open auth, WPA2 min, etc.) |
| Create | `roles/meraki_snapshot/defaults/main.yml` | Snapshot config variables |
| Create | `roles/meraki_snapshot/tasks/main.yml` | Pull live config, compare to baseline, save |
| Create | `playbooks/config_snapshot.yml` | GitOps config snapshot playbook |
| Create | `baselines/.gitkeep` | Directory for stored Meraki config baselines |
| Create | `.github/workflows/deploy-ssids.yml` | SSID deploy workflow (push + manual) |
| Create | `.github/workflows/compliance.yml` | Compliance + snapshot + auto-commit workflow |
| Create | `inventory/sandbox_compliance.yml` | Network-level inventory |
| Create | `group_vars/meraki_networks.yml` | Desired SSID state for compliance |
| Modify | `.env.example` | Alerting env vars |
| Modify | `README.md` | 30-minute demo timestamps |
| Modify | `Makefile` | New make targets |
