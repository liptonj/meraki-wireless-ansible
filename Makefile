PYTHON          := venv/bin/python3
ANSIBLE         := venv/bin/ansible-playbook
ANSIBLE_LINT    := venv/bin/ansible-lint
ANSIBLE_VAULT   := venv/bin/ansible-vault
ANSIBLE_GALAXY  := venv/bin/ansible-galaxy
PIP             := venv/bin/pip
VAULT_PASS_FILE := .vault_pass

.PHONY: help setup lint test test-templates smoke-test clean deploy-ssid-check compliance-check test-all vault-encrypt vault-decrypt vault-view webhook-server webhook-public test-ssid-cleanup remove-ssid remove-ssid-check remove-ssid-menu

help:
	@echo "Meraki Wireless Ansible - Available Commands:"
	@echo ""
	@echo "  make setup         - Create Python venv and install all dependencies"
	@echo "  make lint          - Run ansible-lint on playbooks and roles"
	@echo "  make test          - Run syntax checks and Jinja2 template validation"
	@echo "  make test-templates - Validate Jinja2 template syntax"
	@echo "  make test-ssid-cleanup - Test SSID configuration cleanup script"
	@echo "  make smoke-test    - Run validation tests against target environment"
	@echo "  make clean         - Remove Python cache files and virtual environment"
	@echo "  make vault-encrypt - Encrypt vault/secrets.yml"
	@echo "  make vault-decrypt - Decrypt vault/secrets.yml (edit in place)"
	@echo "  make vault-view    - View vault/secrets.yml contents"
	@echo "  make webhook-server - Start local Meraki webhook receiver"
	@echo "  make webhook-public - Start webhook receiver with public Cloudflare tunnel"
	@echo ""
	@echo "SSID Management:"
	@echo "  make remove-ssid-menu  - Interactive menu (queries Meraki API for options)"
	@echo "  make remove-ssid       - Remove SSID with manual input prompts"
	@echo "  make remove-ssid-check - Preview SSID removal without making changes"
	@echo ""

setup:
	@echo "Setting up Meraki Wireless Ansible project..."
	@echo ""
	@if [ ! -d "venv" ]; then \
		echo "Creating Python virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip
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
		$(ANSIBLE) --syntax-check -i inventory/production.yml "$$playbook" || exit 1; \
	done
	@$(PYTHON) scripts/validate_jinja_templates.py
	@echo "All syntax checks passed!"

test-templates:
	@$(PYTHON) scripts/validate_jinja_templates.py

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
	@$(ANSIBLE) --syntax-check -i inventory/production.yml playbooks/ssid_management.yml

compliance-check:
	@$(ANSIBLE) --syntax-check -i inventory/production.yml playbooks/compliance_check.yml

webhook-server:
	@if [ ! -f "$(PYTHON)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@$(PYTHON) scripts/webhook_receiver.py

webhook-public:
	@if [ ! -f "$(PYTHON)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@if ! command -v cloudflared >/dev/null 2>&1; then \
		echo "ERROR: cloudflared not found. Install with: brew install cloudflared"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/webhook_receiver.py & \
	SERVER_PID=$$!; \
	sleep 1; \
	echo ""; \
	echo "Starting Cloudflare Tunnel → http://localhost:5005 ..."; \
	echo "Copy the https://*.trycloudflare.com URL below and add /webhooks"; \
	echo "Paste that into Meraki Dashboard → Alerts → Webhooks → Server URL"; \
	echo ""; \
	cloudflared tunnel --url http://localhost:5005 || true; \
	kill $$SERVER_PID 2>/dev/null

test-all:
	@echo "Checking all playbooks..."
	@for playbook in playbooks/*.yml; do \
		echo "Checking: $$playbook"; \
		$(ANSIBLE) --syntax-check -i inventory/production.yml "$$playbook" || exit 1; \
	done
	@echo "All playbooks passed syntax check"

test-ssid-cleanup:
	@echo "Testing SSID configuration cleanup script..."
	@if [ ! -f "$(PYTHON)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@echo "Running in check mode (no actual changes)..."
	@$(PYTHON) scripts/cleanup_ssid_config.py \
		--ssid-name "Corp-Guest" \
		--network-name "LAB-Site1" \
		--network-id "L_3664241246819323813" \
		--orgs-config "group_vars/meraki_orgs.yml" \
		--networks-config "group_vars/meraki_networks.yml" \
		--baseline-path "baselines/L_3664241246819323813/ssids.yml" \
		--check-mode
	@echo ""
	@echo "Cleanup script test completed successfully!"

remove-ssid:
	@if [ ! -f "$(ANSIBLE)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  SSID Removal Tool"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "This will remove an SSID from Meraki networks and clean up"
	@echo "all configuration files (deployment config, compliance state,"
	@echo "and baseline snapshots)."
	@echo ""
	@read -p "Enter SSID name to remove: " ssid_name; \
	if [ -z "$$ssid_name" ]; then \
		echo "ERROR: SSID name is required."; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Target Networks:"; \
	echo "  [1] All networks (uses MERAKI_NETWORK_NAMES from .env)"; \
	echo "  [2] Specific network(s) (override)"; \
	echo ""; \
	read -p "Choose option [1-2]: " option; \
	if [ "$$option" = "2" ]; then \
		echo ""; \
		read -p "Enter network name(s) (comma-separated): " network_names; \
		if [ -z "$$network_names" ]; then \
			echo "ERROR: Network name is required when option 2 is selected."; \
			exit 1; \
		fi; \
		echo ""; \
		echo "═══════════════════════════════════════════════════════════"; \
		echo "  Execution Plan"; \
		echo "═══════════════════════════════════════════════════════════"; \
		echo "  SSID to remove : $$ssid_name"; \
		echo "  Target networks: $$network_names"; \
		echo "  Actions        : Remove from Meraki + Cleanup config files"; \
		echo "═══════════════════════════════════════════════════════════"; \
		echo ""; \
		read -p "Proceed with removal? [y/N]: " confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Cancelled."; \
			exit 0; \
		fi; \
		echo ""; \
		echo "Removing SSID '$$ssid_name' from networks: $$network_names"; \
		MERAKI_NETWORK_NAMES="$$network_names" $(ANSIBLE) playbooks/remove_ssid.yml \
			-i inventory/production.yml \
			-e "meraki_remove_ssid_name=$$ssid_name"; \
	else \
		echo ""; \
		echo "═══════════════════════════════════════════════════════════"; \
		echo "  Execution Plan"; \
		echo "═══════════════════════════════════════════════════════════"; \
		echo "  SSID to remove : $$ssid_name"; \
		echo "  Target networks: All networks from MERAKI_NETWORK_NAMES"; \
		echo "  Actions        : Remove from Meraki + Cleanup config files"; \
		echo "═══════════════════════════════════════════════════════════"; \
		echo ""; \
		read -p "Proceed with removal? [y/N]: " confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Cancelled."; \
			exit 0; \
		fi; \
		echo ""; \
		echo "Removing SSID '$$ssid_name' from all networks"; \
		$(ANSIBLE) playbooks/remove_ssid.yml \
			-i inventory/production.yml \
			-e "meraki_remove_ssid_name=$$ssid_name"; \
	fi

remove-ssid-check:
	@if [ ! -f "$(ANSIBLE)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@echo ""
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  SSID Removal Preview (Check Mode)"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "This will preview what would be removed WITHOUT making any"
	@echo "actual changes to Meraki or configuration files."
	@echo ""
	@read -p "Enter SSID name to preview: " ssid_name; \
	if [ -z "$$ssid_name" ]; then \
		echo "ERROR: SSID name is required."; \
		exit 1; \
	fi; \
	echo ""; \
	echo "Target Networks:"; \
	echo "  [1] All networks (uses MERAKI_NETWORK_NAMES from .env)"; \
	echo "  [2] Specific network(s) (override)"; \
	echo ""; \
	read -p "Choose option [1-2]: " option; \
	if [ "$$option" = "2" ]; then \
		echo ""; \
		read -p "Enter network name(s) (comma-separated): " network_names; \
		if [ -z "$$network_names" ]; then \
			echo "ERROR: Network name is required when option 2 is selected."; \
			exit 1; \
		fi; \
		echo ""; \
		echo "Previewing removal of SSID '$$ssid_name' from networks: $$network_names"; \
		echo ""; \
		MERAKI_NETWORK_NAMES="$$network_names" $(ANSIBLE) playbooks/remove_ssid.yml \
			-i inventory/production.yml \
			-e "meraki_remove_ssid_name=$$ssid_name" \
			--check; \
	else \
		echo ""; \
		echo "Previewing removal of SSID '$$ssid_name' from all networks"; \
		echo ""; \
		$(ANSIBLE) playbooks/remove_ssid.yml \
			-i inventory/production.yml \
			-e "meraki_remove_ssid_name=$$ssid_name" \
			--check; \
	fi

remove-ssid-menu:
	@if [ ! -f "$(ANSIBLE)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@if [ ! -f "$(PYTHON)" ]; then echo "Run 'make setup' first."; exit 1; fi
	@echo ""
	@output=$$($(PYTHON) scripts/interactive_ssid_menu.py 2>&1); \
	exit_code=$$?; \
	if [ $$exit_code -ne 0 ]; then \
		echo "$$output"; \
		exit $$exit_code; \
	fi; \
	result=$$(echo "$$output" | grep -A 1 "__RESULT_JSON__" | tail -1); \
	if [ -z "$$result" ]; then \
		echo "ERROR: Failed to parse menu selection"; \
		exit 1; \
	fi; \
	ssid_name=$$(echo "$$result" | $(PYTHON) -c "import sys, json; data=json.load(sys.stdin); print(data['ssid_name'])"); \
	network_name=$$(echo "$$result" | $(PYTHON) -c "import sys, json; data=json.load(sys.stdin); print(data.get('network_name') or '')"); \
	echo ""; \
	echo "═══════════════════════════════════════════════════════════"; \
	echo "  Execution Plan"; \
	echo "═══════════════════════════════════════════════════════════"; \
	echo "  SSID to remove : $$ssid_name"; \
	if [ -n "$$network_name" ]; then \
		echo "  Target network : $$network_name"; \
	else \
		echo "  Target networks: All networks from MERAKI_NETWORK_NAMES"; \
	fi; \
	echo "  Actions        : Remove from Meraki (if exists) + Cleanup config files"; \
	echo "═══════════════════════════════════════════════════════════"; \
	echo ""; \
	echo "NOTE: Config files will be cleaned up even if SSID is not found in Meraki."; \
	echo ""; \
	read -p "Proceed with removal? [y/N]: " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "Cancelled."; \
		exit 0; \
	fi; \
	echo ""; \
	if [ -n "$$network_name" ]; then \
		echo "Removing SSID '$$ssid_name' from network: $$network_name"; \
		MERAKI_NETWORK_NAMES="$$network_name" $(ANSIBLE) playbooks/remove_ssid.yml \
			-i inventory/production.yml \
			-e "meraki_remove_ssid_name=$$ssid_name"; \
	else \
		echo "Removing SSID '$$ssid_name' from all networks"; \
		$(ANSIBLE) playbooks/remove_ssid.yml \
			-i inventory/production.yml \
			-e "meraki_remove_ssid_name=$$ssid_name"; \
	fi
