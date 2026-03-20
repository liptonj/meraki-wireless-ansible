# Meraki SSID Cleanup Config Role

## Purpose

This role cleans up SSID references from Ansible configuration files after an SSID has been removed from Meraki networks using the `meraki_ssid_remove` role.

## What It Does

The role removes SSID entries from the following files:

1. **`group_vars/meraki_orgs.yml`** - Deployment configuration (`meraki_ssids` list)
2. **`group_vars/meraki_networks.yml`** - Compliance desired state (`meraki_desired_ssids`)
3. **`baselines/<network_id>/ssids.yml`** - Snapshot baseline files

## Requirements

- Python 3 with PyYAML library
- The `cleanup_ssid_config.py` script in `scripts/` directory
- Required Ansible facts:
  - `meraki_remove_ssid_name` - Name of SSID to remove
  - `meraki_network_name_resolved` - Human-readable network name
  - `meraki_network_id` - Meraki network ID

## Usage

This role is automatically invoked by the `remove_ssid.yml` playbook after removing an SSID from Meraki:

```bash
ansible-playbook playbooks/remove_ssid.yml -i inventory/production.yml \
  -e "meraki_remove_ssid_name=Corp-Guest"
```

### Check Mode

The role supports Ansible check mode to preview what would be cleaned up:

```bash
ansible-playbook playbooks/remove_ssid.yml -i inventory/production.yml \
  -e "meraki_remove_ssid_name=Corp-Guest" --check
```

## Role Variables

### Required Variables

- `meraki_remove_ssid_name` - Name of the SSID to remove from configuration files
- `meraki_network_name_resolved` - Network name for compliance config filtering
- `meraki_network_id` - Network ID for baseline file path

### Optional Variables (from defaults)

- `meraki_ssid_cleanup_backup` - Whether to create backups before modifying files (default: `true`)
- `meraki_ssid_cleanup_validate_yaml` - Whether to validate YAML syntax (default: `true`)

## File Modifications

### meraki_orgs.yml

The role removes matching SSID entries from the `meraki_ssids` list. This prevents the SSID from being redeployed by `ssid_management.yml`.

**Before:**
```yaml
meraki_ssids:
  - name: "Corp-Secure"
    enabled: true
    authMode: "psk"
    # ...
  - name: "Corp-Guest"
    enabled: true
    authMode: "open"
    # ...
```

**After (removing Corp-Guest):**
```yaml
meraki_ssids:
  - name: "Corp-Secure"
    enabled: true
    authMode: "psk"
    # ...
```

### meraki_networks.yml

The role removes matching SSID entries from the `ssids` list for the specific network in `meraki_desired_ssids`. This prevents compliance drift alerts for the removed SSID.

**Before:**
```yaml
meraki_desired_ssids:
  - network_name: Site-A
    ssids:
      - name: Corp-Secure
        authMode: psk
        # ...
      - name: Corp-Guest
        authMode: open
        # ...
```

**After (removing Corp-Guest from Site-A):**
```yaml
meraki_desired_ssids:
  - network_name: Site-A
    ssids:
      - name: Corp-Secure
        authMode: psk
        # ...
```

### Baseline Files

The role removes matching SSID entries from the `ssids` list in baseline snapshot files located at `baselines/<network_id>/ssids.yml`.

## Dependencies

- `meraki_ssid_remove` role (must run first to actually remove the SSID from Meraki)

## Tags

- `ssid` - All SSID-related tasks
- `cleanup` - Configuration cleanup tasks
- `validate` - Validation tasks

## Example Playbook

```yaml
---
- name: Remove SSID and Cleanup Configuration
  hosts: meraki_networks
  gather_facts: true
  
  roles:
    - role: meraki_ssid_remove
    - role: meraki_ssid_cleanup_config
```

## Error Handling

The role will:
- Fail if required variables are missing
- Continue if baseline file doesn't exist (not an error)
- Report all cleanup actions in the task output
- Fail if the cleanup script encounters errors (except in check mode)

## Notes

- The role runs `run_once: true` and is delegated to localhost to avoid duplicate file modifications
- The Python script preserves the structure and formatting of configuration files
- Files are updated with appropriate header comments including timestamps
- The role is idempotent - running it multiple times has the same effect as running it once
