PYTHON          := venv/bin/python3
ANSIBLE         := venv/bin/ansible-playbook
ANSIBLE_LINT    := venv/bin/ansible-lint
ANSIBLE_VAULT   := venv/bin/ansible-vault
ANSIBLE_GALAXY  := venv/bin/ansible-galaxy
PIP             := venv/bin/pip
VAULT_PASS_FILE := .vault_pass

.PHONY: help setup lint test smoke-test clean deploy-ssid-check compliance-check test-all vault-encrypt vault-decrypt vault-view

help:
	@echo "Meraki Wireless Ansible - Available Commands:"
	@echo ""
	@echo "  make setup         - Create Python venv and install all dependencies"
	@echo "  make lint          - Run ansible-lint on playbooks and roles"
	@echo "  make test          - Run Ansible syntax checks on all playbooks"
	@echo "  make smoke-test    - Run validation tests against target environment"
	@echo "  make clean         - Remove Python cache files and virtual environment"
	@echo "  make vault-encrypt - Encrypt vault/secrets.yml"
	@echo "  make vault-decrypt - Decrypt vault/secrets.yml (edit in place)"
	@echo "  make vault-view    - View vault/secrets.yml contents"
	@echo ""

setup:
	@echo "Setting up Meraki Wireless Ansible project..."
	@echo ""
	@if [ ! -d "venv" ]; then \
		echo "Creating Python virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -r requirements.txt
	@echo "Installing Ansible collections..."
	@$(ANSIBLE_GALAXY) collection install -r requirements.yml
	@echo ""
	@echo "Setup complete!"
	@echo ""
	@echo "  Activate manually : source venv/bin/activate"
	@echo "  Auto-activate     : brew install direnv && direnv allow"
	@echo ""
	@echo "Don't forget:"
	@echo "  cp .env.example .env  and fill in MERAKI_DASHBOARD_API_KEY"
	@echo "  cp vault/secrets.yml.example vault/secrets.yml  then  make vault-encrypt"

lint:
	@echo "Running ansible-lint..."
	@if [ ! -f "$(ANSIBLE_LINT)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@$(ANSIBLE_LINT) playbooks/ roles/

test:
	@echo "Running Ansible syntax checks..."
	@if [ ! -f "$(ANSIBLE)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@for playbook in playbooks/*.yml; do \
		echo "Checking: $$playbook"; \
		$(ANSIBLE) --syntax-check "$$playbook" || exit 1; \
	done
	@echo "All syntax checks passed!"

smoke-test:
	@echo "Running smoke tests..."
	@if [ ! -f "$(ANSIBLE)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@./scripts/smoke_test.sh

clean:
	@echo "Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@if [ -d "venv" ]; then \
		echo "Removing virtual environment..."; \
		rm -rf venv; \
	fi
	@echo "Cleanup complete!"

vault-encrypt:
	@if [ ! -f "$(VAULT_PASS_FILE)" ]; then \
		echo "ERROR: $(VAULT_PASS_FILE) not found."; \
		echo "Generate one: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\" > $(VAULT_PASS_FILE)"; \
		exit 1; \
	fi
	@if [ ! -f "vault/secrets.yml" ]; then \
		echo "ERROR: vault/secrets.yml not found."; \
		echo "Copy the example: cp vault/secrets.yml.example vault/secrets.yml"; \
		exit 1; \
	fi
	@$(ANSIBLE_VAULT) encrypt vault/secrets.yml --vault-password-file $(VAULT_PASS_FILE)
	@echo "vault/secrets.yml encrypted. Safe to commit."

vault-decrypt:
	@if [ ! -f "$(VAULT_PASS_FILE)" ]; then echo "ERROR: $(VAULT_PASS_FILE) not found."; exit 1; fi
	@$(ANSIBLE_VAULT) edit vault/secrets.yml --vault-password-file $(VAULT_PASS_FILE)

vault-view:
	@if [ ! -f "$(VAULT_PASS_FILE)" ]; then echo "ERROR: $(VAULT_PASS_FILE) not found."; exit 1; fi
	@$(ANSIBLE_VAULT) view vault/secrets.yml --vault-password-file $(VAULT_PASS_FILE)

deploy-ssid-check:
	@$(ANSIBLE) --syntax-check playbooks/ssid_management.yml

compliance-check:
	@$(ANSIBLE) --syntax-check playbooks/compliance_check.yml

test-all:
	@echo "Checking all playbooks..."
	@for playbook in playbooks/*.yml; do \
		echo "Checking: $$playbook"; \
		$(ANSIBLE) --syntax-check "$$playbook" || exit 1; \
	done
	@echo "All playbooks passed syntax check"
