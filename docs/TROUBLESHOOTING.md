# Troubleshooting Guide

This guide covers common errors, their causes, and solutions. If you encounter an issue not covered here, please open an issue on GitHub.

## Table of Contents

1. [Rate Limiting](#rate-limiting)
2. [Authentication Errors](#authentication-errors)
3. [API Limitations](#api-limitations)
4. [API Issues](#api-issues)
5. [Ansible Configuration Issues](#ansible-configuration-issues)
6. [Python and Dependency Issues](#python-and-dependency-issues)
7. [Playbook Execution Errors](#playbook-execution-errors)
8. [Debugging Tips](#debugging-tips)

## Rate Limiting

### Symptoms

```
fatal: [labnet]: FAILED! => {
    "msg": "Rate limit exceeded. Please wait before retrying."
}
```

Or:
```
HTTP 429 Too Many Requests
```

### Cause

The Meraki API enforces rate limits to prevent abuse:
- **Standard API**: 5 requests per second per organization
- **Test environments**: May have stricter limits
- **Burst requests**: Can trigger temporary rate limiting

### Solutions

#### Solution 1: Add Delays Between Requests

Edit your role tasks to add delays:

```yaml
# roles/meraki_ssid/tasks/main.yml
- name: Get networks
  cisco.meraki.organizations_networks_info:
    # ... parameters
  register: networks

- name: Wait between API calls
  pause:
    seconds: 1  # Wait 1 second between calls

- name: Update SSID
  cisco.meraki.networks_ssids:
    # ... parameters
```

#### Solution 2: Use Retry Logic

Ansible modules typically include retry logic, but you can add explicit retries:

```yaml
- name: Update SSID with retry
  cisco.meraki.networks_ssids:
    # ... parameters
  register: result
  until: result.failed == false
  retries: 5
  delay: 2  # Wait 2 seconds between retries
```

#### Solution 3: Reduce Parallel Execution

Limit concurrent operations:

```bash
# Run with fewer parallel hosts
ansible-playbook --forks=1 playbooks/ssid_management.yml
```

#### Solution 4: Check Rate Limit Status

Use the Meraki API to check your rate limit status:

```bash
curl -I "https://api.meraki.com/api/v1/organizations" \
  -H "X-Cisco-Meraki-API-Key: YOUR_API_KEY"
```

Look for headers:
- `X-Rate-Limit-Limit`: Maximum requests per window
- `X-Rate-Limit-Remaining`: Remaining requests in current window
- `Retry-After`: Seconds to wait before retrying (if rate limited)

### Prevention

- **Batch operations**: Group multiple changes into single API calls when possible
- **Cache results**: Use Ansible fact caching to avoid repeated API calls
- **Sequential execution**: Process items one at a time for bulk operations

## Authentication Errors

### Symptoms

```
fatal: [labnet]: FAILED! => {
    "msg": "Invalid API key"
}
```

Or:
```
HTTP 401 Unauthorized
```

### Cause

Authentication failures occur when:
- API key is incorrect or expired
- API key doesn't have required permissions
- Organization ID doesn't match the API key
- API key format is wrong

### Solutions

#### Solution 1: Verify API Key

Check your API key format:
- Should be a long alphanumeric string (typically 40+ characters)
- No spaces or special characters at the beginning/end

**Test your API key:**
```bash
curl -X GET "https://api.meraki.com/api/v1/organizations" \
  -H "X-Cisco-Meraki-API-Key: YOUR_API_KEY"
```

If successful, you'll get a JSON list of organizations.

#### Solution 2: Regenerate API Key

1. Log in to [Meraki Dashboard](https://dashboard.meraki.com/)
2. Click your email/profile in the top right, then **My profile**
3. Scroll to **API access**
4. Click **"Generate new API key"**
5. Copy the new key immediately and update your `.env` file or vault

#### Solution 3: Verify Organization ID

- Find it in the Dashboard URL: `https://dashboard.meraki.com/o/ORG_ID/...`
- Or use the API:
  ```bash
  curl -X GET "https://api.meraki.com/api/v1/organizations" \
    -H "Authorization: Bearer YOUR_API_KEY"
  ```

#### Solution 4: Check API Key Permissions

Ensure your API key has the required permissions:
- **Read access**: To view configurations
- **Write access**: To modify configurations
- **Full access**: For all operations

Check permissions in Meraki Dashboard:
**Organization** → **Settings** → **API access** → **Permissions**

#### Solution 5: Verify Environment Variables

Check that variables are loaded correctly:

```bash
# Activate virtual environment
source venv/bin/activate

# Check if variables are set (if using .env)
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('MERAKI_API_KEY'))"
```

If using Ansible Vault:
```bash
# View encrypted file (will prompt for password)
ansible-vault view vault/secrets.yml
```

### Common Mistakes

1. **Copy-paste errors**: Extra spaces or newlines in API key
2. **Wrong org**: Using the wrong organization ID for your API key
3. **Expired keys**: Some organizations rotate API keys periodically
4. **Wrong file**: Editing `.env.example` instead of `.env`

## API Limitations

### Symptoms

```
fatal: [labnet]: FAILED! => {
    "msg": "Operation not permitted"
}
```

Or operations complete but don't persist.

### Cause

Meraki API environments may have the following restrictions depending on your API key permissions:
- **Read-only operations** — Some write operations may be restricted depending on your API key permissions
- **Rate limiting** — API calls are rate-limited (typically 5 requests per second per organization)
- **Limited networks** — Your test org may have a limited set of networks and devices

### Solutions

#### Solution 1: Use Read-Only Operations

For testing, focus on read operations:

```yaml
# Use _info modules (read-only)
- name: Get SSID information
  cisco.meraki.networks_ssids_info:
    # This should work in the target environment
```

#### Solution 2: Verify API Connectivity

Confirm your API key and org ID are working:

```bash
curl -X GET "https://api.meraki.com/api/v1/organizations/YOUR_ORG_ID/networks" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Solution 3: Check API Key Permissions

Ensure your API key has sufficient permissions for the operations you're running. Full org admin access is required for write operations.

### Common API Restrictions

- **SSID creation**: May be restricted
- **Device provisioning**: Limited device types
- **Network creation**: Not available
- **Configuration changes**: May not persist

**Workaround**: Start with read-only operations (`_info` modules) while learning, then move to write operations once you're comfortable.

## API Issues

### Symptoms

```
fatal: [labnet]: FAILED! => {
    "msg": "API endpoint not found"
}
```

Or:
```
HTTP 404 Not Found
HTTP 500 Internal Server Error
```

### Solutions

#### Solution 1: Verify API Endpoint

Check that you're using the correct API endpoint:

```yaml
# group_vars/all.yml
meraki_base_url: "https://api.meraki.com"  # Correct
# meraki_base_url: "https://dashboard.meraki.com"  # Wrong!
```

#### Solution 2: Check API Version

Ensure you're using a supported API version. The `cisco.meraki` collection uses v1 by default.

**Check API status:**
```bash
curl -X GET "https://api.meraki.com/api/v1/organizations" \
  -H "X-Cisco-Meraki-API-Key: YOUR_API_KEY" \
  -v  # Verbose output to see headers
```

#### Solution 3: Verify Network/Device IDs

Ensure IDs exist and are correct:

```yaml
# Get networks first to find correct IDs
- name: Get networks
  cisco.meraki.organizations_networks_info:
    api_key: "{{ meraki_api_key }}"
    org_id: "{{ meraki_org_id }}"
  register: networks

- name: Display network IDs
  debug:
    var: networks.data
```

#### Solution 4: Check Meraki API Status

Meraki API may be experiencing issues:
- Check [Meraki Status Page](https://status.meraki.com/)
- Check [Meraki API Status](https://developer.cisco.com/meraki/api-v1/)

### Common API Errors

| HTTP Code | Meaning | Solution |
|-----------|---------|----------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check API key permissions |
| 404 | Not Found | Verify resource IDs exist |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Check Meraki status, retry later |

## Ansible Configuration Issues

### Symptoms

```
[WARNING]: Could not match supplied host pattern
```

Or:
```
ansible: command not found
```

### Solutions

#### Solution 1: Verify Inventory File

Check that your inventory file exists and is correctly formatted:

```bash
# Check inventory syntax
ansible-inventory --list -i inventory/production.yml
```

**Common issues:**
- Wrong file path in `ansible.cfg`
- YAML syntax errors (indentation, colons)
- Host names don't match playbook `hosts:` directive

#### Solution 2: Check Ansible Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Verify Ansible is installed
ansible --version

# Should show: ansible [core 2.20.2]
```

If not installed:
```bash
pip install -r requirements.txt
```

#### Solution 3: Verify Collections

```bash
# List installed collections
ansible-galaxy collection list

# Should show: cisco.meraki
```

If missing:
```bash
ansible-galaxy collection install -r requirements.yml
```

#### Solution 4: Check ansible.cfg

Verify `ansible.cfg` settings:

```ini
[defaults]
inventory = inventory/production.yml  # Correct path?
host_key_checking = False          # Should be False for API
```

## Python and Dependency Issues

### Symptoms

```
ModuleNotFoundError: No module named 'meraki'
```

Or:
```
ERROR! couldn't resolve module/action 'cisco.meraki.networks_ssids'
```

### Solutions

#### Solution 1: Activate Virtual Environment

Always activate the virtual environment before running playbooks:

```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

#### Solution 2: Reinstall Dependencies

```bash
# Remove old virtual environment
rm -rf venv

# Run setup again
make setup

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

#### Solution 3: Check Python Version

```bash
python3 --version
# Should be Python 3.12 or higher
```

Ansible 2.20.2 requires Python 3.12+.

#### Solution 4: Verify Collection Installation

```bash
# Check collection is installed
ansible-galaxy collection list | grep meraki

# If missing, install:
ansible-galaxy collection install cisco.meraki
```

## Playbook Execution Errors

### Symptoms

```
ERROR! Syntax Error while loading YAML
```

Or:
```
fatal: [labnet]: FAILED! => {"msg": "The task includes an option with an undefined variable"}
```

### Solutions

#### Solution 1: Check YAML Syntax

```bash
# Validate playbook syntax
ansible-playbook --syntax-check playbooks/ssid_management.yml
```

**Common YAML errors:**
- Incorrect indentation (must use spaces, not tabs)
- Missing colons after keys
- Unquoted special characters

#### Solution 2: Check Variable References

Ensure all variables are defined:

```bash
# List all variables for a host
ansible-inventory --host labnet -i inventory/production.yml
```

**Common issues:**
- Variable name typos: `meraki_api_key` vs `meraki_apikey`
- Missing variable definitions in `group_vars/`
- Variables not loaded from `.env` or vault

#### Solution 3: Use Check Mode First

Test playbooks without making changes:

```bash
# Dry run (check mode)
ansible-playbook --check playbooks/ssid_management.yml
```

#### Solution 4: Validate Variable Values

Add debug tasks to check variables:

```yaml
- name: Debug variables
  debug:
    var: meraki_api_key
    # Or check if variable exists:
    # var: meraki_api_key | default('NOT SET')
```

## Debugging Tips

### Enable Verbose Output

```bash
# Level 1: Basic verbose
ansible-playbook -v playbooks/ssid_management.yml

# Level 2: More verbose
ansible-playbook -vv playbooks/ssid_management.yml

# Level 3: Very verbose (shows API calls)
ansible-playbook -vvv playbooks/ssid_management.yml
```

### Check Facts

```bash
# Gather and display facts for a host
ansible labnet -i inventory/production.yml -m setup
```

### Test Individual Tasks

Create a test playbook:

```yaml
# test.yml
---
- name: Test API connection
  hosts: meraki_orgs
  gather_facts: false
  tasks:
    - name: Get organizations
      cisco.meraki.organizations_info:
        api_key: "{{ meraki_api_key }}"
      register: orgs
    
    - name: Display organizations
      debug:
        var: orgs
```

Run it:
```bash
ansible-playbook test.yml
```

### Use Ansible Lint

Check for best practices and common mistakes:

```bash
make lint

# Or manually:
ansible-lint playbooks/ roles/
```

### Check Module Documentation

```bash
# View module documentation
ansible-doc cisco.meraki.networks_ssids

# List all Meraki modules
ansible-doc -l | grep meraki
```

### Enable API Logging

Some modules support logging. Check module documentation for `log_path` parameter.

### Common Debugging Workflow

1. **Start with syntax check**: `ansible-playbook --syntax-check`
2. **Run in check mode**: `ansible-playbook --check`
3. **Enable verbose output**: `ansible-playbook -vvv`
4. **Test individual tasks**: Create minimal test playbook
5. **Verify variables**: Use `debug` tasks to print variable values
6. **Check API directly**: Use `curl` to test API calls manually

## Getting Additional Help

If you've tried the solutions above and still have issues:

1. **Check the logs**: Run with `-vvv` and review the full output
2. **Search issues**: Check GitHub issues for similar problems
3. **Open an issue**: Include:
   - Error message (full output with `-vvv`)
   - Playbook/role that failed
   - Ansible version (`ansible --version`)
   - Python version (`python --version`)
   - Environment details
4. **Check documentation**: Review [ARCHITECTURE.md](ARCHITECTURE.md) for understanding data flow

## Prevention Checklist

Before running playbooks, verify:

- ✅ Virtual environment is activated
- ✅ API key is correct and has permissions
- ✅ Organization ID matches your account
- ✅ Inventory file exists and is correct
- ✅ Collections are installed (`ansible-galaxy collection list`)
- ✅ Python version is 3.12+
- ✅ Ansible version is 2.20.2
- ✅ Playbook syntax is valid (`--syntax-check`)
- ✅ Variables are defined (check `group_vars/`)

---

**Still stuck?** Open an issue on GitHub with the information above!
