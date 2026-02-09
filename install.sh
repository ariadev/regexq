#!/usr/bin/env bash

# RegexQ Installer
# Installs regexq.py to the system

set -e

SCRIPT_NAME="regexq"
REPO_URL="https://github.com/astroteam-ir/regexq.git"
VERSION="2.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.10 or higher."
        exit 1
    fi

    # Check Python version
    py_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    py_major=$(echo "$py_version" | cut -d. -f1)
    py_minor=$(echo "$py_version" | cut -d. -f2)

    if [ "$py_major" -lt 3 ] || ([ "$py_major" -eq 3 ] && [ "$py_minor" -lt 10 ]); then
        print_error "Python 3.10 or higher is required. You have Python $py_version."
        exit 1
    fi

    print_success "Python $py_version found"
}

# Determine installation directory
get_install_dir() {
    # Try to find a suitable directory in PATH
    if [ -w "/usr/local/bin" ]; then
        echo "/usr/local/bin"
    elif [ -w "$HOME/.local/bin" ]; then
        echo "$HOME/.local/bin"
    elif [ -w "$HOME/bin" ]; then
        echo "$HOME/bin"
    else
        echo "$HOME/.local/bin"
    fi
}

# Install regexq
install_regexq() {
    local source_file="$1"
    local install_dir="$2"
    local target_file="$install_dir/$SCRIPT_NAME"

    # Create install directory if it doesn't exist
    if [ ! -d "$install_dir" ]; then
        print_info "Creating directory: $install_dir"
        mkdir -p "$install_dir"
    fi

    # Copy the script
    print_info "Installing $SCRIPT_NAME to $install_dir"
    cp "$source_file" "$target_file"
    chmod +x "$target_file"

    print_success "Installed to $target_file"
}

# Check if directory is in PATH
check_path() {
    local dir="$1"
    if [[ ":$PATH:" != *":$dir:"* ]]; then
        print_warning "$dir is not in your PATH"
        print_info "Add this line to your ~/.bashrc or ~/.zshrc:"
        echo ""
        echo "    export PATH=\"$dir:\$PATH\""
        echo ""
        return 1
    fi
    return 0
}

# Main installation
main() {
    echo ""
    echo "╔═══════════════════════════════════════════╗"
    echo "║      RegexQ Installer v$VERSION         ║"
    echo "╚═══════════════════════════════════════════╝"
    echo ""

    # Check for Python
    check_python

    # Determine source file location
    if [ -f "regexq.py" ]; then
        SOURCE_FILE="$(pwd)/regexq.py"
    elif [ -f "$(dirname "$0")/regexq.py" ]; then
        SOURCE_FILE="$(dirname "$0")/regexq.py"
    else
        print_error "regexq.py not found in current directory"
        print_info "Please run this script from the regexq repository directory"
        exit 1
    fi

    print_info "Found regexq.py at: $SOURCE_FILE"

    # Determine installation directory
    INSTALL_DIR=$(get_install_dir)

    # Ask for custom installation directory
    echo ""
    print_info "Default installation directory: $INSTALL_DIR"
    read -p "Press Enter to continue or specify a different directory: " custom_dir

    if [ -n "$custom_dir" ]; then
        INSTALL_DIR="$custom_dir"
    fi

    # Check if already installed
    if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
        print_warning "$SCRIPT_NAME is already installed at $INSTALL_DIR/$SCRIPT_NAME"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled"
            exit 0
        fi
    fi

    # Install
    install_regexq "$SOURCE_FILE" "$INSTALL_DIR"

    # Check PATH
    echo ""
    if check_path "$INSTALL_DIR"; then
        print_success "$SCRIPT_NAME is ready to use!"
        echo ""
        print_info "Try it out:"
        echo "    $SCRIPT_NAME start literal 'Hello' space word end"
    else
        print_info "After adding $INSTALL_DIR to PATH, restart your shell or run:"
        echo "    source ~/.bashrc  # or ~/.zshrc"
    fi

    echo ""
    print_success "Installation complete!"
    echo ""
}

# Run main
main
