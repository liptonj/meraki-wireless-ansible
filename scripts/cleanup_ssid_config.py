#!/usr/bin/env python3
"""
Cleanup SSID references from Ansible configuration files.
This script is called by the meraki_ssid_cleanup_config role.
"""

import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime


def load_yaml_file(file_path):
    """Load YAML file and return parsed data."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def save_yaml_file(file_path, data, header_comment=None):
    """Save data to YAML file with optional header comment."""
    with open(file_path, 'w') as f:
        if header_comment:
            f.write(header_comment)
            if not header_comment.endswith('\n'):
                f.write('\n')
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)


def cleanup_meraki_orgs_config(config_path, ssid_name):
    """Remove SSID from meraki_orgs.yml deployment configuration."""
    data = load_yaml_file(config_path)
    
    if 'meraki_ssids' not in data:
        return False, "No meraki_ssids found in configuration"
    
    original_count = len(data['meraki_ssids'])
    data['meraki_ssids'] = [
        ssid for ssid in data['meraki_ssids']
        if ssid.get('name') != ssid_name
    ]
    removed_count = original_count - len(data['meraki_ssids'])
    
    if removed_count > 0:
        header = """# SSID Deployment Config — applies to hosts in the `meraki_orgs` inventory group
# (used by ssid_management.yml). Defines what SSIDs to deploy and operational settings.

"""
        save_yaml_file(config_path, data, header)
        return True, f"Removed {removed_count} SSID entry(ies)"
    
    return False, "SSID not found in configuration"


def cleanup_meraki_networks_config(config_path, ssid_name, network_name):
    """Remove SSID from meraki_networks.yml compliance desired state."""
    data = load_yaml_file(config_path)
    
    if 'meraki_desired_ssids' not in data:
        return False, "No meraki_desired_ssids found in configuration"
    
    modified = False
    for network_entry in data['meraki_desired_ssids']:
        if network_entry.get('network_name') == network_name:
            original_count = len(network_entry.get('ssids', []))
            network_entry['ssids'] = [
                ssid for ssid in network_entry.get('ssids', [])
                if ssid.get('name') != ssid_name
            ]
            removed_count = original_count - len(network_entry['ssids'])
            if removed_count > 0:
                modified = True
    
    if modified:
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        header = f"""---
# Compliance Desired State — used by compliance_check.yml.
# Any deviation from these values is flagged as drift.
#
# network_name must match the Meraki network name exactly.
# Networks not listed here will have no desired config to compare against.
# Last updated: {timestamp} via remove_ssid.yml
"""
        save_yaml_file(config_path, data, header)
        return True, f"Removed SSID from network {network_name}"
    
    return False, f"SSID not found in network {network_name}"


def cleanup_baseline_config(baseline_path, ssid_name, network_id):
    """Remove SSID from baseline snapshot file."""
    if not Path(baseline_path).exists():
        return False, "Baseline file does not exist"
    
    data = load_yaml_file(baseline_path)
    
    if 'ssids' not in data:
        return False, "No ssids found in baseline"
    
    original_count = len(data['ssids'])
    data['ssids'] = [
        ssid for ssid in data['ssids']
        if ssid.get('name') != ssid_name
    ]
    removed_count = original_count - len(data['ssids'])
    
    if removed_count > 0:
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        header = f"""---
# Meraki SSID Configuration Baseline
# Network: {network_id}
# Captured: {timestamp}
# Updated by remove_ssid playbook — SSID '{ssid_name}' removed

"""
        save_yaml_file(baseline_path, data, header)
        return True, f"Removed {removed_count} SSID entry(ies) from baseline"
    
    return False, "SSID not found in baseline"


def main():
    parser = argparse.ArgumentParser(
        description='Cleanup SSID references from Ansible configuration files'
    )
    parser.add_argument('--ssid-name', required=True, help='Name of SSID to remove')
    parser.add_argument('--network-name', required=True, help='Network name')
    parser.add_argument('--network-id', required=True, help='Network ID')
    parser.add_argument('--orgs-config', required=True, help='Path to meraki_orgs.yml')
    parser.add_argument('--networks-config', required=True, help='Path to meraki_networks.yml')
    parser.add_argument('--baseline-path', required=True, help='Path to baseline file')
    parser.add_argument('--check-mode', action='store_true', help='Check mode (no changes)')
    
    args = parser.parse_args()
    
    results = {
        'changed': False,
        'files_updated': [],
        'messages': []
    }
    
    if args.check_mode:
        results['messages'].append(f"CHECK MODE: Would cleanup SSID '{args.ssid_name}'")
        print(yaml.dump(results))
        return 0
    
    # Cleanup meraki_orgs.yml
    try:
        changed, msg = cleanup_meraki_orgs_config(args.orgs_config, args.ssid_name)
        if changed:
            results['changed'] = True
            results['files_updated'].append(args.orgs_config)
        results['messages'].append(f"meraki_orgs.yml: {msg}")
    except Exception as e:
        results['messages'].append(f"ERROR in meraki_orgs.yml: {str(e)}")
    
    # Cleanup meraki_networks.yml
    try:
        changed, msg = cleanup_meraki_networks_config(
            args.networks_config, args.ssid_name, args.network_name
        )
        if changed:
            results['changed'] = True
            results['files_updated'].append(args.networks_config)
        results['messages'].append(f"meraki_networks.yml: {msg}")
    except Exception as e:
        results['messages'].append(f"ERROR in meraki_networks.yml: {str(e)}")
    
    # Cleanup baseline
    try:
        changed, msg = cleanup_baseline_config(
            args.baseline_path, args.ssid_name, args.network_id
        )
        if changed:
            results['changed'] = True
            results['files_updated'].append(args.baseline_path)
        results['messages'].append(f"baseline: {msg}")
    except Exception as e:
        results['messages'].append(f"ERROR in baseline: {str(e)}")
    
    # Output results as YAML for Ansible to parse
    print(yaml.dump(results))
    return 0 if results['changed'] or args.check_mode else 1


if __name__ == '__main__':
    sys.exit(main())
