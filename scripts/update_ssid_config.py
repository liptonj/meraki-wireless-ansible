#!/usr/bin/env python3
"""
update_ssid_config.py

Adds or updates an SSID entry in group_vars/meraki_orgs.yml based on
environment variables set by the GitHub Actions workflow_dispatch inputs.

Usage (set env vars before running):
    SSID_NAME="Corp-Secure" AUTH_MODE="psk" PSK_SECRET="CORP_SECURE_PSK" \\
        python scripts/update_ssid_config.py

The script preserves all existing YAML formatting, comments, and Ansible
Vault / Jinja2 template references using ruamel.yaml round-trip mode.
"""
import logging
import os
import sys

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

GROUP_VARS_PATH = "group_vars/meraki_orgs.yml"

# Maps the workflow input choice to the Jinja2 Ansible reference stored in YAML.
# The actual secret value never touches group_vars — only the lookup expression.
PSK_VAULT_MAP: dict[str, str] = {
    "CORP_SECURE_PSK": (
        "{{ lookup('env', 'CORP_SECURE_PSK') | default(vault_corp_secure_psk | default(''), true) }}"
    ),
    "GUEST_SSID_PSK": (
        "{{ lookup('env', 'GUEST_SSID_PSK') | default(vault_guest_ssid_psk | default(''), true) }}"
    ),
    "CORPORATE_BYOD_PSK": (
        "{{ lookup('env', 'CORPORATE_BYOD_PSK') | default(vault_corporate_byod_psk | default(''), true) }}"
    ),
    "IOT_SSID_PSK": (
        "{{ lookup('env', 'IOT_SSID_PSK') | default(vault_iot_ssid_psk | default(''), true) }}"
    ),
}

# RADIUS vault reference templates (populated from GitHub secrets in CI)
_RADIUS = {
    "host": (
        "{{ lookup('env', 'RADIUS_SERVER_1_HOST') "
        "| default(vault_radius_server_1_host | default(''), true) }}"
    ),
    "secret": (
        "{{ lookup('env', 'RADIUS_SERVER_1_SECRET') "
        "| default(vault_radius_server_1_secret | default(''), true) }}"
    ),
    "acct_host": (
        "{{ lookup('env', 'RADIUS_ACCOUNTING_SERVER_HOST') "
        "| default(vault_radius_accounting_server_host | default(''), true) }}"
    ),
    "acct_secret": (
        "{{ lookup('env', 'RADIUS_ACCOUNTING_SERVER_SECRET') "
        "| default(vault_radius_accounting_server_secret | default(''), true) }}"
    ),
}


def _dqs(value: str) -> DoubleQuotedScalarString:
    """Wrap a string so ruamel.yaml writes it with double quotes."""
    return DoubleQuotedScalarString(value)


def get_required_env(key: str) -> str:
    value = os.environ.get(key, "").strip()
    if not value:
        log.error("Required environment variable %s is not set or empty.", key)
        sys.exit(1)
    return value


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def build_ssid_entry(
    name: str,
    auth_mode: str,
    encryption_mode: str,
    psk_secret: str,
    band_selection: str,
    enabled: bool,
    visible: bool,
    min_bitrate: int | float = 11,
) -> dict:
    """Return a dict representing one SSID in meraki_orgs.yml."""
    effective_encryption = "open" if auth_mode == "open" else "wpa"
    effective_wpa_encryption_mode = (
        "WPA3 Transition Mode" if encryption_mode == "wpa3" else "WPA2 only"
    )
    entry: dict = {
        "name":                       _dqs(name),
        "enabled":                    enabled,
        "authMode":                   _dqs(auth_mode),
        "encryptionMode":             _dqs(effective_encryption),
        "minBitrate":                 min_bitrate,
        "bandSelection":              _dqs(band_selection),
        "perClientBandwidthLimitUp":  0,
        "perClientBandwidthLimitDown": 0,
        "visible":                    visible,
        "availableOnAllAps":          True,
    }

    if auth_mode == "psk":
        if psk_secret not in PSK_VAULT_MAP:
            log.error(
                "psk_secret '%s' is not recognised. Valid options: %s",
                psk_secret,
                ", ".join(PSK_VAULT_MAP.keys()),
            )
            sys.exit(1)
        entry["psk"] = _dqs(PSK_VAULT_MAP[psk_secret])

    elif auth_mode == "8021x-radius":
        entry["radiusServers"] = [
            {
                "host":   _dqs(_RADIUS["host"]),
                "secret": _dqs(_RADIUS["secret"]),
            }
        ]
        entry["radiusAccountingEnabled"] = True
        entry["radiusAccountingServers"] = [
            {
                "host":   _dqs(_RADIUS["acct_host"]),
                "secret": _dqs(_RADIUS["acct_secret"]),
            }
        ]

    # open auth — no extra keys needed
    if auth_mode != "open":
        entry["wpaEncryptionMode"] = _dqs(effective_wpa_encryption_mode)

    if auth_mode == "open":
        entry.pop("perClientBandwidthLimitUp", None)
        entry.pop("perClientBandwidthLimitDown", None)

    return entry


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
    ssid_name       = get_required_env("SSID_NAME")
    auth_mode       = get_env("AUTH_MODE",       "psk")
    encryption_mode = get_env("ENCRYPTION_MODE", "wpa3")
    psk_secret      = get_env("PSK_SECRET",      "none")
    band_selection  = get_env("BAND_SELECTION",  "Dual band operation")
    enabled         = get_env("SSID_ENABLED",    "true").lower() == "true"
    visible         = get_env("SSID_VISIBLE",    "true").lower() == "true"
    min_bitrate     = 11  # fixed default; not exposed as a workflow input

    # Guard: PSK mode requires a secret selection
    if auth_mode == "psk" and psk_secret == "none":
        log.error("auth_mode is 'psk' but PSK_SECRET is 'none'. Select a saved PSK.")
        sys.exit(1)

    log.info(
        "Building SSID entry — name='%s' auth=%s enc=%s psk=%s band='%s' enabled=%s visible=%s bitrate=%s",
        ssid_name, auth_mode, encryption_mode, psk_secret,
        band_selection, enabled, visible, min_bitrate,
    )

    new_ssid = build_ssid_entry(
        name=ssid_name,
        auth_mode=auth_mode,
        encryption_mode=encryption_mode,
        psk_secret=psk_secret,
        band_selection=band_selection,
        enabled=enabled,
        visible=visible,
        min_bitrate=min_bitrate,
    )

    data, yaml = load_group_vars(GROUP_VARS_PATH)

    if "meraki_ssids" not in data or data["meraki_ssids"] is None:
        data["meraki_ssids"] = []

    ssids = data["meraki_ssids"]
    existing_idx = next(
        (i for i, s in enumerate(ssids) if s.get("name") == ssid_name), None
    )

    if existing_idx is not None:
        log.info("Updating existing SSID '%s' at index %d.", ssid_name, existing_idx)
        ssids[existing_idx] = new_ssid
    else:
        log.info("Appending new SSID '%s'.", ssid_name)
        ssids.append(new_ssid)

    save_group_vars(GROUP_VARS_PATH, data, yaml)
    log.info("Done — SSID '%s' written to %s.", ssid_name, GROUP_VARS_PATH)


if __name__ == "__main__":
    main()
