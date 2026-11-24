#!/usr/bin/env python3
"""Drive the signed APK through real subscription changes without injecting UI or daemon state."""
from pathlib import Path
import importlib.util
import json
import re
import time
import urllib.request

spec = importlib.util.spec_from_file_location("qa", Path(__file__).with_name("qa-emulator.py"))
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
OUT = qa.OUT / "startup-refresh"
OUT.mkdir(exist_ok=True)

def results():
    return json.loads(urllib.request.urlopen("http://127.0.0.1:18765/results").read())

def change(phase):
    request = urllib.request.Request("http://127.0.0.1:18765/state", data=json.dumps({"phase": phase}).encode(), method="POST")
    urllib.request.urlopen(request).close()

def open_again():
    qa.adb("shell", "input", "keyevent", "KEYCODE_HOME")
    time.sleep(11)
    before = len(results()["requests"])
    qa.adb("shell", "am", "start", "-n", qa.PACKAGE + "/com.v2ray.ang.ui.main.MainActivity")
    deadline = time.monotonic() + 30
    while len(results()["requests"]) <= before:
        if time.monotonic() >= deadline:
            raise AssertionError("Returning to app did not fetch its saved subscription URL")
        time.sleep(.2)
    # UI is observed after the real HTTP response has been applied, not just after a request is sent.
    time.sleep(2)

def starts():
    return qa.adb("logcat", "-d", "-v", "brief").count("StartCore-Manager: Starting core loop")

if __name__ == "__main__":
    assert qa.adb("shell", "getprop", "ro.kernel.qemu").strip() == "1"
    qa.adb("shell", "pm", "clear", qa.PACKAGE)
    qa.adb("shell", "cmd", "locale", "set-app-locales", qa.PACKAGE, "--user", "0", "--locales", "zh-CN")
    qa.adb("logcat", "-c")
    change("initial")
    initial_requests = len(results()["requests"])
    qa.adb("shell", "am", "start", "-n", qa.PACKAGE + "/com.v2ray.ang.ui.main.MainActivity")
    qa.wait_text("准备出发")
    assert len(results()["requests"]) == initial_requests
    assert qa.find("Allow", exact=False) is None
    qa.screenshot("1.0.2-home-empty.png")
    qa.click("导入订阅链接")
    edit = next(n for n in qa.tree().iter("node") if n.get("class") == "android.widget.EditText")
    bounds = [int(v) for v in re.findall(r"\d+", edit.get("bounds"))]
    qa.adb("shell", "input", "tap", str((bounds[0] + bounds[2]) // 2), str((bounds[1] + bounds[3]) // 2))
    qa.adb("shell", "input", "text", "http://10.0.2.2:18765/subscription")
    qa.click("导入订阅")
    qa.wait_text("2 个节点")
    if qa.find("虎斑验证节点-A") is None:
        qa.click("虎斑验证节点-B")
        qa.click("虎斑验证节点-A")
    qa.click("启动")
    if qa.find("OK") is not None: qa.click("OK")
    elif qa.find("确定") is not None: qa.click("确定")
    qa.wait_text("已经出发")
    qa.probe("A")
    before = starts()
    open_again()
    qa.wait_text("虎斑验证节点-A")
    assert starts() == before, "Unchanged connection parameters restarted the VPN"
    qa.probe("A")
    print("unchanged subscription: kept selected node and live connection", flush=True)
    change("changed")
    open_again()
    qa.wait_text("虎斑验证节点-A")
    qa.wait_text("已经出发")
    qa.probe("B")
    qa.click("虎斑验证节点-A")
    qa.wait_text("虎斑验证节点-C")
    assert qa.find("虎斑验证节点-B") is None
    qa.click("关闭")
    qa.screenshot("1.0.2-updated-node-connected.png")
    print("changed subscription: refreshed list, retained node name, applied new endpoint through real VPN", flush=True)
    for phase in ("failure", "invalid"):
        change(phase)
        before = starts()
        open_again()
        qa.wait_text("虎斑验证节点-A")
        qa.click("虎斑验证节点-A")
        qa.wait_text("虎斑验证节点-C")
        qa.click("关闭")
        assert starts() == before
        qa.probe("B")
        print(phase + ": retained cached list and active connection", flush=True)
    qa.click("断开")
    qa.wait_text("准备出发")
    fixture = results()
    fixture["requests"] = fixture["requests"][initial_requests:]
    report = {"result": "passed", "version": "1.0.2", "checks": ["empty startup", "no notification permission dialog", "import", "foreground auto refresh", "unchanged selected node does not restart", "changed selected endpoint reloads active VPN", "new and removed nodes reflected", "HTTP failure preserves cache", "invalid response preserves cache"], "fixture": fixture}
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("PASS: startup refresh", flush=True)
