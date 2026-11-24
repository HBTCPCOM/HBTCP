#!/usr/bin/env python3
"""Drive the real APK on an emulator; no app code bypass or injected VPN state."""
from pathlib import Path
import json
import re
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist/qa"
OUT.mkdir(parents=True, exist_ok=True)
ADB = str(Path.home() / "Library/Android/sdk/platform-tools/adb")
PACKAGE = "com.hbtcp.client"

def adb(*args, **kwargs):
    return subprocess.run([ADB, *args], capture_output=True, text=True, check=True, **kwargs).stdout

def tree():
    adb("shell", "uiautomator", "dump", "/sdcard/hbtcp-qa.xml")
    return ET.fromstring(adb("exec-out", "cat", "/sdcard/hbtcp-qa.xml"))

def find(text, exact=True):
    for node in tree().iter("node"):
        values = (node.get("text", ""), node.get("content-desc", ""))
        if (text in values) if exact else any(text in value for value in values):
            return node
    return None

def click(text, exact=True):
    node = find(text, exact)
    if node is None:
        raise AssertionError(f"UI control missing: {text}")
    bounds = [int(value) for value in re.findall(r"\d+", node.get("bounds"))]
    adb("shell", "input", "tap", str((bounds[0] + bounds[2]) // 2), str((bounds[1] + bounds[3]) // 2))

def wait_text(text, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if find(text, exact=False) is not None:
            return
    raise AssertionError(f"UI state did not arrive: {text}")

def screenshot(name):
    with (OUT / name).open("wb") as stream:
        subprocess.run([ADB, "exec-out", "screencap", "-p"], stdout=stream, check=True)

def probe(expected):
    command = "printf 'GET / HTTP/1.1\\r\\nHost: 1.1.1.1\\r\\nConnection: close\\r\\n\\r\\n' | toybox nc -w 12 1.1.1.1 80"
    response = adb("shell", command, timeout=20)
    (OUT / f"vpn-response-{expected}.txt").write_text(response)
    if f"HBTCP_VPN_OK_NODE_{expected}" not in response:
        raise AssertionError(f"VPN packet path did not reach node {expected}: {response[:200]}")

if __name__ == "__main__":
    adb("shell", "cmd", "locale", "set-app-locales", PACKAGE, "--user", "0", "--locales", "zh-CN")
    adb("shell", "am", "start", "-n", PACKAGE + "/com.v2ray.ang.ui.main.MainActivity")
    wait_text("准备出发")
    screenshot("home-empty.png")
    click("导入订阅链接")
    click("导入订阅")
    wait_text("请先粘贴")
    screenshot("import-empty-validation.png")
    edit = next(n for n in tree().iter("node") if n.get("class") == "android.widget.EditText")
    bounds = [int(v) for v in re.findall(r"\d+", edit.get("bounds"))]
    adb("shell", "input", "tap", str((bounds[0] + bounds[2]) // 2), str((bounds[1] + bounds[3]) // 2))
    adb("shell", "input", "text", "http://10.0.2.2:18765/subscription")
    screenshot("import-with-keyboard.png")
    click("导入订阅")
    wait_text("2 个节点")
    if find("虎斑验证节点-A") is None:
        click("虎斑验证节点-B")
        click("虎斑验证节点-A")
    wait_text("虎斑验证节点-A")
    screenshot("subscription-imported.png")
    click("全局")
    wait_text("除局域网外")
    click("启动")
    if find("OK") is not None:
        click("OK")
    elif find("确定") is not None:
        click("确定")
    wait_text("已经出发")
    screenshot("vpn-connected-node-A.png")
    probe("A")
    click("虎斑验证节点-A")
    click("虎斑验证节点-B")
    wait_text("已经出发")
    wait_text("虎斑验证节点-B")
    probe("B")
    screenshot("vpn-connected-node-B.png")
    click("断开")
    wait_text("准备出发")
    adb("shell", "am", "force-stop", PACKAGE)
    adb("shell", "am", "start", "-n", PACKAGE + "/com.v2ray.ang.ui.main.MainActivity")
    wait_text("虎斑验证节点-B")
    wait_text("除局域网外")
    screenshot("selection-restored.png")
    records = json.loads(urllib.request.urlopen("http://127.0.0.1:18765/results").read())
    assert {record["node"] for record in records} == {"A", "B"}, records
    report = {"result": "passed", "device": adb("shell", "getprop", "ro.build.version.release").strip(), "checks": ["empty import error", "subscription import with keyboard visible", "global mode", "VPN consent and real TUN traffic through node A", "switch to node B while connected and route real traffic", "stop", "node and mode restored after force-stop"], "network_requests": records}
    (OUT / "network-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))
