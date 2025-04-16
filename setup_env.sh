#!/bin/bash
# Script to set up compatible environment for HypnoBot

set -e  # Exit on error

# Print colored status messages
function print_status() {
  echo -e "\e[34m>>> $1\e[0m"
}

print_status "Setting up HypnoBot environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
  echo "Python 3 is not installed. Please install Python 3.8 or newer and try again."
  exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
  echo "Python 3.8 or newer is required. You have Python $PYTHON_VERSION."
  exit 1
fi

print_status "Python $PYTHON_VERSION detected."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  print_status "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing compatible dependencies..."
pip install --upgrade pip
pip install -r requirements-compatible.txt

# Check for .env file
if [ ! -f ".env" ]; then
  print_status "Creating .env file from template..."
  cp .env.example .env
  echo "Please edit .env file and add your OpenAI API key."
fi

print_status "Environment setup complete!"
print_status "Run 'source venv/bin/activate' to activate the virtual environment."
print_status "Then run './run_cli.py' or 'python run_api.py' to start the bot." 