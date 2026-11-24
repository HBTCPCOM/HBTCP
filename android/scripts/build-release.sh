#!/usr/bin/env bash
set -euo pipefail
HBTCP_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -z "${JAVA_HOME:-}" && -d /opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home ]]; then
  export JAVA_HOME=/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home
fi
export HBTCP_SIGNING_PROPERTIES="${HBTCP_SIGNING_PROPERTIES:-$HOME/.local/share/hbtcp-android/signing/signing.properties}"
if [[ ! -f "$HBTCP_SIGNING_PROPERTIES" ]]; then
  echo "Missing local release signing configuration. See README-HBTCP.md."
  exit 1
fi
cd "$HBTCP_ROOT/V2rayNG"
./gradlew :app:assemblePlaystoreRelease "$@" --console=plain
mkdir -p "$HBTCP_ROOT/dist"
python3 - "$HBTCP_ROOT" <<'PY'
from pathlib import Path
import hashlib, json, re, shutil, sys
root = Path(sys.argv[1])
output_dir = root / 'V2rayNG/app/build/outputs/apk/playstore/release'
metadata = json.loads((output_dir / 'output-metadata.json').read_text())
for element in sorted(metadata['elements'], key=lambda item: item['outputFile']):
    apk = output_dir / element['outputFile']
    match = re.fullmatch(r'v2rayNG_(.+)_(arm64-v8a|armeabi-v7a|x86_64|x86|universal)', apk.stem)
    if not match:
        raise SystemExit(f'Unexpected APK name: {apk.name}')
    version, abi = match.groups()
    output = root / 'dist' / f'HBTCP-{version}-{abi}.apk'
    shutil.copy2(apk, output)
    print(output.name, output.stat().st_size)
files = sorted((root / 'dist').glob('*.apk'))
(root / 'dist/SHA256SUMS').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n' for f in files))
PY
