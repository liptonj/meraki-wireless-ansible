#!/usr/bin/env python3
"""
remove_ssid_desired_state.py

Removes an SSID from the compliance desired state in
group_vars/meraki_networks.yml, across all networks.

Usage (set env vars before running):
    SSID_NAME="Corp-Guest" python scripts/remove_ssid_desired_state.py

Preserves all existing YAML formatting using ruamel.yaml round-trip mode.
"""
import logging
import os
import sys

from ruamel.yaml import YAML

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

NETWORKS_PATH = "group_vars/meraki_networks.yml"


def get_required_env(key: str) -> str:
    value = os.environ.get(key, "").strip()
    if not value:
        log.error("Required environment variable %s is not set or empty.", key)
        sys.exit(1)
    return value


def load_yaml(path: str) -> tuple[dict, YAML]:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 120
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.load(fh)
    return data, yaml


def save_yaml(path: str, data: dict, yaml: YAML) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh)
    log.info("Wrote updated config to %s", path)


def main() -> None:
    ssid_name = get_required_env("SSID_NAME")

    log.info("Removing SSID '%s' from compliance desired state in %s", ssid_name, NETWORKS_PATH)

    data, yaml = load_yaml(NETWORKS_PATH)

    desired_ssids = data.get("meraki_desired_ssids")
    if not desired_ssids:
        log.warning("No meraki_desired_ssids found in %s. Nothing to remove.", NETWORKS_PATH)
        return

    total_removed = 0

    for network_entry in desired_ssids:
        network_name = network_entry.get("network_name", "unknown")
        ssids = network_entry.get("ssids", [])
        if ssids is None:
            continue

        original_count = len(ssids)
        # Filter out the SSID to remove
        filtered = [s for s in ssids if s.get("name") != ssid_name]
        removed_count = original_count - len(filtered)

        if removed_count > 0:
            network_entry["ssids"] = filtered
            total_removed += removed_count
            log.info(
                "Removed %d instance(s) of '%s' from network '%s'.",
                removed_count, ssid_name, network_name,
            )

    # Remove any network entries that now have zero SSIDs
    data["meraki_desired_ssids"] = [
        entry for entry in desired_ssids
        if entry.get("ssids") and len(entry["ssids"]) > 0
    ]
    pruned_networks = len(desired_ssids) - len(data["meraki_desired_ssids"])

    if total_removed == 0:
        log.warning("SSID '%s' not found in any network desired state.", ssid_name)
        return

    save_yaml(NETWORKS_PATH, data, yaml)
    log.info(
        "Done — removed %d total entries for '%s' across all networks. "
        "Pruned %d empty network entries.",
        total_removed, ssid_name, pruned_networks,
    )


if __name__ == "__main__":
    main()
