#!/bin/sh
# Anatomy Lab installer for Linux: downloads the app to your Desktop and adds a launcher.
# Run:  sh install-linux.sh
set -e
REPO=2004Kunj/learnAutonomy
DESK="$HOME/Desktop"; [ -d "$DESK" ] || DESK="$HOME"
DEST="$DESK/Anatomy Lab"
TMP=$(mktemp -d)
echo "Downloading Anatomy Lab from github.com/$REPO (about 90 MB)..."
curl -fL --progress-bar -o "$TMP/lab.zip" "https://codeload.github.com/$REPO/zip/refs/heads/main"
unzip -q "$TMP/lab.zip" -d "$TMP"
SRC=$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -n 1)
[ -f "$SRC/app/index.html" ] || { echo "The download did not contain the app."; exit 1; }
mkdir -p "$DEST"; rm -rf "$DEST/app"
cp -R "$SRC/app" "$DEST/app"
for f in README.md LICENSE LICENSE-DATA.md; do [ -f "$SRC/$f" ] && cp "$SRC/$f" "$DEST/"; done
L="$DEST/Start Anatomy Lab.command"
cat > "$L" <<'EOF'
#!/bin/sh
# Serves the app on http://localhost:8259 and opens your browser. Close this window to stop.
cd "$(dirname "$0")/app" || exit 1
PORT=8259
URL="http://localhost:$PORT/"
( sleep 1; if command -v open >/dev/null; then open "$URL"; else xdg-open "$URL" >/dev/null 2>&1; fi ) &
echo "Anatomy Lab is running at $URL - close this window to stop it."
if command -v python3 >/dev/null; then exec python3 -m http.server "$PORT" --bind 127.0.0.1
elif command -v ruby >/dev/null; then exec ruby -run -e httpd . -p "$PORT" -b 127.0.0.1
else echo "Python 3 is needed to run the app (macOS: run 'xcode-select --install')."; read x; fi
EOF
chmod +x "$L"
rm -rf "$TMP"
echo "Done. Installed to: $DEST"
echo "Double-click 'Start Anatomy Lab.command' in that folder to open it. Run this installer again to update."
