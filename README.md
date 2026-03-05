# Meraki Wireless Ansible Automation

[![Ansible](https://img.shields.io/badge/Ansible-2.20.2-EE0000?logo=ansible)](https://www.ansible.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automate Cisco Meraki wireless network management with Ansible playbooks. This project provides production-ready automation for SSID management, bulk AP deployment, and compliance checking.

## Quick Start

### Prerequisites

- **Python 3.12+** (required for Ansible 2.20.2)
- **Git** for cloning the repository
- **Meraki API Key** (get one from [Meraki Dashboard](https://dashboard.meraki.com/) — see [Getting Started](docs/GETTING_STARTED.md) for details)
- **Meraki Organization Name** (the name of your org in Meraki Dashboard)
- **Meraki Network Name(s)** (the name(s) of the networks you want to manage)

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/meraki-wireless-ansible.git
cd meraki-wireless-ansible
```

### 2. Setup Environment

```bash
make setup
source venv/bin/activate
```

### 3. Configure API Credentials

```bash
cp .env.example .env
# Edit .env and add your credentials:
# MERAKI_DASHBOARD_API_KEY=your_api_key_here
# MERAKI_ORG_NAME=your_organization_name_here
# MERAKI_NETWORK_NAMES=Site-A,Site-B,Site-C
```

### 4. Run Your First Playbook

```bash
ansible-playbook --syntax-check playbooks/ssid_management.yml
ansible-playbook playbooks/ssid_management.yml
```

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Setup guide with GitHub Actions configuration
- **[Architecture](docs/ARCHITECTURE.md)** - Project structure and data flow
- **[Compliance](docs/COMPLIANCE.md)** - SSID compliance checking and security baselines
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common errors and solutions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## What This Project Does

### Playbooks

- **`ssid_management.yml`** - Deploy and configure wireless SSIDs across networks
- **`compliance_check.yml`** - Validate SSID configurations against desired state and security baselines
- **`config_snapshot.yml`** - Capture live Meraki config and store as GitOps baseline

### Key Features

- **Name-Based Discovery** - Reference orgs and networks by name, not IDs
- **Multi-Network Support** - Manage multiple networks in a single playbook run
- **GitOps for Wireless** - Config stored in Git, drift detected automatically
- **Security Baselines** - No open auth, WPA2 minimum, guest bandwidth limits
- **Automated Alerting** - GitHub Issues + Webex Teams on compliance violations
- **CI/CD Native** - Everything runs in GitHub Actions (deploy, check, alert, snapshot)
- **Idempotent Operations** - Safe to run multiple times
- **Environment-Aware** - Separate configs for production and development

## Available Commands

```bash
make setup      # Initial project setup
make lint       # Check code quality
make test       # Validate playbook syntax
make smoke-test # Run validation tests
make clean      # Remove virtual environment
```

## Project Structure

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
│   ├── meraki_discovery/
│   ├── meraki_ssid/
│   ├── meraki_compliance/
│   └── meraki_snapshot/
├── inventory/          # Host and group definitions
│   └── production.yml
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

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed explanation.

## Security Best Practices

- **Never commit API keys** - Use `.env` files (gitignored) or Ansible Vault
- **Use names, not IDs** - Org and network names are resolved at runtime
- **Use environment variables** - Load secrets from `.env` files
- **Encrypt sensitive data** - Use `ansible-vault encrypt` for production secrets
- **Review before running** - Always check playbooks before executing

## Troubleshooting

Common issues and solutions:

- **Rate Limiting** - Meraki API has rate limits. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#rate-limiting)
- **Authentication Errors** - Verify API key and organization ID. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#authentication-errors)
- **API Issues** - Check API status and endpoint configuration. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#api-issues)

For detailed troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make lint && make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Cisco Meraki** for the excellent Dashboard API
- **Ansible Community** for the powerful automation framework

---

**Ready to get started?** Head over to [GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed setup instructions!
