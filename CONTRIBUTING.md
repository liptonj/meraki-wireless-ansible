# Contributing to Meraki Wireless Ansible

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing Your Changes](#testing-your-changes)
6. [Code Style Guidelines](#code-style-guidelines)
7. [Submitting Pull Requests](#submitting-pull-requests)
8. [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

There are many ways to contribute:

- 🐛 **Report bugs** - Help us identify issues
- 💡 **Suggest features** - Share your ideas
- 📝 **Improve documentation** - Make docs clearer
- 🔧 **Fix bugs** - Submit pull requests
- ✨ **Add features** - Extend functionality
- 🧪 **Write tests** - Improve test coverage
- 🔍 **Review code** - Help improve pull requests

## Development Setup

### 1. Fork the Repository

1. Click the "Fork" button on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/meraki-wireless-ansible.git
   cd meraki-wireless-ansible
   ```

### 2. Set Up Development Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install -r requirements.yml

# Install development tools
pip install ansible-lint pre-commit
```

### 3. Configure Pre-commit Hooks (Optional but Recommended)

```bash
pre-commit install
```

This will automatically run linting and checks before each commit.

### 4. Set Up Your Environment

```bash
# Copy example files
cp .env.example .env
cp vault/secrets.yml.example vault/secrets.yml

# Edit .env with your Meraki API credentials
# (See GETTING_STARTED.md for details)
```

## Making Changes

### Workflow

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**:
   - Write code following our style guidelines
   - Update documentation if needed
   - Add tests if applicable

3. **Test your changes**:
   ```bash
   make lint      # Check code quality
   make test      # Validate syntax
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

### Branch Naming

Use descriptive branch names:

- `feature/add-new-role` - New features
- `fix/rate-limit-handling` - Bug fixes
- `docs/update-getting-started` - Documentation updates
- `refactor/simplify-playbook` - Code refactoring

## Testing Your Changes

### Before Submitting

Always test your changes:

```bash
# 1. Run linting
make lint

# 2. Check syntax
make test

# 3. Test against your environment (if applicable)
ansible-playbook --check playbooks/your_playbook.yml

# 4. Run with verbose output to verify
ansible-playbook -vv playbooks/your_playbook.yml
```

### Testing Checklist

- [ ] Code follows style guidelines
- [ ] All playbooks pass syntax check
- [ ] Linting passes without errors
- [ ] Changes work in target environment
- [ ] Documentation is updated
- [ ] No secrets or API keys committed

## Code Style Guidelines

### Ansible Best Practices

1. **Use meaningful names**:
   ```yaml
   # Good
   - name: Create guest SSID
   
   # Bad
   - name: Do stuff
   ```

2. **Include comments for complex logic**:
   ```yaml
   - name: Update SSID configuration
     # Only update if SSID doesn't match desired state
     cisco.meraki.networks_ssids:
       # ... parameters
   ```

3. **Use variables instead of hardcoding**:
   ```yaml
   # Good
   api_key: "{{ meraki_api_key }}"
   
   # Bad
   api_key: "hardcoded_key_value"
   ```

4. **Keep tasks focused**:
   ```yaml
   # Good - one task, one purpose
   - name: Get networks
     cisco.meraki.organizations_networks_info:
       # ...
   
   # Bad - multiple purposes in one task
   - name: Get networks and update SSIDs
     # ...
   ```

5. **Use handlers for notifications**:
   ```yaml
   # In tasks
   - name: Update SSID
     notify: restart_wireless
   
   # In handlers
   handlers:
     - name: restart_wireless
       # ...
   ```

### YAML Style

- Use 2 spaces for indentation (never tabs)
- Use quotes for strings with special characters
- Keep line length under 120 characters
- Use `---` at the start of YAML files

### Python Style (if adding scripts)

- Follow PEP 8
- Use type hints where applicable
- Include docstrings for functions
- Keep functions focused and small

### File Organization

- **Playbooks**: `playbooks/` directory
- **Roles**: `roles/` directory (one role per directory)
- **Inventory**: `inventory/` directory
- **Variables**: `group_vars/` directory
- **Scripts**: `scripts/` directory
- **Documentation**: `docs/` directory

## Submitting Pull Requests

### PR Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main
- [ ] No merge conflicts

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?
- [ ] Tested in target environment
- [ ] Tested in production (if applicable)
- [ ] Added new tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Documentation updated
- [ ] No new warnings
```

### Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add retry logic for rate-limited API calls"
git commit -m "Fix authentication error handling in meraki_ssid role"
git commit -m "Update getting started guide"

# Bad
git commit -m "fix stuff"
git commit -m "updates"
git commit -m "WIP"
```

**Format:**
- Use imperative mood ("Add" not "Added")
- Keep first line under 50 characters
- Add detailed description if needed (after blank line)
- Reference issues: "Fixes #123"

### Review Process

1. **Automated Checks**: GitHub Actions will run linting and tests
2. **Code Review**: Maintainers will review your PR
3. **Feedback**: Address any requested changes
4. **Merge**: Once approved, your PR will be merged

### What to Expect

- **Response Time**: We aim to review PRs within 48 hours
- **Feedback**: We'll provide constructive feedback
- **Questions**: Don't hesitate to ask if something is unclear
- **Iteration**: It's normal to have a few rounds of feedback

## Reporting Issues

### Before Reporting

1. Check if the issue already exists
2. Verify you're using the latest version
3. Try to reproduce the issue
4. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

### Issue Template

```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. Run command: `ansible-playbook playbooks/...`
2. See error: `...`

## Expected Behavior
What should happen

## Actual Behavior
What actually happened

## Environment
- Ansible version: `ansible --version`
- Python version: `python --version`
- OS: macOS/Linux/Windows
- Environment name

## Logs
Include relevant logs (use `-vvv` for verbose output)
```

### Bug Reports

Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Relevant logs/output

### Feature Requests

Include:
- Use case (why is this needed?)
- Proposed solution
- Alternatives considered
- Impact on existing code

## Code Style Examples

### Good Playbook Structure

```yaml
---
- name: Descriptive playbook name
  hosts: meraki_orgs
  gather_facts: false
  become: false
  
  vars:
    # Playbook-specific variables
    ssid_name: "Guest Network"
  
  roles:
    - meraki_ssid
```

### Good Role Structure

```yaml
# roles/meraki_ssid/tasks/main.yml
---
- name: Get current SSID configuration
  cisco.meraki.networks_ssids_info:
    api_key: "{{ meraki_api_key }}"
    org_id: "{{ meraki_org_id }}"
    network_id: "{{ network_id }}"
  register: current_ssids

- name: Update SSID if needed
  cisco.meraki.networks_ssids:
    api_key: "{{ meraki_api_key }}"
    network_id: "{{ network_id }}"
    number: "{{ item.number }}"
    name: "{{ item.name }}"
    enabled: "{{ item.enabled }}"
  loop: "{{ ssid_configurations }}"
  when: item.name not in current_ssids.data | map(attribute='name') | list
```

### Good Variable Usage

```yaml
# group_vars/all.yml
# Global defaults
meraki_base_url: "https://api.meraki.com"
meraki_api_timeout: 30

# group_vars/meraki_orgs.yml
# SSID deployment config for meraki_orgs group
meraki_environment: production
meraki_api_timeout: 60
```

## Documentation Contributions

Documentation improvements are always welcome!

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots when helpful
- Keep formatting consistent
- Link between related docs

### Where to Document

- **README.md**: Project overview, quick start
- **docs/GETTING_STARTED.md**: Detailed setup instructions
- **docs/ARCHITECTURE.md**: Technical architecture
- **docs/TROUBLESHOOTING.md**: Common issues and solutions
- **Inline comments**: Explain complex logic in code

## Getting Help

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions for questions
- **Pull Requests**: Ask questions in PR comments

## Recognition

Contributors will be:
- Listed in the README (if desired)
- Credited in release notes
- Appreciated by the community! 🙏

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** Your efforts make this project better for everyone. 🎉
