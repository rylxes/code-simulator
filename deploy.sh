#!/bin/bash
# Enhanced deployment script for Code Simulator application using Briefcase
# This script repairs Briefcase installation issues and handles the deployment process

# ANSI color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${RESET}"
}

# Function to execute command with error handling
execute_command() {
    local command="$1"
    local message="$2"
    local allow_fail=${3:-false}

    print_message "$BLUE" "► $message"

    if eval "$command"; then
        print_message "$GREEN" "✓ Success!"
        return 0
    else
        local exit_code=$?
        if [ "$allow_fail" = true ]; then
            print_message "$YELLOW" "⚠ Command failed but continuing (Exit code: $exit_code)"
            return $exit_code
        else
            print_message "$RED" "✗ Failed to $message (Exit code: $exit_code)"
            exit 1
        fi
    fi
}

# Ensure we're in the project root directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd "$script_dir" || exit 1

# Check if this is a Python project
if [ ! -f "pyproject.toml" ]; then
    print_message "$RED" "No pyproject.toml found. This doesn't appear to be a valid Python project."
    print_message "$YELLOW" "Make sure you're running this script from the project root directory."
    exit 1
fi

# Function to completely fix Briefcase installation
fix_briefcase_installation() {
    print_message "$BLUE" "Fixing Briefcase installation..."

    # Check if we're in a virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_message "$YELLOW" "Not running in a virtual environment. Creating one..."

        # Create a new virtual environment
        execute_command "python3 -m venv .venv" "Creating virtual environment"

        # Activate the virtual environment
        execute_command "source .venv/bin/activate" "Activating virtual environment"

        print_message "$GREEN" "Virtual environment created and activated."
    else
        print_message "$GREEN" "Using existing virtual environment: $VIRTUAL_ENV"
    fi

    # Update pip to latest version
    execute_command "pip install --upgrade pip" "Upgrading pip"

    # Uninstall problematic packages
    execute_command "pip uninstall -y briefcase setuptools setuptools_scm" "Uninstalling problematic packages" true

    # Install correct version of setuptools
    execute_command "pip install 'setuptools>=61.0.0'" "Installing correct setuptools version"

    # Install setuptools_scm
    execute_command "pip install setuptools_scm" "Installing setuptools_scm"

    # Set environment variable to prevent version detection issues
    export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_BRIEFCASE=0.3.14

    # Install Briefcase with pinned version
    execute_command "pip install briefcase==0.3.14" "Installing Briefcase 0.3.14"

    # Verify installation
    if briefcase --version > /dev/null 2>&1; then
        print_message "$GREEN" "Briefcase successfully installed!"
        return 0
    else
        print_message "$RED" "Briefcase installation still has issues."
        return 1
    fi
}

# Function to clean the project
clean_project() {
    print_message "$BLUE" "Cleaning project..."

    # Remove Python cache files
    execute_command "find . -type d -name \"__pycache__\" -exec rm -r {} +  2>/dev/null || true" "Removing __pycache__ directories" true
    execute_command "find . -type f -name \"*.pyc\" -delete" "Removing .pyc files"
    execute_command "find . -type f -name \"*.pyo\" -delete" "Removing .pyo files"
    execute_command "find . -type d -name \"*.egg-info\" -exec rm -r {} + 2>/dev/null || true" "Removing .egg-info directories" true
    execute_command "find . -type d -name \"*.dist-info\" -exec rm -r {} + 2>/dev/null || true" "Removing .dist-info directories" true

    # Manual cleanup for Briefcase directories
    execute_command "rm -rf macOS/ windows/ linux/ android/ iOS/ web/ 2>/dev/null || true" "Manually cleaning build directories" true

    # If Briefcase is properly installed, use it for cleaning
    if briefcase --version > /dev/null 2>&1; then
        execute_command "briefcase clean" "Cleaning with Briefcase" true
    fi

    print_message "$GREEN" "Project cleaned successfully."
}

# Function to create a new application build
build_app() {
    local platform=$1
    print_message "$BLUE" "Building application for $platform..."

    # Ensure Briefcase is properly installed
    if ! briefcase --version > /dev/null 2>&1; then
        print_message "$YELLOW" "Briefcase is not properly installed. Attempting to fix..."
        fix_briefcase_installation
    fi

    # Make sure we have the correct versions (in case the script is run multiple times)
    export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_BRIEFCASE=0.3.14

    # Set platform-specific environment variables
    case "$platform" in
        macOS|macos|darwin)
            # Create the app for macOS
            execute_command "briefcase create macOS && briefcase build macOS" "Building for macOS"
            ;;
        windows|win)
            # Create the app for Windows
            execute_command "briefcase create windows && briefcase build windows" "Building for Windows"
            ;;
        linux)
            # Create the app for Linux
            execute_command "briefcase create linux && briefcase build linux" "Building for Linux"
            ;;
        all)
            # Create for all platforms
            execute_command "briefcase create && briefcase build" "Building for all platforms" true
            ;;
        *)
            print_message "$RED" "Unknown platform: $platform"
            exit 1
            ;;
    esac

    print_message "$GREEN" "Application build completed."
}

# Function to package the application
package_app() {
    local platform=$1

    print_message "$BLUE" "Packaging application for $platform..."

    # Ensure Briefcase is properly installed
    if ! briefcase --version > /dev/null 2>&1; then
        print_message "$YELLOW" "Briefcase is not properly installed. Attempting to fix..."
        fix_briefcase_installation
    fi

    # Make sure we have the correct versions
    export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_BRIEFCASE=0.3.14

    case "$platform" in
        macOS|macos|darwin)
            execute_command "briefcase package macOS --no-sign" "Creating macOS package (without signing)"
            ;;
        windows|win)
            execute_command "briefcase package windows" "Creating Windows package"
            ;;
        linux)
            execute_command "briefcase package linux" "Creating Linux package"
            ;;
        all)
            execute_command "briefcase package" "Creating packages for all platforms" true
            ;;
        *)
            print_message "$RED" "Unknown platform: $platform"
            exit 1
            ;;
    esac

    print_message "$GREEN" "Application packaging completed."
}

# Function to publish the app
publish_app() {
    local version=$(grep -m 1 "version" pyproject.toml | sed 's/.*version = "\(.*\)".*/\1/')

    print_message "$BLUE" "Preparing to publish version $version..."

    # Create GitHub release if appropriate tools are available
    if command -v gh &>/dev/null; then
        print_message "$BLUE" "Creating GitHub release..."

        # Check if a tag already exists for this version
        if ! git rev-parse "v$version" >/dev/null 2>&1; then
            execute_command "git tag -a \"v$version\" -m \"Version $version release\"" "Creating git tag" true
            execute_command "git push origin \"v$version\"" "Pushing git tag" true
        fi

        # Create release
        execute_command "gh release create \"v$version\" --title \"Version $version\" --notes \"Release of version $version\"" "Creating GitHub release" true

        # Upload macOS assets if they exist
        if [ -d "macOS/app" ]; then
            print_message "$BLUE" "Uploading macOS package..."
            execute_command "cd macOS/app && zip -r \"../../CodeSimulator-$version-macOS.zip\" \"Code Simulator.app\"" "Creating macOS zip archive" true
            execute_command "gh release upload \"v$version\" \"CodeSimulator-$version-macOS.zip\"" "Uploading macOS package" true
        fi

        # Upload Windows assets if they exist
        if [ -f "windows/Code Simulator-$version-setup.exe" ]; then
            print_message "$BLUE" "Uploading Windows package..."
            execute_command "gh release upload \"v$version\" \"windows/Code Simulator-$version-setup.exe\"" "Uploading Windows installer" true
        fi

        # Upload Linux assets if they exist
        if [ -f "linux/Code_Simulator-$version.AppImage" ]; then
            print_message "$BLUE" "Uploading Linux package..."
            execute_command "gh release upload \"v$version\" \"linux/Code_Simulator-$version.AppImage\"" "Uploading Linux AppImage" true
        fi
    else
        print_message "$YELLOW" "GitHub CLI not found. Skipping GitHub release creation."
        print_message "$YELLOW" "To publish to GitHub, install the GitHub CLI (gh) and run this script again."
    fi

    print_message "$GREEN" "Publication process completed."
}

# Function to detect current platform
detect_platform() {
    case "$(uname -s)" in
        Darwin*)    echo "macOS" ;;
        Linux*)     echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "all" ;;
    esac
}

# Main script execution
print_message "$BLUE" "=== Code Simulator Deployment Script ==="
print_message "$BLUE" "=== Version $(date +%Y.%m.%d) ==="

# Process command line arguments
platform=$(detect_platform)
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix-briefcase)
            fix_only=true
            shift
            ;;
        --clean)
            clean_only=true
            shift
            ;;
        --build)
            build_only=true
            shift
            ;;
        --package)
            package_only=true
            shift
            ;;
        --publish)
            publish_only=true
            shift
            ;;
        --platform)
            platform=$2
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --fix-briefcase     Only fix Briefcase installation"
            echo "  --clean             Only clean the project"
            echo "  --build             Only build the application"
            echo "  --package           Only package the application"
            echo "  --publish           Only publish the application"
            echo "  --platform [platform] Specify target platform (macos, windows, linux, all)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Execute requested actions or perform full deployment
if [ "$fix_only" = true ]; then
    fix_briefcase_installation
elif [ "$clean_only" = true ]; then
    clean_project
elif [ "$build_only" = true ]; then
    clean_project
    build_app "$platform"
elif [ "$package_only" = true ]; then
    package_app "$platform"
elif [ "$publish_only" = true ]; then
    publish_app
else
    # Full deployment process
    fix_briefcase_installation
    clean_project
    build_app "$platform"
    package_app "$platform"
    publish_app
fi

print_message "$GREEN" "=== Deployment process completed successfully ==="