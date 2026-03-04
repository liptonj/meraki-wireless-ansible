# Meraki Wireless Ansible Automation

[![Ansible](https://img.shields.io/badge/Ansible-2.20.2-EE0000?logo=ansible)](https://www.ansible.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automate Cisco Meraki wireless network management with Ansible playbooks. This project provides production-ready automation for SSID management, bulk AP deployment, and compliance checking.

## 🎥 YouTube Episode

This project was created for **Unplugged Connectivity** with Dan Klamert. Follow along with the video tutorial to learn network automation with Ansible and Meraki.

**Video Timestamps:**
- `00:00` - Cold open: See compliance alerting in action
- `01:00` - Introduction: Why automate wireless with Ansible?
- `03:00` - Fork, clone, and configure GitHub secrets
- `09:00` - Deploy an SSID via GitHub Actions
- `14:00` - Compliance check runs automatically — all green
- `18:00` - Simulate a rogue change — compliance fails
- `21:00` - Alerts fire: GitHub Issue + Webex Teams notification
- `24:00` - Workflow triggers: schedule, webhook, and manual dispatch
- `27:00` - Recap and next steps

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (required for Ansible 2.20.2)
- **Git** for cloning the repository
- **Meraki API Key** (get one from [Meraki Dashboard](https://dashboard.meraki.com/) — see [Getting Started](docs/GETTING_STARTED.md) for details)
- **Meraki Organization ID** (found in your Meraki Dashboard URL or API)

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/meraki-wireless-ansible.git
cd meraki-wireless-ansible
```

### 2. Setup Environment

```bash
# One-command setup (creates venv, installs dependencies)
make setup

# Activate the virtual environment
source venv/bin/activate
```

### 3. Configure API Credentials

**Option A: Using a Test/Sandbox Organization (Recommended for Learning)**

See [Getting Started](docs/GETTING_STARTED.md#api-key-configuration) for detailed instructions on configuring a test environment.

**Option B: Using Your Own Meraki Organization**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
# MERAKI_API_KEY=your_api_key_here
# MERAKI_ORG_ID=your_org_id_here
```

### 4. Run Your First Playbook

```bash
# Verify your setup
ansible-playbook --syntax-check playbooks/ssid_management.yml

# Run the SSID management playbook
ansible-playbook playbooks/ssid_management.yml
```

## 📚 Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Setup guide with GitHub Actions configuration
- **[Architecture](docs/ARCHITECTURE.md)** - Project structure and data flow
- **[Compliance](docs/COMPLIANCE.md)** - SSID compliance checking and security baselines
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common errors and solutions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## 🎯 What This Project Does

### Playbooks

- **`ssid_management.yml`** - Deploy and configure wireless SSIDs across networks
- **`compliance_check.yml`** - Validate SSID configurations against desired state and security baselines
- **`config_snapshot.yml`** - Capture live Meraki config and store as GitOps baseline

### Key Features

- ✅ **GitOps for Wireless** - Config stored in Git, drift detected automatically
- ✅ **Security Baselines** - No open auth, WPA2 minimum, guest bandwidth limits
- ✅ **Automated Alerting** - GitHub Issues + Webex Teams on compliance violations
- ✅ **CI/CD Native** - Everything runs in GitHub Actions (deploy, check, alert, snapshot)
- ✅ **Idempotent Operations** - Safe to run multiple times
- ✅ **Environment-Aware** - Separate configs for sandbox and production

## 🛠️ Available Commands

```bash
make setup      # Initial project setup
make lint       # Check code quality
make test       # Validate playbook syntax
make smoke-test # Validate setup and test API connectivity
make clean      # Remove virtual environment
```

## 📖 Project Structure

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
│   ├── meraki_ssid/
│   ├── meraki_compliance/
│   └── meraki_snapshot/
├── inventory/          # Host and group definitions
│   ├── sandbox.yml
│   └── sandbox_compliance.yml
├── group_vars/         # Environment-specific variables
│   ├── all.yml
│   ├── sandbox.yml
│   └── meraki_networks.yml
├── baselines/          # GitOps config snapshots (auto-updated)
├── vault/              # Encrypted secrets (Ansible Vault)
│   └── secrets.yml.example
├── reports/            # Generated compliance reports
└── docs/               # Documentation
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed explanation.

## 🔐 Security Best Practices

- **Never commit API keys** - Use `.env` files (gitignored) or Ansible Vault
- **Use environment variables** - Load secrets from `.env` files
- **Encrypt sensitive data** - Use `ansible-vault encrypt` for production secrets
- **Review before running** - Always check playbooks before executing in production

## 🐛 Troubleshooting

Common issues and solutions:

- **Rate Limiting** - Meraki API has rate limits. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#rate-limiting)
- **Authentication Errors** - Verify API key and organization ID. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#authentication-errors)
- **Sandbox Limitations** - Test/sandbox environments may have restrictions. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#sandbox-limitations)

For detailed troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make lint && make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Cisco Meraki** for the excellent Dashboard API
- **Ansible Community** for the powerful automation framework
- **Unplugged Connectivity** for the platform to share knowledge

## 📺 Video Description Template

```
🚀 Automate Cisco Meraki Wireless Networks with Ansible!

In this episode, we'll build a complete Ansible automation project for managing Meraki wireless networks. Perfect for network engineers and DevOps professionals looking to automate repetitive tasks.

What you'll learn:
✅ Deploy wireless SSIDs via GitHub Actions + Ansible + Meraki API
✅ Run automated compliance checks — no local tools needed
✅ Auto-alert on violations via GitHub Issues + Webex Teams
✅ Trigger workflows on push, schedule, or Meraki webhook
✅ Build a closed-loop wireless compliance system in CI/CD

🔗 Links:
- Repository: [GitHub URL]
- Meraki Developer Hub: https://developer.cisco.com/meraki/
- Ansible Documentation: https://docs.ansible.com/

📚 Chapters:
00:00 Cold Open — Compliance Alert Demo
01:00 Introduction — Why Automate Wireless?
03:00 Fork, Clone & Configure GitHub Secrets
09:00 Deploy an SSID via GitHub Actions
14:00 Compliance Check Runs Automatically
18:00 Simulate a Rogue Change
21:00 Alerts: GitHub Issue + Webex Teams
24:00 Workflow Triggers: Schedule, Webhook & Manual
27:00 Recap & Next Steps

#NetworkAutomation #Ansible #Meraki #DevOps #NetworkEngineering #Cisco #InfrastructureAsCode
```

## 🏷️ Video Tags

```
network automation, ansible, meraki, cisco meraki, network engineering, devops, infrastructure as code, network management, wireless networks, ssid management, ansible playbooks, network automation tutorial, meraki api, network automation for beginners, ansible tutorial, network infrastructure, automation tools, network configuration, network operations, cisco devnet
```

---

**Ready to get started?** Head over to [GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed setup instructions!
