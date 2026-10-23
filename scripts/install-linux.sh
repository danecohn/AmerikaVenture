#!/bin/sh
set -eu
SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET="$HOME/.local/opt/amerika-venture"
mkdir -p "$TARGET" "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor/128x128/apps" "$HOME/.local/bin"
cp -R "$SOURCE"/. "$TARGET"/
chmod +x "$TARGET/Venture" "$TARGET/firefox" "$TARGET/firefox-bin"
ln -sf "$TARGET/Venture" "$HOME/.local/bin/Venture"
cp "$TARGET/browser/chrome/icons/default/default128.png" "$HOME/.local/share/icons/hicolor/128x128/apps/amerika-venture.png"
cat > "$HOME/.local/share/applications/amerika-venture.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Venture
Comment=AltStack LLC browser based on Firefox
Exec="$TARGET/Venture" %u
Icon=amerika-venture
Terminal=false
Categories=Network;WebBrowser;
MimeType=text/html;x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
StartupWMClass=Venture
EOF
printf '%s\n' 'Venture installed. Open it from your application launcher.'
