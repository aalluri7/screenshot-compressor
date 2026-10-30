#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "=== Setting up Screenshot Compressor ==="

# Check if running in Termux
if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then
  echo "Detected Termux environment on Android."
  echo "Installing system packages via pkg..."
  pkg update -y
  pkg install -y python python-pillow termux-api git
else
  echo "Detected standard Linux / macOS / Unix environment."
  if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt
  elif command -v pip >/dev/null 2>&1; then
    pip install -r requirements.txt
  else
    echo "Error: Neither pip3 nor pip found. Please install Python package manager."
    exit 1
  fi
fi

# Initialize config.json from example if missing
if [ ! -f "config.json" ] && [ -f "config.example.json" ]; then
  echo "Creating default config.json from template..."
  cp config.example.json config.json
fi

# Make scripts executable
chmod +x compress.py 2>/dev/null || true

echo ""
echo "=== Setup Complete! ==="
echo "You can now run: python compress.py"
