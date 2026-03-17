# Meraki Wireless Ansible

This repository manages Cisco Meraki wireless configuration with Ansible and GitHub Actions.
It covers SSID deployment, SSID removal, compliance auditing, baseline snapshots, and network-scoped group policy seeding.

## What Is In Scope

- Deploy SSIDs from Git-managed desired state in `group_vars/meraki_orgs.yml`
- Remove an SSID by resetting its Meraki slot to an unconfigured placeholder
- Build compliance desired state in `group_vars/meraki_networks.yml`
- Audit live SSID drift, security baselines, and group policy ACLs
- Snapshot live SSID config into `baselines/`
- Trigger runs locally, from the GitHub UI, or through `repository_dispatch`

## Repository Layout

```text
.github/workflows/   GitHub Actions for validation, deploys, dispatch, and compliance
playbooks/           Ansible entrypoints
roles/               Reusable Ansible logic
inventory/           Production inventory and development example
group_vars/          Desired SSID, network, and group-policy state
vault/               Vault example/template files
baselines/           Saved live snapshots for drift history
docs/                Getting started, architecture, compliance, workflow docs
scripts/             Local setup, smoke tests, YAML update helpers, template validation
Dashboard Workflow/  Meraki Dashboard workflow export
slides/              Presentation assets
```

`Dashboard Workflow/workflow.json` is intentionally kept in the repo so the Meraki Dashboard workflow can be recreated or re-imported.

## Prerequisites

- Python 3.12+
- Ansible Core 2.20.x
- Access to a Meraki org with API enabled
- A Meraki API key with access to the target org and networks

Python and collection versions are pinned in [requirements.txt](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/requirements.txt) and [requirements.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/requirements.yml).

## Setup

```bash
make setup
source venv/bin/activate
cp .env.example .env
cp vault/secrets.yml.example vault/secrets.yml
```

Then fill in `.env` with at least:

```bash
MERAKI_DASHBOARD_API_KEY=...
MERAKI_ORG_NAME=...
MERAKI_NETWORK_NAMES=Site-A,Site-B
```

You can use `MERAKI_NETWORK_NAME` for a single network instead of `MERAKI_NETWORK_NAMES`.

If you want encrypted repo-managed secrets, create `vault/secrets.yml` from the example and run:

```bash
make vault-encrypt
```

## Variable Model

- [inventory/production.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/inventory/production.yml) resolves org and network names at runtime from env vars or vault vars.
- [group_vars/meraki_orgs.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/group_vars/meraki_orgs.yml) is the SSID deployment source of truth.
- [group_vars/meraki_networks.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/group_vars/meraki_networks.yml) is the compliance desired state.
- [group_vars/meraki_group_policies.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/group_vars/meraki_group_policies.yml) is the desired group-policy seed state.
- [vault/secrets.yml.example](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/vault/secrets.yml.example) shows the supported vault-backed secret names.

Common secret env vars used by the repo include:

- `MERAKI_DASHBOARD_API_KEY`
- `CORP_SECURE_PSK`, `GUEST_SSID_PSK`, `CORPORATE_BYOD_PSK`, `IOT_SSID_PSK`
- `RADIUS_SERVER_1_HOST`, `RADIUS_SERVER_1_SECRET`
- `RADIUS_ACCOUNTING_SERVER_HOST`, `RADIUS_ACCOUNTING_SERVER_SECRET`
- `WEBEX_BOT_TOKEN`, `WEBEX_ALERT_EMAIL`, `WEBEX_WEBHOOK_URL`, `WEBEX_WEBHOOK_SECRET`

## Playbooks

- `playbooks/discover.yml`
  Internal discovery playbook that resolves the target org and dynamically builds the `meraki_networks` host group.

- `playbooks/ssid_management.yml`
  Deploys SSIDs from `group_vars/meraki_orgs.yml` to the resolved target networks.

- `playbooks/remove_ssid.yml`
  Resets a named SSID slot to an `Unconfigured SSID <n>` placeholder.
  Requires `-e "meraki_remove_ssid_name=<SSID>"`.

- `playbooks/group_policy_management.yml`
  Seeds or updates network-scoped Meraki group policies from `group_vars/meraki_group_policies.yml`.

- `playbooks/compliance_check.yml`
  Audits desired-vs-live SSID drift, security baselines, and group policy ACL findings.
  Writes Markdown reports to `reports/`.

- `playbooks/config_snapshot.yml`
  Pulls live SSID config and writes sanitized baselines into `baselines/`.

- `playbooks/configure_network.yml`
  Updates `group_vars/meraki_networks.yml` for one or more target networks using SSIDs already defined in `group_vars/meraki_orgs.yml`.
  Requires `-e "target_networks=Site-A,Site-B"` and optionally accepts `-e "scope_ssid=Corp-Secure"`.

## Local Usage

Validate before you change anything:

```bash
make lint
make test
make test-templates
make smoke-test
```

Common playbook runs:

```bash
# Dry-run SSID deployment
ansible-playbook -i inventory/production.yml playbooks/ssid_management.yml --check --diff

# Live SSID deployment
ansible-playbook -i inventory/production.yml playbooks/ssid_management.yml

# Remove one SSID by name
ansible-playbook -i inventory/production.yml playbooks/remove_ssid.yml \
  -e "meraki_remove_ssid_name=Corp-Guest"

# Seed group policies
ansible-playbook -i inventory/production.yml playbooks/group_policy_management.yml

# Run compliance audit
ansible-playbook -i inventory/production.yml playbooks/compliance_check.yml

# Snapshot live config
ansible-playbook -i inventory/production.yml playbooks/config_snapshot.yml

# Update compliance desired state for selected networks
ansible-playbook -i inventory/production.yml playbooks/configure_network.yml \
  -e "target_networks=Site-A,Site-B"

# Update compliance desired state for one SSID only
ansible-playbook -i inventory/production.yml playbooks/configure_network.yml \
  -e "target_networks=Site-A,Site-B" \
  -e "scope_ssid=Corp-Secure"
```

## GitHub Actions

The repo currently ships four workflows:

- [validate.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/.github/workflows/validate.yml)
  Lint, syntax check, template validation, dry-run validation, and secret scanning.
  Triggers on `workflow_dispatch`, `push`, `pull_request`, and `repository_dispatch` (`validate-ansible`).

- [deploy-ssids.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/.github/workflows/deploy-ssids.yml)
  Can add or update an SSID definition in `group_vars/meraki_orgs.yml`, optionally update `group_vars/meraki_networks.yml`, deploy to Meraki, and then run post-deploy compliance plus a baseline snapshot.
  Triggers on `workflow_dispatch` and `repository_dispatch` (`deploy-ssids`).

- [playbook-dispatch.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/.github/workflows/playbook-dispatch.yml)
  Runs one selected playbook from GitHub.
  Triggers on `workflow_dispatch` and `repository_dispatch` with:
  `run-playbook`, `run-ssid-management`, `run-remove-ssid`, `run-group-policy-management`, `run-compliance-check`, `run-config-snapshot`, and `run-configure-network`.

- [compliance.yml](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/.github/workflows/compliance.yml)
  Runs scheduled or on-demand compliance checks, snapshots baselines, and can open GitHub issues for violations.
  Triggers on `workflow_dispatch`, `workflow_call`, `schedule`, and `repository_dispatch` (`meraki-config-change`).

Important workflow behavior:

- `deploy-ssids.yml` only runs post-deploy compliance when `dry_run=false`.
- `playbook-dispatch.yml` requires `target_networks` for `configure_network.yml`, `remove_ssid.yml`, and `group_policy_management.yml`.
- `playbook-dispatch.yml` also requires `ssid_name` for `remove_ssid.yml`.
- `compliance.yml` debounces `repository_dispatch` bursts using the repo variable `COMPLIANCE_WEBHOOK_DEBOUNCE_SECONDS` and defaults to 120 seconds.
- Baseline and generated state files can be committed back to the repo from GitHub Actions.

## Repository Dispatch Events

Supported dispatch entrypoints in the current repo are:

- `deploy-ssids`
- `run-playbook`
- `run-ssid-management`
- `run-remove-ssid`
- `run-group-policy-management`
- `run-compliance-check`
- `run-config-snapshot`
- `run-configure-network`
- `validate-ansible`
- `meraki-config-change`

Common payload fields used across workflows:

- `dry_run`
- `target_networks`
- `scope_ssid`
- `ssid_name`
- `commit_changes`
- `meraki_org_name`
- `meraki_network_names`

## Meraki Dashboard Workflow And AI Assistant

This repo does talk about the Meraki Dashboard workflow path, but it was only linked before. The intended trigger chain is:

```text
Meraki Dashboard AI Assistant -> Meraki Dashboard Workflow -> GitHub POST /dispatches -> GitHub Actions workflow -> Ansible playbook
```

What is in the repo today:

- [Dashboard Workflow/workflow.json](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/Dashboard%20Workflow/workflow.json)
  Exported Meraki Dashboard workflow named `Wireless Ansible Trigger`.
  Keep this file in the repo so the workflow can be recreated or re-imported in Meraki Dashboard Workflows.

- [docs/MERAKI_AI_ASSISTANT_WORKFLOW_PROMPT.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/MERAKI_AI_ASSISTANT_WORKFLOW_PROMPT.md)
  Prompt pack for building AI Assistant workflows that call this repo.

- [docs/MERAKI_AI_ASSISTANT_DEPLOY_SSIDS_PROMPT.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/MERAKI_AI_ASSISTANT_DEPLOY_SSIDS_PROMPT.md)
  Focused deploy prompt for a single SSID create/update path.

The current exported Dashboard workflow is deploy-focused:

- It sends a GitHub `POST` to `https://api.github.com/repos/liptonj/meraki-wireless-ansible/dispatches`
- It uses `event_type: deploy-ssids`
- It passes deploy inputs such as `target_networks`, `ssid_name`, `auth_mode`, `encryption_mode`, `band_selection`, `ssid_enabled`, `ssid_visible`, `dry_run`, and optional `psk_secret`

For AI Assistant usage:

- Use a Meraki Dashboard workflow or AI Assistant prompt that resolves the org and network, then sends the GitHub dispatch request
- Keep the GitHub token in workflow secrets, not in `client_payload`
- Treat HTTP `204 No Content` from GitHub as a successful dispatch
- Default change actions to `dry_run=true` unless a human explicitly wants a live run

Minimal deploy example:

```json
{
  "event_type": "deploy-ssids",
  "client_payload": {
    "target_networks": "LAB-Site1",
    "ssid_name": "Corp-Secure",
    "auth_mode": "psk",
    "encryption_mode": "wpa3",
    "band_selection": "Dual band operation",
    "ssid_enabled": true,
    "ssid_visible": true,
    "dry_run": true,
    "psk_secret": "CORP_SECURE_PSK"
  }
}
```

For complete prompt packs and payload examples, use:

- [docs/MERAKI_AI_ASSISTANT_WORKFLOW_PROMPT.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/MERAKI_AI_ASSISTANT_WORKFLOW_PROMPT.md)
- [docs/MERAKI_AI_ASSISTANT_DEPLOY_SSIDS_PROMPT.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/MERAKI_AI_ASSISTANT_DEPLOY_SSIDS_PROMPT.md)
- [Dashboard Workflow/workflow.json](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/Dashboard%20Workflow/workflow.json)

## Documentation

- [docs/GETTING_STARTED.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/GETTING_STARTED.md)
- [docs/ARCHITECTURE.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/ARCHITECTURE.md)
- [docs/COMPLIANCE.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/COMPLIANCE.md)
- [docs/TROUBLESHOOTING.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/TROUBLESHOOTING.md)
- [docs/WORKFLOW_TEST_MATRIX.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/docs/WORKFLOW_TEST_MATRIX.md)
- [CONTRIBUTING.md](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/CONTRIBUTING.md)

## License

[MIT](/Users/jolipton/Youtube/Wireless Automation/meraki-wireless-ansible/LICENSE)
