#!/usr/bin/env python3
"""
Interactive menu helper for SSID removal.
Queries Meraki API to show available networks and SSIDs.
"""

import sys
import os
import json
from pathlib import Path

try:
    import yaml
    import requests
except ImportError:
    print("ERROR: Required Python packages not found.")
    print("Run: pip install pyyaml requests")
    sys.exit(1)


def load_env_file(env_path=".env"):
    """Load environment variables from .env file."""
    env_vars = {}
    if Path(env_path).exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def get_meraki_config():
    """Get Meraki API configuration from environment."""
    env_vars = load_env_file()
    
    api_key = env_vars.get('MERAKI_DASHBOARD_API_KEY') or os.environ.get('MERAKI_DASHBOARD_API_KEY')
    org_name = env_vars.get('MERAKI_ORG_NAME') or os.environ.get('MERAKI_ORG_NAME')
    base_url = env_vars.get('MERAKI_BASE_URL', 'https://api.meraki.com/api/v1')
    
    if not api_key:
        print("ERROR: MERAKI_DASHBOARD_API_KEY not found in .env or environment")
        sys.exit(1)
    
    if not org_name:
        print("ERROR: MERAKI_ORG_NAME not found in .env or environment")
        sys.exit(1)
    
    return {
        'api_key': api_key,
        'org_name': org_name,
        'base_url': base_url
    }


def meraki_request(config, endpoint):
    """Make a request to Meraki API."""
    headers = {
        'X-Cisco-Meraki-API-Key': config['api_key'],
        'Content-Type': 'application/json'
    }
    
    url = f"{config['base_url']}{endpoint}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API request failed: {e}")
        sys.exit(1)


def get_organization_id(config):
    """Get organization ID by name."""
    orgs = meraki_request(config, '/organizations')
    
    for org in orgs:
        if org['name'] == config['org_name']:
            return org['id']
    
    print(f"ERROR: Organization '{config['org_name']}' not found")
    sys.exit(1)


def get_networks(config, org_id):
    """Get all networks for the organization."""
    networks = meraki_request(config, f'/organizations/{org_id}/networks')
    
    # Filter to only wireless networks
    wireless_networks = []
    for net in networks:
        if 'wireless' in net.get('productTypes', []):
            wireless_networks.append({
                'id': net['id'],
                'name': net['name']
            })
    
    return sorted(wireless_networks, key=lambda x: x['name'])


def get_ssids(config, network_id):
    """Get all configured SSIDs for a network."""
    ssids = meraki_request(config, f'/networks/{network_id}/wireless/ssids')
    
    # Filter to only configured SSIDs (not "Unconfigured SSID N")
    configured_ssids = []
    for ssid in ssids:
        if not ssid['name'].startswith('Unconfigured SSID'):
            configured_ssids.append({
                'number': ssid['number'],
                'name': ssid['name'],
                'enabled': ssid.get('enabled', False)
            })
    
    return sorted(configured_ssids, key=lambda x: x['number'])


def get_config_file_ssids():
    """Get SSIDs from configuration files."""
    ssids = set()
    
    # From meraki_orgs.yml
    orgs_path = Path('group_vars/meraki_orgs.yml')
    if orgs_path.exists():
        with open(orgs_path, 'r') as f:
            data = yaml.safe_load(f)
            if data and 'meraki_ssids' in data:
                for ssid in data['meraki_ssids']:
                    ssids.add(ssid['name'])
    
    # From meraki_networks.yml
    networks_path = Path('group_vars/meraki_networks.yml')
    if networks_path.exists():
        with open(networks_path, 'r') as f:
            data = yaml.safe_load(f)
            if data and 'meraki_desired_ssids' in data:
                for net in data['meraki_desired_ssids']:
                    for ssid in net.get('ssids', []):
                        ssids.add(ssid['name'])
    
    return sorted(list(ssids))


def show_network_menu(networks):
    """Display network selection menu."""
    print("\n" + "="*65)
    print("  Available Networks")
    print("="*65)
    print("")
    
    for idx, net in enumerate(networks, 1):
        print(f"  [{idx:2}] {net['name']}")
    
    print(f"  [ 0] All networks")
    print("")
    print("="*65)
    
    while True:
        try:
            choice = input("\nSelect network number (0 for all): ").strip()
            
            if not choice:
                continue
            
            choice_num = int(choice)
            
            if choice_num == 0:
                return None  # All networks
            
            if 1 <= choice_num <= len(networks):
                return networks[choice_num - 1]
            
            print(f"ERROR: Please enter a number between 0 and {len(networks)}")
        except ValueError:
            print("ERROR: Please enter a valid number")
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)


def show_ssid_menu(network_ssids, config_ssids):
    """Display SSID selection menu."""
    print("\n" + "="*65)
    print("  Available SSIDs")
    print("="*65)
    print("")
    
    # Show SSIDs from selected network
    if network_ssids:
        print("  From Selected Network:")
        for idx, ssid in enumerate(network_ssids, 1):
            status = "✓ enabled" if ssid['enabled'] else "✗ disabled"
            print(f"  [{idx:2}] {ssid['name']:<30} ({status})")
        print("")
    
    # Show SSIDs from config files
    if config_ssids:
        config_only = [s for s in config_ssids if s not in [ns['name'] for ns in network_ssids]]
        if config_only:
            print("  From Config Files Only:")
            start_idx = len(network_ssids) + 1
            for idx, ssid in enumerate(config_only, start_idx):
                print(f"  [{idx:2}] {ssid:<30} (config only)")
            print("")
    
    print("  [ 0] Enter SSID name manually")
    print("")
    print("="*65)
    
    all_ssids = network_ssids + [{'name': s} for s in config_ssids if s not in [ns['name'] for ns in network_ssids]]
    
    while True:
        try:
            choice = input("\nSelect SSID number (0 for manual entry): ").strip()
            
            if not choice:
                continue
            
            choice_num = int(choice)
            
            if choice_num == 0:
                ssid_name = input("Enter SSID name: ").strip()
                if ssid_name:
                    return ssid_name
                print("ERROR: SSID name cannot be empty")
                continue
            
            if 1 <= choice_num <= len(all_ssids):
                return all_ssids[choice_num - 1]['name']
            
            print(f"ERROR: Please enter a number between 0 and {len(all_ssids)}")
        except ValueError:
            print("ERROR: Please enter a valid number")
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)


def main():
    """Main interactive menu."""
    print("\n" + "="*65)
    print("  SSID Removal Tool - Interactive Menu")
    print("="*65)
    print("")
    print("  This tool will help you remove an SSID from Meraki networks")
    print("  and clean up all configuration files.")
    print("")
    
    # Get Meraki configuration
    config = get_meraki_config()
    org_id = get_organization_id(config)
    
    # Get networks
    print("  Fetching networks...")
    networks = get_networks(config, org_id)
    
    if not networks:
        print("ERROR: No wireless networks found")
        sys.exit(1)
    
    # Select network
    selected_network = show_network_menu(networks)
    
    # Get SSIDs
    network_ssids = []
    if selected_network:
        print(f"\n  Fetching SSIDs from {selected_network['name']}...")
        network_ssids = get_ssids(config, selected_network['id'])
    
    # Get SSIDs from config files
    config_ssids = get_config_file_ssids()
    
    # Select SSID
    selected_ssid = show_ssid_menu(network_ssids, config_ssids)
    
    # Output result as JSON for make target to consume
    result = {
        'ssid_name': selected_ssid,
        'network_name': selected_network['name'] if selected_network else None,
        'network_id': selected_network['id'] if selected_network else None
    }
    
    print("")
    print("="*65)
    print("  Selection Complete")
    print("="*65)
    print(f"  SSID: {result['ssid_name']}")
    print(f"  Network: {result['network_name'] if result['network_name'] else 'All networks'}")
    print("="*65)
    print("")
    
    # Output for make target consumption
    print("__RESULT_JSON__")
    print(json.dumps(result))


if __name__ == '__main__':
    main()
