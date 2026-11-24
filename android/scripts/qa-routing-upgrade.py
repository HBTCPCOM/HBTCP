#!/usr/bin/env python3
"""Exercise bundled routing formats with the current release on a disposable emulator only."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist/qa/routing-upgrade"
ADB = str(Path.home() / "Library/Android/sdk/platform-tools/adb")
SERIAL = "emulator-5554"
PACKAGE = "com.hbtcp.client"
TEST = PACKAGE + ".test/androidx.test.runner.AndroidJUnitRunner"
CLASS = "com.v2ray.ang.handler.HbtcpRoutingDeviceTest"

def adb(*args, check=True):
    return subprocess.run([ADB, "-s", SERIAL, *args], capture_output=True, text=True, check=check).stdout

def instrument(method):
    result = adb("shell", "am", "instrument", "-w", "-r", "-e", "class", CLASS + "#" + method, TEST)
    (OUT / (method + ".log")).write_text(result)
    if "OK (1 test)" not in result:
        raise AssertionError(result)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: qa-routing-upgrade.py <current-release.apk> <release-androidTest.apk>")
    if adb("shell", "getprop", "ro.kernel.qemu").strip() != "1":
        raise SystemExit("Refusing to replace application data on a physical device.")
    OUT.mkdir(parents=True, exist_ok=True)
    release_apk = str(Path(sys.argv[1]).resolve())
    test_apk = str(Path(sys.argv[2]).resolve())
    report = []
    # The new application ID uses fresh storage; seed prior routing formats explicitly inside that sandbox.
    for scenario, seed, verify in [
        ("custom", "seedCustomRules", "verifyCustomPreserved"),
        ("global", "seedGlobalRules", "verifyGlobalPreserved"),
        ("default", "seedLegacyDefaults", "verifyDefaultUpgrade"),
    ]:
        adb("uninstall", PACKAGE, check=False)
        adb("install", release_apk)
        adb("install", "-r", test_apk)
        instrument(seed)
        adb("shell", "am", "force-stop", PACKAGE)
        instrument(verify)
        destination = OUT / scenario
        destination.mkdir(exist_ok=True)
        adb("pull", "/sdcard/Android/data/" + PACKAGE + "/files/routing-qa/.", str(destination))
        for config in destination.glob("*-config.json"):
            shutil.copy2(config, OUT / config.name)
        report.append({"scenario": scenario, "fixture": "preceding routing format -> current defaults", "result": "passed"})
        print(scenario + ": passed", flush=True)
    (OUT / "upgrade-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
