#!/bin/bash
# Setup script for Meraki Wireless Ansible project
#
# Usage: ./scripts/setup.sh or make setup

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error()   { echo -e "${RED}❌ $1${NC}"; }

echo ""
echo "=========================================="
echo "  Meraki Wireless Ansible Setup"
echo "=========================================="
echo ""

info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install Python 3.12 or newer."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
info "Found: $PYTHON_VERSION"

PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    error "Python 3.12 or newer is required. Found: $PYTHON_VERSION"
    exit 1
fi

if [ ! -d "venv" ]; then
    info "Creating Python virtual environment..."
    python3 -m venv venv
    success "Virtual environment created!"
else
    warning "Virtual environment already exists. Skipping creation."
fi

info "Activating virtual environment..."
source venv/bin/activate

info "Upgrading pip..."
pip install --quiet --upgrade pip
success "pip upgraded!"

info "Installing Python dependencies from requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    error "requirements.txt not found! Are you in the project root?"
    exit 1
fi

pip install --quiet -r requirements.txt
success "Python dependencies installed!"

info "Installing Ansible collections from requirements.yml..."
if [ ! -f "requirements.yml" ]; then
    error "requirements.yml not found! Are you in the project root?"
    exit 1
fi

ansible-galaxy collection install --force -r requirements.yml
success "Ansible collections installed!"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        info "Creating .env file from .env.example..."
        cp .env.example .env
        warning "IMPORTANT: Please edit .env and add your Meraki API credentials!"
        warning "Get your API key from: https://dashboard.meraki.com/ -> My Profile -> API access"
    fi
else
    info ".env file already exists. Skipping creation."
fi

echo ""
info "Verifying installation..."
ANSIBLE_VERSION=$(ansible --version | head -n 1)
ANSIBLE_LINT_VERSION=$(ansible-lint --version | head -n 1)

echo ""
success "Setup complete!"
echo ""
echo "Installed versions:"
echo "  $ANSIBLE_VERSION"
echo "  $ANSIBLE_LINT_VERSION"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     ${GREEN}source venv/bin/activate${NC}"
echo ""
echo "  2. Configure your API credentials:"
echo "     ${GREEN}cp .env.example .env${NC}"
echo "     ${GREEN}# Edit .env and add your MERAKI_DASHBOARD_API_KEY${NC}"
echo ""
echo "  3. Run a smoke test:"
echo "     ${GREEN}make smoke-test${NC}"
echo ""
echo "  4. Check available commands:"
echo "     ${GREEN}make help${NC}"
echo ""
