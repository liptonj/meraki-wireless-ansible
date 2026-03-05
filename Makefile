.PHONY: help setup lint test smoke-test clean deploy-ssid-check compliance-check test-all

help:
	@echo "Meraki Wireless Ansible - Available Commands:"
	@echo ""
	@echo "  make setup      - Create Python virtual environment and install all dependencies"
	@echo "  make lint       - Run ansible-lint on playbooks and roles"
	@echo "  make test       - Run Ansible syntax checks on all playbooks"
	@echo "  make smoke-test - Run validation tests against target environment"
	@echo "  make clean      - Remove Python cache files and virtual environment"
	@echo ""

setup:
	@echo "Setting up Meraki Wireless Ansible project..."
	@echo ""
	@if [ ! -d "venv" ]; then \
		echo "Creating Python virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Installing dependencies..."
	@. venv/bin/activate && pip install --upgrade pip setuptools wheel
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "Installing Ansible collections..."
	@. venv/bin/activate && ansible-galaxy collection install -r requirements.yml
	@echo ""
	@echo "Setup complete! Activate the virtual environment with:"
	@echo "   source venv/bin/activate"
	@echo ""
	@echo "Don't forget to copy .env.example to .env and add your API key!"

lint:
	@echo "Running ansible-lint..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && ansible-lint playbooks/ roles/; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

test:
	@echo "Running Ansible syntax checks..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		ansible-playbook --syntax-check playbooks/ssid_management.yml && \
		ansible-playbook --syntax-check playbooks/compliance_check.yml && \
		ansible-playbook --syntax-check playbooks/config_snapshot.yml; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "All syntax checks passed!"

smoke-test:
	@echo "Running smoke tests..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && ./scripts/smoke_test.sh; \
	else \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

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

deploy-ssid-check:
	ansible-playbook --syntax-check playbooks/ssid_management.yml

compliance-check:
	ansible-playbook --syntax-check playbooks/compliance_check.yml

test-all:
	@echo "Checking all playbooks..."
	@for playbook in playbooks/*.yml; do \
		echo "Checking: $$playbook"; \
		ansible-playbook --syntax-check "$$playbook" || exit 1; \
	done
	@echo "All playbooks passed syntax check"
