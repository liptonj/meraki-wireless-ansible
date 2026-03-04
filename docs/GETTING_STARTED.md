# Getting Started Guide

This guide will walk you through setting up the Meraki Wireless Ansible project from scratch. You'll need access to a Meraki organization with API enabled — either your own or a test/lab environment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Meraki API Access](#meraki-api-access)
3. [Forking and Cloning](#forking-and-cloning)
4. [Environment Setup](#environment-setup)
5. [API Key Configuration](#api-key-configuration)
6. [Running Your First Playbook](#running-your-first-playbook)
7. [Running Each Playbook](#running-each-playbook)
8. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python 3.12 or higher**
  ```bash
  python3 --version
  # Should show Python 3.12.x or higher
  ```
  
  If you need to install Python:
  - **macOS**: `brew install python@3.12`
  - **Linux**: `sudo apt-get install python3.12` (Ubuntu/Debian) or use your distribution's package manager
  - **Windows**: Download from [python.org](https://www.python.org/downloads/)

- **Git**
  ```bash
  git --version
  ```
  
  If you need to install Git:
  - **macOS**: `brew install git`
  - **Linux**: `sudo apt-get install git`
  - **Windows**: Download from [git-scm.com](https://git-scm.com/download/win)

- **Make** (optional, but recommended)
  ```bash
  make --version
  ```
  
  If you need to install Make:
  - **macOS**: Usually pre-installed, or `xcode-select --install`
  - **Linux**: `sudo apt-get install build-essential`
  - **Windows**: Install via [Chocolatey](https://chocolatey.org/) or use Git Bash

### Required Accounts

- **GitHub Account** - For forking and cloning the repository
- **Meraki Account** - A Meraki organization with API access enabled

## Meraki API Access

You need a Meraki Dashboard account with API access to use this project. Here's how to get set up.

### Step 1: Enable API Access

1. Log in to [Meraki Dashboard](https://dashboard.meraki.com/)
2. Navigate to **Organization** > **Settings**
3. Scroll to **Dashboard API access**
4. Check **"Enable access to the Cisco Meraki Dashboard API"**
5. Click **Save Changes**

### Step 2: Generate Your API Key

1. In the Meraki Dashboard, click your email/profile in the top right
2. Select **My profile**
3. Scroll to **API access**
4. Click **"Generate new API key"**
5. **Copy this key immediately** — you won't be able to see it again!
6. If you lose it, you can revoke and regenerate a new one

### Step 3: Find Your Organization ID

You can find your organization ID in two ways:

**Option 1**: From the Dashboard URL — look for the number after `/o/` in your URL:
`https://dashboard.meraki.com/o/YOUR_ORG_ID/...`

**Option 2**: Using the API:

```bash
curl -X GET "https://api.meraki.com/api/v1/organizations" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

### Step 4: Verify API Access

Verify your API key works by listing your networks:

```bash
curl -X GET "https://api.meraki.com/api/v1/organizations/YOUR_ORG_ID/networks" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

If successful, you'll see a JSON response with network information.

### Test Environment Recommendations

For learning and testing, consider using a dedicated test organization or network to avoid impacting production:

- **Separate test network** — Create a network in your org specifically for automation testing
- **Read-only first** — Start with read-only operations (the `_info` modules) before running write operations
- **Check mode** — Use `--check` flag to preview changes without applying them

> **Note**: The Meraki API enforces rate limits (typically 5 requests per second per organization). The playbooks in this project include retry logic and rate limiting to handle this.

## Forking and Cloning

### Step 1: Fork the Repository

1. Go to the [meraki-wireless-ansible repository](https://github.com/YOUR_ORG/meraki-wireless-ansible)
2. Click the **"Fork"** button in the top right
3. Choose your GitHub account as the destination
4. Wait for the fork to complete

### Step 2: Clone Your Fork

```bash
# Replace YOUR_USERNAME with your GitHub username
git clone https://github.com/YOUR_USERNAME/meraki-wireless-ansible.git
cd meraki-wireless-ansible
```

### Step 3: Add Upstream Remote (Optional)

If you want to sync with the original repository:

```bash
git remote add upstream https://github.com/ORIGINAL_ORG/meraki-wireless-ansible.git
```

## Environment Setup

### Step 1: Run the Setup Script

The project includes a Makefile with a convenient setup command:

```bash
make setup
```

This will:
- Create a Python virtual environment (`venv/`)
- Install all Python dependencies from `requirements.txt`
- Install Ansible collections from `requirements.yml`
- Create a `.env` file from `.env.example` (if it doesn't exist)

### Step 2: Activate the Virtual Environment

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt)
.\venv\Scripts\activate.bat
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### Step 3: Verify Installation

```bash
# Check Ansible version
ansible --version
# Should show: ansible [core 2.20.2]

# Check Python version
python --version
# Should show: Python 3.12.x

# Verify collections are installed
ansible-galaxy collection list
# Should show: cisco.meraki and community.general
```

## API Key Configuration

### Option A: Using Environment Variables (Recommended for Development)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your preferred editor:
   ```bash
   # Using nano
   nano .env
   
   # Using vim
   vim .env
   
   # Using VS Code
   code .env
   ```

3. Add your credentials:
   ```bash
   # Your Meraki Dashboard API key
   MERAKI_DASHBOARD_API_KEY=your_api_key_here
   
   # Your Meraki organization ID
   MERAKI_ORG_ID=your_org_id_here
   
   # Environment: sandbox (for testing) or production
   ENVIRONMENT=sandbox
   ```

4. **Important**: The `.env` file is gitignored, so your secrets won't be committed.

### Option B: Using Ansible Vault (Recommended for Production)

For production environments, use Ansible Vault to encrypt your secrets:

1. Copy the example vault file:
   ```bash
   cp vault/secrets.yml.example vault/secrets.yml
   ```

2. Edit `vault/secrets.yml`:
   ```yaml
   vault_meraki_api_key: "your_api_key_here"
   vault_meraki_org_id: "your_org_id_here"
   ```

3. Encrypt the file:
   ```bash
   ansible-vault encrypt vault/secrets.yml
   ```
   
   You'll be prompted to create a vault password. Remember this password!

4. When running playbooks, use:
   ```bash
   ansible-playbook --ask-vault-pass playbooks/ssid_management.yml
   ```

### Finding Your Organization ID

See [Meraki API Access](#meraki-api-access) above for instructions on finding your organization ID via the Dashboard URL or the API.

## Running Your First Playbook

### Step 1: Verify Configuration

Before running any playbook, verify your setup:

```bash
# Check playbook syntax
ansible-playbook --syntax-check playbooks/ssid_management.yml

# Dry run (check mode - won't make changes)
ansible-playbook --check playbooks/ssid_management.yml

# Verbose output (for debugging)
ansible-playbook -vvv playbooks/ssid_management.yml
```

### Step 2: Run the SSID Management Playbook

```bash
# Basic run
ansible-playbook playbooks/ssid_management.yml

# With verbose output
ansible-playbook -vv playbooks/ssid_management.yml

# With vault password (if using Ansible Vault)
ansible-playbook --ask-vault-pass playbooks/ssid_management.yml
```

### Step 3: Verify Results

The playbook will output task results. Look for:
- ✅ **ok** - Task completed successfully (no changes needed)
- ✅ **changed** - Task made changes
- ❌ **failed** - Task encountered an error

## Running Each Playbook

### SSID Management Playbook

Manages wireless SSID configuration across Meraki networks.

```bash
ansible-playbook playbooks/ssid_management.yml
```

**What it does:**
- Creates or updates SSID configurations
- Ensures SSIDs match your defined standards
- Can enable/disable SSIDs

**Configuration:**
- Edit `group_vars/all.yml` or `group_vars/sandbox.yml` to define SSID settings
- Variables are documented in `roles/meraki_ssid/defaults/main.yml`

### Bulk AP Deployment Playbook

Deploys and configures access points in bulk.

```bash
ansible-playbook playbooks/bulk_ap_deploy.yml
```

**What it does:**
- Provisions multiple access points
- Configures AP settings (name, tags, location)
- Assigns APs to networks

**Configuration:**
- Define AP configurations in `group_vars/` files
- See `roles/meraki_devices/defaults/main.yml` for available options

### Compliance Check Playbook

Validates network configurations against compliance standards.

```bash
ansible-playbook playbooks/compliance_check.yml
```

**What it does:**
- Checks SSID security settings
- Validates network configurations
- Generates compliance reports

**Configuration:**
- Define compliance rules in `group_vars/` files
- Reports are generated in `reports/` directory

## Next Steps

Now that you have the project set up:

1. **Explore the Architecture** - Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how everything connects
2. **Customize Configuration** - Edit `group_vars/` files to match your needs
3. **Run More Playbooks** - Try all three playbooks and see what they do
4. **Read Troubleshooting Guide** - Bookmark [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for when things go wrong
5. **Contribute** - See [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute improvements

## Common First-Time Issues

### Issue: "ansible: command not found"

**Solution**: Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

### Issue: "Module not found: cisco.meraki"

**Solution**: Install the collections:
```bash
ansible-galaxy collection install -r requirements.yml
```

### Issue: "Authentication failed"

**Solution**: 
- Verify your API key is correct in `.env`
- Check that your organization ID matches your account
- See [Meraki API Access](#meraki-api-access) for how to verify your credentials

### Issue: "Rate limit exceeded"

**Solution**: The Meraki API has rate limits. Wait a few seconds and try again. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#rate-limiting) for details.

## Getting Help

- **Documentation**: Check the [docs/](.) directory
- **Issues**: Open an issue on GitHub
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Ready to dive deeper?** Check out [ARCHITECTURE.md](ARCHITECTURE.md) to understand how everything works!
