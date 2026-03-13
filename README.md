# Meraki Wireless Ansible: Best Practices Guide

This repository manages Cisco Meraki wireless configuration with Ansible.
This README is intentionally focused on operational best practices only.

## Scope

- Deploy and update SSID configuration safely.
- Check compliance and detect drift.
- Snapshot live configuration for audit history.

## Core Principles

- Use explicit inventory on every run (`-i inventory/production.yml`).
- Run visibility checks before applying changes.
- Use check mode and diffs before live execution.
- Keep secrets out of Git (env vars or Ansible Vault only).
- Keep changes idempotent and serial to limit blast radius.
- Validate with lint and syntax checks before merge/deploy.

## Repository Layout

```text
playbooks/      # Execution entrypoints
roles/          # Reusable logic
inventory/      # Environment inventory files
group_vars/     # Desired state and shared vars
vault/          # Vault examples/templates only
baselines/      # Captured snapshots for drift/audit
```

## Prerequisites

- Python 3.12+
- Ansible Core 2.20+
- Meraki API key with required org/network access

## Setup (Safe Defaults)

```bash
make setup
source venv/bin/activate
cp .env.example .env
```

Populate `.env` with required values:

```bash
MERAKI_DASHBOARD_API_KEY=...
MERAKI_ORG_NAME=...
MERAKI_NETWORK_NAMES=Site-A,Site-B
```

## Secrets Best Practices

- Do not commit plaintext credentials, keys, or tokens.
- Use `vault/secrets.yml` (encrypted) for persistent secrets.
- Keep vault password material outside Git.
- Prefer environment-variable injection in CI/CD.

Vault workflow:

```bash
cp vault/secrets.yml.example vault/secrets.yml
make vault-encrypt
```

## Meraki Dashboard AI Webhook Flow

End-to-end trigger path:

```text
Meraki Dashboard AI Agent -> Meraki Workflow -> GitHub repository_dispatch webhook -> GitHub Actions workflow -> Ansible playbook run
```

GitHub webhook endpoint:

```text
POST https://api.github.com/repos/<OWNER>/<REPO>/dispatches
```

Required request headers:

- `Accept: application/vnd.github+json`
- `Authorization: Bearer <GITHUB_TOKEN>`

Supported dispatch patterns for Meraki workflow automation:

1. `event_type: deploy-ssids`
   - Workflow: `.github/workflows/deploy-ssids.yml`
   - Typical use: AI agent requests SSID deploy with optional dry-run and target networks.
   - Runs: SSID config update path, network desired-state update, deploy run, optional post-deploy compliance.
2. `event_type: run-ssid-management|run-compliance-check|run-config-snapshot|run-configure-network|run-playbook`
   - Workflow: `.github/workflows/playbook-dispatch.yml`
   - Typical use: AI agent picks one playbook directly.
   - Runs: selected playbook with optional `dry_run`, optional `target_networks`, optional `scope_ssid`.
3. `event_type: meraki-config-change`
   - Workflow: `.github/workflows/compliance.yml`
   - Typical use: AI agent detects a dashboard configuration change and triggers drift/compliance checks.
   - Runs: compliance check plus baseline snapshot.

Example payload from Meraki workflow to run SSID deploy:

```json
{
  "event_type": "deploy-ssids",
  "client_payload": {
    "environment": "production",
    "dry_run": true,
    "target_networks": "Site-A,Site-B",
    "scope_ssid": "Corp-Secure"
  }
}
```

Example payload from Meraki workflow to run one specific playbook:

```json
{
  "event_type": "run-playbook",
  "client_payload": {
    "playbook": "configure_network.yml",
    "target_networks": "Site-A,Site-B",
    "scope_ssid": "Corp-Secure",
    "dry_run": false,
    "commit_changes": true
  }
}
```

Webhook best practices:

- Keep secrets in GitHub secrets, not in `client_payload`.
- Default to `dry_run: true` for AI-initiated changes.
- Send explicit `target_networks` to limit blast radius.
- Require human approval in Meraki workflow before live changes.

## Recommended Execution Order

1. Validate target scope.

```bash
ansible-playbook -i inventory/production.yml playbooks/ssid_management.yml --list-hosts --list-tasks
```

2. Dry run with diff.

```bash
ansible-playbook -i inventory/production.yml playbooks/ssid_management.yml --check --diff
```

3. Limit blast radius for rollout.

```bash
ansible-playbook -i inventory/production.yml playbooks/ssid_management.yml --limit "Site-A"
```

4. Run live when dry-run output is acceptable.

```bash
ansible-playbook -i inventory/production.yml playbooks/ssid_management.yml
```

## Playbooks

- `playbooks/ssid_management.yml`: deploy SSID desired config.
- `playbooks/compliance_check.yml`: compare live state to desired state and security baseline.
- `playbooks/config_snapshot.yml`: capture live SSID state into `baselines/`.
- `playbooks/configure_network.yml`: update desired-state mapping for target networks.

## Validation Gates

Run locally before committing:

```bash
make lint
make test
make test-templates
```

- `make lint` runs `ansible-lint`.
- `make test` runs syntax checks for all playbooks with explicit inventory plus Jinja2 template parsing.
- `make test-templates` runs standalone Jinja2 template validation.

## Operational Guardrails

- Inventory is explicit by design; no implicit production default.
- Multi-network execution is serialized for safer rollout/check behavior.
- Compliance fetches fail closed on API errors (no silent success on failed data collection).
- Compliance notifications are only sent when violation conditions are met.

## Documentation

- [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- [docs/COMPLIANCE.md](docs/COMPLIANCE.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

## License

[MIT](LICENSE)
