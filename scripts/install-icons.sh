#!/usr/bin/env bash
# Install the bundled Cendre icon theme for the current user.
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
icon_dir="${XDG_DATA_HOME:-$HOME/.local/share}/icons/Cendre"
mkdir -p "$icon_dir"
cp "$repo_dir/icons/Cendre/index.theme" "$repo_dir/icons/Cendre/LICENSE" "$repo_dir/icons/Cendre/ATTRIBUTION.txt" "$icon_dir/"
for source_dir in "$repo_dir/icons/Cendre/"[0-9]*; do
  [[ -d "$source_dir" ]] && cp -R "$source_dir" "$icon_dir/"
done
if command -v gtk-update-icon-cache >/dev/null; then
  gtk-update-icon-cache --force --ignore-theme-index "$icon_dir"
fi
gsettings set org.gnome.desktop.interface icon-theme Cendre
printf 'Installed Cendre icons in %s\n' "$icon_dir"
