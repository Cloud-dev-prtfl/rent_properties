#!/usr/bin/env bash
# Download the pinned Tailwind CSS standalone CLI and verify its SHA-256 (docs/architecture/03 §9).
set -euo pipefail

VERSION="4.3.3"
DEST="${1:-.tools/tailwindcss}"


case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) PLATFORM=linux-x64 EXPECTED=dc61b3ac6b8c9ca874c0cc4c57b2409791a64c5540404ca5f5367360babc313a ;;
  Linux-aarch64 | Linux-arm64) PLATFORM=linux-arm64 EXPECTED=55fd0b241214eff3de1e8ee4f22796662f2d2e7a49bcfca7477cfd0bac398195 ;;
  Darwin-arm64) PLATFORM=macos-arm64 EXPECTED=cdf646702987a743464dff4d9c60fd4480d1c1e73dd819a9a67f1078815dce9d ;;
  Darwin-x86_64) PLATFORM=macos-x64 EXPECTED=7922e0953f2110c05976e3bf58f14e643d90427575e766b7d433f5f80cbee7e1 ;;
  *) echo "Unsupported platform: $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac

if [[ -x "$DEST" ]] && "$DEST" --help 2>/dev/null | grep -q "v${VERSION}"; then
  exit 0
fi

mkdir -p "$(dirname "$DEST")"
TMP="$(mktemp)"
curl -fsSL -o "$TMP" "https://github.com/tailwindlabs/tailwindcss/releases/download/v${VERSION}/tailwindcss-${PLATFORM}"
ACTUAL="$( (command -v sha256sum >/dev/null && sha256sum "$TMP" || shasum -a 256 "$TMP") | cut -d' ' -f1)"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "Checksum mismatch for tailwindcss-${PLATFORM}: $ACTUAL" >&2
  rm -f "$TMP"; exit 1
fi
mv "$TMP" "$DEST" && chmod +x "$DEST"
echo "tailwindcss v${VERSION} (${PLATFORM}) → $DEST"
