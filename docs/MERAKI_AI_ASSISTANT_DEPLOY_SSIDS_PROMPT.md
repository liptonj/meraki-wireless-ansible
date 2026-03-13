# Meraki AI Assistant Prompt: Deploy SSID

```text
Generate a workflow that can create or update an Ansible-managed SSID by triggering the Meraki Wireless Ansible GitHub dispatch workflow.

User must provide the following
- Get Meraki Organization by Name
- Get Meraki Network by Name
- SSID Name
- Auth Mode
- Encryption Mode
- Band Selection
- SSID Enabled
- SSID Visible
- Dry Run
- PSK Secret when Auth Mode is `psk`

Generate 1 Output variable
- Markdown listing the workflow name, organization name, network name, SSID name, dry run value, and GitHub dispatch status.

Additional Details:
- The workflow name must be `Wireless Ansible Trigger`.
- Resolve the organization by name using the existing `getOrganizationByName` atomic.
- Resolve the network by name using the existing `getNetworkByName` atomic.
- Use the resolved Meraki Network name as the `target_networks` value in the GitHub payload.
- Set `scope_ssid` to the provided SSID Name.
- Send a `POST` request to `https://api.github.com/repos/liptonj/meraki-wireless-ansible/dispatches`.
- Send headers:
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer <GITHUB_TOKEN>`
  - `Content-Type: application/json`
- Send this payload shape:
  {
    "event_type": "meraki_wireless_ansible",
    "client_payload": {
      "target_networks": "<Resolved Network Name>",
      "scope_ssid": "<SSID Name>",
      "auth_mode": "<Auth Mode>",
      "encryption_mode": "<Encryption Mode>",
      "band_selection": "<Band Selection>",
      "ssid_enabled": true,
      "ssid_visible": true,
      "dry_run": false,
      "psk_secret": "<PSK Secret if required>"
    }
  }
- Only include `psk_secret` in the payload when Auth Mode is `psk`.
- Handle `ssid_enabled` and `ssid_visible` explicitly as Booleans.
- Handle `dry_run` explicitly as a Boolean.
- Treat HTTP `204 No Content` as a successful dispatch.

Constraint Checklist & Confidence Score:
- Use existing Meraki Atomics as sub-workflows for organization and network lookup
- Do not hallucinate API endpoints; use the atomic library for Meraki lookups
- Do not use a Meraki atomic for the final trigger unless one exists for GitHub repository dispatch; use a standard HTTP request activity for that step because the target is GitHub, not the Meraki Dashboard API
- Ensure variable types (Strings vs Booleans) are handled explicitly via Python script blocks where necessary
- Safety: save the resolved organization object and resolved network object to distinct variables before building the dispatch payload
- Tooling: use standard Meraki Atomics for all possible Meraki interactions

Make sure and use Atomics for your activities unless absolutely not possible.
```
