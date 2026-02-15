#!/bin/bash
# Gift Reminder - macOS Installer
# Installs the app, creates a virtual environment, and sets up background notifications.

set -e

APP_NAME="GiftReminder"
INSTALL_DIR="$HOME/.gift-reminder"
PLIST_NAME="com.giftreminder.notify"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "========================================="
echo "  Gift Reminder - macOS Installer"
echo "========================================="
echo ""

# Check Python version
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required. Install it from https://python.org or via Homebrew."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python ${PYTHON_VERSION}"

# Create install directory
echo "Installing to ${INSTALL_DIR}..."
mkdir -p "$INSTALL_DIR"

# Copy source files
cp -r "$SCRIPT_DIR/gift_reminder" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/setup.py" "$INSTALL_DIR/"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r "$INSTALL_DIR/requirements.txt"
pip install --quiet -e "$INSTALL_DIR"

# Create launcher script
cat > "$INSTALL_DIR/launch.sh" << 'LAUNCHER'
#!/bin/bash
INSTALL_DIR="$HOME/.gift-reminder"
source "$INSTALL_DIR/venv/bin/activate"
python -m gift_reminder.app
LAUNCHER
chmod +x "$INSTALL_DIR/launch.sh"

# Create notification checker script
cat > "$INSTALL_DIR/check_notify.sh" << 'CHECKER'
#!/bin/bash
INSTALL_DIR="$HOME/.gift-reminder"
source "$INSTALL_DIR/venv/bin/activate"
python -m gift_reminder.notify_check
CHECKER
chmod +x "$INSTALL_DIR/check_notify.sh"

# Create macOS app bundle (simple .command approach)
APP_LINK="$HOME/Desktop/${APP_NAME}.command"
cat > "$APP_LINK" << APPLINK
#!/bin/bash
"$INSTALL_DIR/launch.sh"
APPLINK
chmod +x "$APP_LINK"

# Set up launchd for daily notification checks
echo "Setting up background notifications..."
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${INSTALL_DIR}/check_notify.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${INSTALL_DIR}/notify.log</string>
    <key>StandardErrorPath</key>
    <string>${INSTALL_DIR}/notify_error.log</string>
</dict>
</plist>
PLIST

# Load the launchd job
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "  How to use:"
echo "  Desktop App:"
echo "    Double-click '${APP_NAME}.command' on your Desktop"
echo "    OR run: ${INSTALL_DIR}/launch.sh"
echo ""
echo "  Web App (browser-based):"
echo "    ${INSTALL_DIR}/venv/bin/python -m gift_reminder.webapp"
echo "    Then open http://localhost:5000 in your browser"
echo ""
echo "  Background notifications run daily at 9:00 AM"
echo "  to check if any gift reminders are due."
echo ""
echo "  To uninstall:"
echo "     launchctl unload ${PLIST_PATH}"
echo "     rm -rf ${INSTALL_DIR}"
echo "     rm ${PLIST_PATH}"
echo "     rm ${APP_LINK}"
echo ""
