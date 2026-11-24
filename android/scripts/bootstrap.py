#!/usr/bin/env python3
"""Fetch pinned inputs and rebuild the same native libraries for a fresh checkout."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
INPUTS = json.loads((ROOT / "build-inputs.json").read_text())

def download(url, destination, digest):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() == digest:
        print(f"Verified existing {destination.name}")
        return
    temporary = destination.with_suffix(destination.suffix + ".download")
    try:
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Checksum mismatch: {destination.name}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Downloaded and verified {destination.name}")

if __name__ == "__main__":
    subprocess.run(["git", "submodule", "update", "--init", "--recursive"], cwd=ROOT, check=True)
    core_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT / "AndroidLibXrayLite", text=True).strip()
    if core_commit != INPUTS["native"]["commit"]:
        raise SystemExit("Native core revision differs from the pinned build inputs.")
    app = ROOT / "V2rayNG/app"
    download(INPUTS["native"]["url"], app / "libs/libv2ray.aar", INPUTS["native"]["sha256"])
    for name in ("geoip.dat", "geosite.dat"):
        url = f'https://github.com/Loyalsoldier/v2ray-rules-dat/releases/download/{INPUTS["geo"]["release"]}/{name}'
        download(url, app / "src/main/assets" / name, INPUTS["geo"][name])
    sdk = Path(os.environ.get("ANDROID_HOME", str(Path.home() / "Library/Android/sdk")))
    ndk = Path(os.environ.get("NDK_HOME", str(sdk / "ndk" / INPUTS["hev"]["builtWithNdk"])))
    if not (ndk / "ndk-build").exists():
        raise SystemExit("Install the NDK listed in build-inputs.json, or set NDK_HOME to a compatible NDK.")
    required = [app / "libs" / abi / name for abi in INPUTS["hev"]["abis"] for name in ("libhev-socks5-tunnel.so", "libhevsockstun.so")]
    if not all(path.exists() for path in required):
        subprocess.run(["bash", "compile-hevtun.sh"], cwd=ROOT, env={**os.environ, "NDK_HOME": str(ndk)}, check=True)
        shutil.copytree(ROOT / "libs", app / "libs", dirs_exist_ok=True)
    (ROOT / "V2rayNG/local.properties").write_text(f"sdk.dir={sdk}\n")
    print("Build inputs ready. Run bash scripts/build-release.sh after configuring local signing.")
