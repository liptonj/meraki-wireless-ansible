# Meraki Wireless Ansible - Makefile
# Provides common development and deployment tasks
# Beginner-friendly targets for YouTube tutorial viewers

.PHONY: help setup lint test smoke-test clean

# Default target - show help
help:
	@echo "Meraki Wireless Ansible - Available Commands:"
	@echo ""
	@echo "  make setup      - Create Python virtual environment and install all dependencies"
	@echo "  make lint       - Run ansible-lint on playbooks and roles"
	@echo "  make test       - Run Ansible syntax checks on all playbooks"
	@echo "  make smoke-test - Run validation tests against DevNet sandbox"
	@echo "  make clean      - Remove Python cache files and virtual environment"
	@echo ""

# Setup: Create venv, install Python deps, install Ansible collections
# This is the one-command setup for beginners
setup:
	@echo "🚀 Setting up Meraki Wireless Ansible project..."
	@echo ""
	@if [ ! -d "venv" ]; then \
		echo "📦 Creating Python virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "📥 Activating virtual environment and installing dependencies..."
	@. venv/bin/activate && pip install --upgrade pip setuptools wheel
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "📚 Installing Ansible collections..."
	@. venv/bin/activate && ansible-galaxy collection install -r requirements.yml
	@echo ""
	@echo "✅ Setup complete! Activate the virtual environment with:"
	@echo "   source venv/bin/activate"
	@echo ""
	@echo "📝 Don't forget to copy .env.example to .env and add your API key!"

# Lint: Run ansible-lint on playbooks and roles
# Checks for best practices and common mistakes
lint:
	@echo "🔍 Running ansible-lint..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && ansible-lint playbooks/ roles/; \
	else \
		echo "⚠️  Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Test: Run syntax checks on all playbooks
# Validates YAML syntax without executing playbooks
test:
	@echo "🧪 Running Ansible syntax checks..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		ansible-playbook --syntax-check playbooks/ssid_management.yml && \
		ansible-playbook --syntax-check playbooks/bulk_ap_deploy.yml && \
		ansible-playbook --syntax-check playbooks/compliance_check.yml; \
	else \
		echo "⚠️  Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "✅ All syntax checks passed!"

# Smoke-test: Run validation against DevNet sandbox
# Quick validation that everything works end-to-end
smoke-test:
	@echo "💨 Running smoke tests against DevNet sandbox..."
	@if [ -d "venv" ]; then \
		. venv/bin/activate && ./scripts/smoke_test.sh; \
	else \
		echo "⚠️  Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Clean: Remove Python cache files and virtual environment
# Use this to start fresh or free up disk space
clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@if [ -d "venv" ]; then \
		echo "🗑️  Removing virtual environment..."; \
		rm -rf venv; \
	fi
	@echo "✅ Cleanup complete!"
