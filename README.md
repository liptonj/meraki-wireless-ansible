# Meraki Wireless Ansible Automation

[![Ansible](https://img.shields.io/badge/Ansible-2.20.2-EE0000?logo=ansible)](https://www.ansible.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automate Cisco Meraki wireless network management with Ansible playbooks. This project provides production-ready automation for SSID management, bulk AP deployment, and compliance checking.

## 🎥 YouTube Episode

This project was created for **Unplugged Connectivity** with Dan Klamert. Follow along with the video tutorial to learn network automation with Ansible and Meraki.

**Video Timestamps:**
- `00:00` - Introduction and project overview
- `05:00` - Prerequisites and environment setup
- `15:00` - Forking and cloning the repository
- `20:00` - Environment setup and API key configuration
- `30:00` - Running your first playbook
- `40:00` - Understanding the architecture
- `50:00` - Troubleshooting common issues
- `55:00` - Q&A and next steps

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

- **[Getting Started](docs/GETTING_STARTED.md)** - Detailed setup guide with DevNet Sandbox instructions
- **[Architecture](docs/ARCHITECTURE.md)** - Project structure and data flow explanation
- **[Group Policy Drift Detection](docs/GROUP_POLICY_DRIFT.md)** - Configuration drift monitoring and remediation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common errors and solutions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## 🎯 What This Project Does

### Playbooks

- **`ssid_management.yml`** - Create, update, and manage wireless SSIDs across networks
- **`bulk_ap_deploy.yml`** - Deploy and configure multiple access points simultaneously
- **`compliance_check.yml`** - Validate network configurations against compliance standards
- **`group_policy_drift.yml`** - Detect and remediate group policy configuration drift

### Key Features

- ✅ **Idempotent Operations** - Safe to run multiple times
- ✅ **Configuration Drift Detection** - Maintain source of truth for group policies
- ✅ **Environment-Aware** - Separate configs for sandbox and production
- ✅ **Secure** - API keys stored in Ansible Vault
- ✅ **Beginner-Friendly** - Clear documentation and examples
- ✅ **Production-Ready** - Follows Ansible best practices

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
├── playbooks/          # Main Ansible playbooks
│   ├── ssid_management.yml
│   ├── bulk_ap_deploy.yml
│   ├── compliance_check.yml
│   └── group_policy_drift.yml
├── roles/              # Reusable Ansible roles
│   ├── meraki_ssid/
│   ├── meraki_devices/
│   ├── meraki_compliance/
│   └── meraki_group_policy_drift/
├── inventory/          # Host and group definitions
│   ├── sandbox.yml
│   └── production.yml.example
├── group_vars/         # Environment-specific variables
│   ├── all.yml
│   └── sandbox.yml
├── vault/              # Encrypted secrets (Ansible Vault)
│   └── secrets.yml.example
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
✅ Setting up Ansible for network automation
✅ Using the Cisco Meraki API with Ansible
✅ Creating reusable playbooks and roles
✅ Managing SSIDs, access points, and compliance checks
✅ Best practices for network automation

🔗 Links:
- Repository: [GitHub URL]
- Meraki Developer Hub: https://developer.cisco.com/meraki/
- Ansible Documentation: https://docs.ansible.com/

📚 Chapters:
00:00 Introduction
05:00 Prerequisites & Environment Setup
15:00 Forking & Cloning
20:00 Environment Setup
30:00 First Playbook
40:00 Architecture Deep Dive
50:00 Troubleshooting
55:00 Q&A

#NetworkAutomation #Ansible #Meraki #DevOps #NetworkEngineering #Cisco #InfrastructureAsCode
```

## 🏷️ Video Tags

```
network automation, ansible, meraki, cisco meraki, network engineering, devops, infrastructure as code, network management, wireless networks, ssid management, ansible playbooks, network automation tutorial, meraki api, network automation for beginners, ansible tutorial, network infrastructure, automation tools, network configuration, network operations, cisco devnet
```

---

**Ready to get started?** Head over to [GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed setup instructions!
