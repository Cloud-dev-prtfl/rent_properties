#!/usr/bin/env bash
# Fetch pinned third-party browser libraries into static/vendor/ and record their SHA-256.
# `scripts/fetch-vendor.sh --verify` (make vendor-verify) checks files against the manifest.
set -euo pipefail

VENDOR_DIR="static/vendor"
MANIFEST="$VENDOR_DIR/manifest.json"
# name|version|url
LIBS=(
  "htmx.min.js|2.0.11|https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"
  "alpine-csp.min.js|3.17.5|https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.17.5/dist/cdn.min.js"
)

sha() { (command -v sha256sum >/dev/null && sha256sum "$1" || shasum -a 256 "$1") | cut -d' ' -f1; }

if [[ "${1:-}" == "--verify" ]]; then
  python3 - "$MANIFEST" "$VENDOR_DIR" <<'PY'
import hashlib, json, sys, pathlib
manifest, vendor = json.load(open(sys.argv[1])), pathlib.Path(sys.argv[2])
bad = [n for n, m in manifest.items() if hashlib.sha256((vendor / n).read_bytes()).hexdigest() != m["sha256"]]
print("vendored files OK" if not bad else f"hash mismatch: {bad}")
sys.exit(1 if bad else 0)
PY
  exit $?
fi

mkdir -p "$VENDOR_DIR"
echo "{" > "$MANIFEST.tmp"
for i in "${!LIBS[@]}"; do
  IFS="|" read -r name version url <<< "${LIBS[$i]}"
  curl -fsSL -o "$VENDOR_DIR/$name" "$url"
  sep=$([[ $i -lt $((${#LIBS[@]} - 1)) ]] && echo "," || echo "")
  printf '  "%s": {"version": "%s", "url": "%s", "sha256": "%s"}%s\n' \
    "$name" "$version" "$url" "$(sha "$VENDOR_DIR/$name")" "$sep" >> "$MANIFEST.tmp"
done
echo "}" >> "$MANIFEST.tmp"
mv "$MANIFEST.tmp" "$MANIFEST"
cat "$MANIFEST"
