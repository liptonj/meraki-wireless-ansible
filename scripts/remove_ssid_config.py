#!/usr/bin/env python3
"""
remove_ssid_config.py

Removes an SSID entry from group_vars/meraki_orgs.yml based on the
SSID_NAME environment variable set by the GitHub Actions workflow.

Usage (set env vars before running):
    SSID_NAME="Corp-Guest" python scripts/remove_ssid_config.py

The script preserves all existing YAML formatting, comments, and Ansible
Vault / Jinja2 template references using ruamel.yaml round-trip mode.
"""
import logging
import os
import sys

from ruamel.yaml import YAML

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

GROUP_VARS_PATH = "group_vars/meraki_orgs.yml"


def get_required_env(key: str) -> str:
    value = os.environ.get(key, "").strip()
    if not value:
        log.error("Required environment variable %s is not set or empty.", key)
        sys.exit(1)
    return value


def load_group_vars(path: str) -> tuple[dict, YAML]:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 120
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.load(fh)
    return data, yaml


def save_group_vars(path: str, data: dict, yaml: YAML) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh)
    log.info("Wrote updated config to %s", path)


def main() -> None:
    ssid_name = get_required_env("SSID_NAME")

    log.info("Removing SSID '%s' from %s", ssid_name, GROUP_VARS_PATH)

    data, yaml = load_group_vars(GROUP_VARS_PATH)

    if "meraki_ssids" not in data or data["meraki_ssids"] is None:
        log.warning("No meraki_ssids found in %s. Nothing to remove.", GROUP_VARS_PATH)
        return

    ssids = data["meraki_ssids"]
    original_count = len(ssids)

    # Find and remove the SSID by name
    matching_indices = [
        i for i, s in enumerate(ssids) if s.get("name") == ssid_name
    ]

    if not matching_indices:
        log.warning(
            "SSID '%s' not found in %s. Available SSIDs: %s",
            ssid_name,
            GROUP_VARS_PATH,
            ", ".join(s.get("name", "?") for s in ssids),
        )
        return

    # Remove in reverse order to preserve indices
    for idx in reversed(matching_indices):
        log.info("Removing SSID '%s' at index %d.", ssid_name, idx)
        del ssids[idx]

    save_group_vars(GROUP_VARS_PATH, data, yaml)
    log.info(
        "Done — removed %d SSID entry/entries for '%s'. SSIDs: %d -> %d.",
        len(matching_indices),
        ssid_name,
        original_count,
        len(ssids),
    )


if __name__ == "__main__":
    main()
