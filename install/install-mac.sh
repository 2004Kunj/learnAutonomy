#!/bin/sh
# Anatomy Lab installer for macOS: downloads the latest version and puts "Anatomy Lab.app" on your Desktop.
# Double-click this file (or run: sh Install-AnatomyLab-Mac.command). Run it again any time to update.
set -e
REPO=2004Kunj/learnAutonomy
APP="$HOME/Desktop/Anatomy Lab.app"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
echo ""
echo "  Installing Anatomy Lab (KNES 259) to your Desktop..."
echo "  Downloading from github.com/$REPO (about 90 MB)..."
curl -fL --progress-bar -o "$TMP/lab.zip" "https://codeload.github.com/$REPO/zip/refs/heads/main"
echo "  Unpacking..."
unzip -q "$TMP/lab.zip" -d "$TMP"
SRC=$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)
[ -f "$SRC/app/index.html" ] && [ -f "$SRC/install/mac/server.pl" ] || { echo "  The download did not contain the app."; exit 1; }
pkill -f "Anatomy Lab.app/Contents/Resources/server.pl" 2>/dev/null || true     # stop an older copy before replacing it
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp -R "$SRC/app" "$APP/Contents/Resources/app"
cp "$SRC/install/mac/server.pl" "$SRC/install/mac/AppIcon.icns" "$APP/Contents/Resources/"
cp "$SRC/install/mac/launcher.sh" "$APP/Contents/MacOS/AnatomyLab"
for f in README.md LICENSE LICENSE-DATA.md; do [ -f "$SRC/$f" ] && cp "$SRC/$f" "$APP/Contents/Resources/"; done
chmod +x "$APP/Contents/MacOS/AnatomyLab"
VER=$(date +%Y.%m.%d)
cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Anatomy Lab</string>
  <key>CFBundleDisplayName</key><string>Anatomy Lab</string>
  <key>CFBundleIdentifier</key><string>io.github.2004kunj.anatomylab</string>
  <key>CFBundleExecutable</key><string>AnatomyLab</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>$VER</string>
  <key>CFBundleVersion</key><string>$VER</string>
  <key>LSUIElement</key><true/>
  <key>LSMinimumSystemVersion</key><string>10.13</string>
</dict></plist>
EOF
xattr -cr "$APP" 2>/dev/null || true
touch "$APP"
echo ""
echo "  Done. \"Anatomy Lab\" is on your Desktop. Double-click it any time to open the app."
echo "  Run this installer again later to update to the newest version."
command -v open >/dev/null && open "$APP" || true
