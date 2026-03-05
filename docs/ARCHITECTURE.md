# Architecture Documentation

This document explains the structure of the Meraki Wireless Ansible project, how components connect, and the data flow from inventory through playbooks and roles to the Meraki API.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Component Overview](#component-overview)
3. [Data Flow](#data-flow)
4. [How Playbooks and Roles Connect](#how-playbooks-and-roles-connect)
5. [Variable Precedence](#variable-precedence)
6. [Execution Flow](#execution-flow)

## Project Structure

```
meraki-wireless-ansible/
├── .ansible-lint              # Ansible linting configuration
├── .devcontainer/             # VS Code DevContainer config
├── .env.example               # Example environment variables
├── .github/
│   └── workflows/
│       ├── validate.yml       # CI/CD validation workflow
│       ├── deploy-ssids.yml   # SSID deployment workflow
│       └── compliance.yml     # Compliance check + snapshot workflow
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── ansible.cfg                # Ansible configuration file
├── Makefile                   # Development convenience commands
├── README.md                  # Project overview and quick start
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
├── requirements.txt           # Python dependencies
├── requirements.yml           # Ansible collection dependencies
│
├── playbooks/                 # Main Ansible playbooks
│   ├── ssid_management.yml    # SSID configuration management
│   ├── compliance_check.yml   # Compliance validation
│   └── config_snapshot.yml    # GitOps config capture
│
├── roles/                     # Reusable Ansible roles
│   ├── meraki_ssid/           # SSID management role
│   │   ├── defaults/
│   │   │   └── main.yml       # Default variables for SSID role
│   │   ├── tasks/
│   │   │   └── main.yml       # SSID management tasks
│   │   └── handlers/
│   │       └── main.yml       # Handlers (notifications)
│   ├── meraki_compliance/     # Compliance checking role
│   │   ├── defaults/
│   │   │   └── main.yml       # Default variables for compliance
│   │   ├── tasks/
│   │   │   ├── main.yml       # Drift detection tasks
│   │   │   └── security_baseline.yml  # Security baseline checks
│   │   └── templates/
│   │       └── compliance_report.md.j2  # Report template
│   └── meraki_snapshot/       # GitOps config capture role
│       ├── defaults/
│       │   └── main.yml       # Snapshot defaults (fields, paths)
│       └── tasks/
│           └── main.yml       # Pull, filter, compare, save
│
├── inventory/                 # Host and group definitions
│   ├── production.yml         # Production inventory (meraki_orgs)
│   └── development.yml.example # Development inventory template
│
├── group_vars/                # Group-specific variables
│   ├── all.yml                # Variables for all hosts
│   ├── meraki_orgs.yml        # SSID deployment config for meraki_orgs group
│   └── meraki_networks.yml    # Desired SSID state for compliance
│
├── baselines/                 # GitOps config snapshots (auto-updated)
│
├── vault/                     # Encrypted secrets (Ansible Vault)
│   └── secrets.yml.example    # Example vault file
│
├── scripts/                   # Utility scripts
│   ├── setup.sh               # Initial setup script
│   └── smoke_test.sh          # Validation test script
│
└── docs/                      # Documentation
    ├── GETTING_STARTED.md     # Setup guide
    ├── ARCHITECTURE.md        # This file
    ├── COMPLIANCE.md          # Compliance and security baselines
    └── TROUBLESHOOTING.md     # Troubleshooting guide
```

## Component Overview

### Playbooks (`playbooks/`)

Playbooks are the entry point for Ansible automation. They define **what** to do and **where** to do it.

**Structure:**
```yaml
---
- name: Descriptive name
  hosts: target_group        # From inventory
  gather_facts: false       # Don't gather system facts
  become: false             # Don't use sudo
  
  vars:                     # Playbook-level variables
    # Override defaults here
  
  roles:                    # Which roles to execute
    - role_name
```

**Example: `playbooks/ssid_management.yml`**
```yaml
---
- name: Manage Meraki SSIDs
  hosts: meraki_orgs        # Targets all hosts in meraki_orgs group
  gather_facts: false
  become: false
  
  roles:
    - meraki_ssid            # Executes tasks from roles/meraki_ssid/
```

### Roles (`roles/`)

Roles are reusable collections of tasks, variables, handlers, and templates. They define **how** to accomplish a task.

**Role Structure:**
- `defaults/main.yml` - Default variables (lowest precedence)
- `tasks/main.yml` - Main task execution
- `handlers/main.yml` - Handlers (notifications triggered by tasks)
- `templates/` - Jinja2 templates for generating files
- `vars/main.yml` - Role-specific variables (higher precedence than defaults)

**Example Role: `roles/meraki_ssid/`**
```
meraki_ssid/
├── defaults/main.yml     # Default SSID configuration
├── tasks/main.yml        # SSID management logic
└── handlers/main.yml     # Handlers for SSID changes
```

### Inventory (`inventory/`)

Inventory files define **where** playbooks run. They list hosts and organize them into groups.

**Example: `inventory/production.yml`**
```yaml
all:
  children:
    meraki_orgs:              # Group name (referenced in playbooks)
      hosts:
        labnet:                # Host name
          meraki_org_id: "{{ vault_meraki_org_id }}"
          meraki_api_key: "{{ vault_meraki_api_key }}"
```

**Key Concepts:**
- **Hosts**: Individual targets (e.g., `labnet`, `secondary-org`)
- **Groups**: Collections of hosts (e.g., `meraki_orgs`)
- **Host Variables**: Variables specific to a host
- **Group Variables**: Variables for all hosts in a group

### Group Variables (`group_vars/`)

Group variables provide configuration for groups of hosts.

**`group_vars/all.yml`** - Applies to ALL hosts:
```yaml
meraki_base_url: "https://api.meraki.com"
meraki_api_timeout: 30
```

**`group_vars/meraki_orgs.yml`** - SSID deployment config for `meraki_orgs` inventory group:
```yaml
meraki_environment: production
meraki_api_timeout: 60
```

### Ansible Configuration (`ansible.cfg`)

The `ansible.cfg` file configures Ansible behavior:

```ini
[defaults]
inventory = inventory/production.yml  # Default inventory file
host_key_checking = False             # Don't check SSH host keys
retry_files_enabled = False           # Don't create retry files
gathering = smart                     # Smart fact gathering
```

## Data Flow

Understanding data flow is crucial for debugging and customization.

### Complete Data Flow Diagram

```
┌─────────────────┐
│   User Runs     │
│   Playbook      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ansible.cfg    │◄─── Configuration (inventory path, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Inventory     │◄─── Defines hosts and groups
│ (production.yml)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  group_vars/    │◄─── Provides variables for groups
│  all.yml        │
│  meraki_orgs.yml│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Playbook     │◄─── Defines what to do
│ (ssid_manage)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      Role       │◄─── Defines how to do it
│  (meraki_ssid)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Role Tasks     │◄─── Executes Ansible modules
│  (main.yml)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Meraki API     │◄─── Makes HTTP requests
│  (cisco.meraki) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Meraki Cloud   │◄─── Actual API endpoint
│  Dashboard API  │
└─────────────────┘
```

### Step-by-Step Execution

1. **User executes**: `ansible-playbook playbooks/ssid_management.yml`

2. **Ansible reads `ansible.cfg`**:
   - Determines which inventory file to use (`inventory/production.yml`)
   - Sets connection and other defaults

3. **Ansible loads inventory** (`inventory/production.yml`):
   - Identifies target hosts (`labnet`)
   - Groups hosts (`meraki_orgs`)
   - Loads host-specific variables

4. **Ansible loads group variables**:
   - `group_vars/all.yml` → applies to all hosts
   - `group_vars/meraki_orgs.yml` → SSID deployment config for meraki_orgs group

5. **Playbook execution begins**:
   - Playbook defines target hosts: `hosts: meraki_orgs`
   - Ansible matches this to inventory groups

6. **Role execution**:
   - Playbook calls `roles: - meraki_ssid`
   - Ansible loads role defaults (`roles/meraki_ssid/defaults/main.yml`)
   - Ansible executes role tasks (`roles/meraki_ssid/tasks/main.yml`)

7. **Task execution**:
   - Each task in `tasks/main.yml` runs sequentially
   - Tasks use Ansible modules (e.g., `cisco.meraki.networks_ssids`)
   - Modules make API calls to Meraki

8. **API interaction**:
   - Modules use variables like `meraki_api_key` and `meraki_org_id`
   - HTTP requests sent to `https://api.meraki.com/api/v1/...`
   - Responses processed and displayed

## How Playbooks and Roles Connect

### Connection Mechanism

Playbooks reference roles using the `roles:` keyword:

```yaml
# playbooks/ssid_management.yml
---
- name: Manage Meraki SSIDs
  hosts: meraki_orgs
  roles:
    - meraki_ssid    # ← References roles/meraki_ssid/
```

When Ansible encounters `- meraki_ssid`, it:
1. Looks for `roles/meraki_ssid/` directory
2. Loads `roles/meraki_ssid/defaults/main.yml` (variables)
3. Executes `roles/meraki_ssid/tasks/main.yml` (tasks)
4. Loads `roles/meraki_ssid/handlers/main.yml` (if referenced)

### Variable Passing

Variables flow from multiple sources into roles:

```yaml
# 1. Role defaults (lowest priority)
# roles/meraki_ssid/defaults/main.yml
ssid_name: "Guest Network"
ssid_enabled: true

# 2. Group variables (medium priority)
# group_vars/all.yml
ssid_enabled: false  # Overrides role default

# 3. Playbook variables (high priority)
# playbooks/ssid_management.yml
vars:
  ssid_enabled: true  # Overrides group vars

# 4. Inventory host variables (highest priority)
# inventory/production.yml
hosts:
  labnet:
    ssid_enabled: false  # Overrides everything
```

### Task Execution Order

Within a role, tasks execute in order:

```yaml
# roles/meraki_ssid/tasks/main.yml
---
- name: Get current SSIDs
  # Task 1: Runs first

- name: Update SSID configuration
  # Task 2: Runs second (can use results from Task 1)

- name: Verify SSID is active
  # Task 3: Runs third (can use results from Task 2)
```

## Variable Precedence

Ansible has a specific order for variable precedence (lowest to highest):

1. **Role defaults** (`roles/*/defaults/main.yml`)
2. **Inventory group variables** (`group_vars/all.yml`)
3. **Inventory host variables** (`inventory/*.yml` host vars)
4. **Playbook variables** (`vars:` in playbook)
5. **Role variables** (`roles/*/vars/main.yml`)
6. **Set facts** (variables set during playbook execution)
7. **Command-line variables** (`-e "var=value"`)

**Example:**
```yaml
# 1. Role default
# roles/meraki_ssid/defaults/main.yml
timeout: 30

# 2. Group variable (overrides #1)
# group_vars/all.yml
timeout: 60

# 3. Playbook variable (overrides #2)
# playbooks/ssid_management.yml
vars:
  timeout: 90

# Final value used: 90
```

## Execution Flow

### Example: Running SSID Management Playbook

```bash
$ ansible-playbook playbooks/ssid_management.yml
```

**What happens:**

1. **Initialization**
   ```
   Ansible reads ansible.cfg
   → Loads inventory: inventory/production.yml
   → Identifies hosts: labnet
   → Groups: meraki_orgs
   ```

2. **Variable Loading**
   ```
   Load group_vars/all.yml
   → meraki_base_url: "https://api.meraki.com"
   → meraki_api_timeout: 30
   
   Load group_vars/meraki_orgs.yml
   → meraki_environment: production
   → meraki_api_timeout: 60 (overrides all.yml)
   
   Load inventory/production.yml host vars
   → meraki_org_id: "YOUR_ORG_ID"
   → meraki_api_key: "***" (from vault or .env)
   ```

3. **Playbook Execution**
   ```
   Play: Manage Meraki SSIDs
   → Target: hosts in meraki_orgs group
   → Found: labnet host
   ```

4. **Role Execution**
   ```
   Role: meraki_ssid
   → Load defaults: roles/meraki_ssid/defaults/main.yml
   → Execute tasks: roles/meraki_ssid/tasks/main.yml
   ```

5. **Task Execution**
   ```
   Task 1: Get organization networks
   → Module: cisco.meraki.organizations_networks_info
   → API Call: GET /organizations/{org_id}/networks
   → Result: List of networks
   
   Task 2: Update SSID configuration
   → Module: cisco.meraki.networks_ssids
   → API Call: PUT /networks/{network_id}/ssids/{ssid_number}
   → Result: SSID updated
   ```

6. **Completion**
   ```
   All tasks completed
   → Summary displayed
   → Exit code: 0 (success)
   ```

## Key Design Patterns

### 1. Idempotency

All tasks are designed to be **idempotent** - running them multiple times produces the same result:

```yaml
- name: Ensure SSID exists
  cisco.meraki.networks_ssids:
    state: present
    # If SSID already exists with same config → no change
    # If SSID doesn't exist → creates it
    # If SSID exists with different config → updates it
```

### 2. Environment Separation

Different configurations for different environments:

```
inventory/
├── production.yml     # Production environment
└── development.yml   # Development (not in repo)

group_vars/
├── all.yml            # Common settings
└── meraki_orgs.yml    # SSID deployment config for meraki_orgs group
```

### 3. Role Reusability

Roles can be used by multiple playbooks:

```yaml
# playbooks/ssid_management.yml
roles:
  - meraki_ssid

# playbooks/compliance_check.yml
roles:
  - meraki_compliance

# playbooks/config_snapshot.yml
roles:
  - meraki_snapshot
```

### 4. Variable Layering

Configuration through multiple layers:

```
Defaults → Group Vars → Playbook Vars → Host Vars
(lowest priority)                    (highest priority)
```

## Understanding the Meraki API Integration

### API Module Usage

Roles use Ansible modules from the `cisco.meraki` collection:

```yaml
# Example task
- name: Get SSID information
  cisco.meraki.networks_wireless_ssids_info:
    networkId: "{{ meraki_network_id }}"
    meraki_api_key: "{{ meraki_api_key }}"
  register: ssid_info
```

### Authentication Flow

1. API key loaded from:
   - Environment variable `MERAKI_DASHBOARD_API_KEY`
   - Ansible Vault (`vault/secrets.yml` as `vault_meraki_api_key`)
   - GitHub Actions secrets (for CI/CD)

2. Key passed to modules via `meraki_api_key` parameter

3. Modules add header: `Authorization: Bearer {key}`

4. Meraki API validates and processes request

## Next Steps

- **Customize**: Edit `group_vars/` files to match your needs
- **Extend**: Add new roles or playbooks following the same patterns
- **Debug**: Use `-vvv` flag to see detailed execution flow
- **Troubleshoot**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

---

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub!
