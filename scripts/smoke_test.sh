#!/bin/bash
# Smoke test script for Meraki Wireless Ansible
# Validates playbook syntax and runs basic connectivity checks
#
# Usage: ./scripts/smoke_test.sh
# Or: make smoke-test
#
# This script performs quick validation to ensure everything is configured correctly
# Perfect for verifying setup before running full playbooks

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo ""
echo "=========================================="
echo "  Meraki Wireless Ansible Smoke Tests"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        info "Activating virtual environment..."
        source venv/bin/activate
    else
        error "Virtual environment not found. Run 'make setup' first."
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    warning ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        warning "⚠️  Please edit .env and add your Meraki API credentials before running playbooks!"
    else
        error ".env.example not found. Cannot proceed."
        exit 1
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    set -a  # Automatically export all variables
    source .env
    set +a
fi

# Check if API key is set
if [ -z "$MERAKI_DASHBOARD_API_KEY" ] || [ "$MERAKI_DASHBOARD_API_KEY" = "your_meraki_dashboard_api_key_here" ]; then
    warning "MERAKI_DASHBOARD_API_KEY not configured in .env"
    warning "Smoke tests will check syntax only (no API calls)"
    SKIP_API_TESTS=true
else
    info "API key found. Will run full validation tests."
    SKIP_API_TESTS=false
fi

# Test 1: Check Ansible installation
info "Test 1: Verifying Ansible installation..."
if command -v ansible-playbook &> /dev/null; then
    ANSIBLE_VERSION=$(ansible-playbook --version | head -n 1)
    success "Ansible installed: $ANSIBLE_VERSION"
else
    error "ansible-playbook not found!"
    exit 1
fi

# Test 2: Check Ansible Lint installation
info "Test 2: Verifying ansible-lint installation..."
if command -v ansible-lint &> /dev/null; then
    LINT_VERSION=$(ansible-lint --version | head -n 1)
    success "ansible-lint installed: $LINT_VERSION"
else
    error "ansible-lint not found!"
    exit 1
fi

# Test 3: Syntax check on all playbooks
info "Test 3: Checking playbook syntax..."
PLAYBOOKS=(
    "playbooks/ssid_management.yml"
    "playbooks/bulk_ap_deploy.yml"
    "playbooks/compliance_check.yml"
)

SYNTAX_ERRORS=0
for playbook in "${PLAYBOOKS[@]}"; do
    if [ -f "$playbook" ]; then
        if ansible-playbook --syntax-check "$playbook" > /dev/null 2>&1; then
            success "Syntax OK: $playbook"
        else
            error "Syntax error in: $playbook"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        fi
    else
        warning "Playbook not found: $playbook (skipping)"
    fi
done

if [ $SYNTAX_ERRORS -gt 0 ]; then
    error "Found $SYNTAX_ERRORS syntax error(s). Please fix before proceeding."
    exit 1
fi

# Test 4: Run ansible-lint
info "Test 4: Running ansible-lint..."
if ansible-lint playbooks/ roles/ > /dev/null 2>&1; then
    success "ansible-lint passed!"
else
    warning "ansible-lint found issues (non-blocking)"
    # Show linting output
    ansible-lint playbooks/ roles/ || true
fi

# Test 5: Validate inventory file
info "Test 5: Validating inventory file..."
if [ -f "inventory/sandbox.yml" ]; then
    if ansible-inventory --list -i inventory/sandbox.yml > /dev/null 2>&1; then
        success "Inventory file is valid"
    else
        error "Inventory file has errors"
        exit 1
    fi
else
    warning "Inventory file not found: inventory/sandbox.yml"
fi

# Test 6: API connectivity test (if API key is configured)
if [ "$SKIP_API_TESTS" = false ]; then
    info "Test 6: Testing Meraki API connectivity..."
    
    # Try to list organizations (read-only operation, safe for testing)
    if python3 -c "
import os
import sys
try:
    from meraki import DashboardAPI
    api_key = os.getenv('MERAKI_DASHBOARD_API_KEY')
    if not api_key or api_key == 'your_meraki_dashboard_api_key_here':
        sys.exit(1)
    dashboard = DashboardAPI(api_key, suppress_logging=True)
    orgs = dashboard.organizations.getOrganizations()
    print('API connection successful')
    sys.exit(0)
except Exception as e:
    print(f'API connection failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        success "Meraki API connection successful!"
    else
        warning "Meraki API connection test failed (check your API key)"
        warning "Check your API key and organization ID in .env"
    fi
else
    info "Test 6: Skipping API connectivity test (no API key configured)"
fi

# Summary
echo ""
success "Smoke tests completed! 🎉"
echo ""
if [ "$SKIP_API_TESTS" = true ]; then
    warning "Note: API tests were skipped. Configure MERAKI_DASHBOARD_API_KEY in .env to enable full testing."
fi
echo "All basic checks passed. You're ready to run playbooks!"
echo ""
