#!/usr/bin/env python3
"""Exercise real 1.0.0 -> 1.0.1 release installs on a disposable emulator only."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist/qa/routing-upgrade"
ADB = str(Path.home() / "Library/Android/sdk/platform-tools/adb")
SERIAL = "emulator-5554"
PACKAGE = "com.huban.client"
TEST = PACKAGE + ".test/androidx.test.runner.AndroidJUnitRunner"
CLASS = "com.v2ray.ang.handler.HubanRoutingDeviceTest"

def adb(*args, check=True):
    return subprocess.run([ADB, "-s", SERIAL, *args], capture_output=True, text=True, check=check).stdout

def instrument(method):
    result = adb("shell", "am", "instrument", "-w", "-r", "-e", "class", CLASS + "#" + method, TEST)
    (OUT / (method + ".log")).write_text(result)
    if "OK (1 test)" not in result:
        raise AssertionError(result)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: qa-routing-upgrade.py <release-androidTest.apk>")
    if adb("shell", "getprop", "ro.kernel.qemu").strip() != "1":
        raise SystemExit("Refusing to replace application data on a physical device.")
    OUT.mkdir(parents=True, exist_ok=True)
    test_apk = str(Path(sys.argv[1]).resolve())
    report = []
    # Every scenario seeds the prior shipped binary, then performs install -r with the same release certificate.
    for scenario, seed, verify in [
        ("custom", "seedCustomRules", "verifyCustomPreserved"),
        ("global", "seedGlobalRules", "verifyGlobalPreserved"),
        ("default", "seedLegacyDefaults", "verifyDefaultUpgrade"),
    ]:
        adb("uninstall", PACKAGE, check=False)
        adb("install", str(ROOT / "dist/Huban-1.0.0-arm64-v8a.apk"))
        adb("install", "-r", test_apk)
        instrument(seed)
        adb("shell", "am", "force-stop", PACKAGE)
        adb("install", "-r", str(ROOT / "dist/Huban-1.0.1-arm64-v8a.apk"))
        instrument(verify)
        destination = OUT / scenario
        destination.mkdir(exist_ok=True)
        adb("pull", "/sdcard/Android/data/" + PACKAGE + "/files/routing-qa/.", str(destination))
        for config in destination.glob("*-config.json"):
            shutil.copy2(config, OUT / config.name)
        report.append({"scenario": scenario, "upgrade": "1.0.0 -> 1.0.1 install -r", "result": "passed"})
        print(scenario + ": passed", flush=True)
    (OUT / "upgrade-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
