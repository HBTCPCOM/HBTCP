#!/usr/bin/env python3
"""Reproduce Android vectors from the original Hbtcp logo and localized app copy."""
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
import shutil
import re

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "V2rayNG/app/src/main/res"
ANDROID = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID)

def attribute(name):
    return f"{{{ANDROID}}}{name}"

def logo_vector():
    source = ET.parse(ROOT / "branding/hbtcp-logo.svg").getroot()
    vector = ET.Element("vector", {
        attribute("width"): "180dp", attribute("height"): "168dp",
        attribute("viewportWidth"): "1298", attribute("viewportHeight"): "1212",
    })
    def walk(element, fill="#080603", parent=vector):
        fill = element.attrib.get("fill", fill)
        if element.tag.endswith("path"):
            ET.SubElement(parent, "path", {
                attribute("fillColor"): fill,
                attribute("pathData"): element.attrib["d"],
            })
        else:
            for child in element:
                walk(child, fill, parent)
    walk(source)
    ET.ElementTree(vector).write(RES / "drawable/hbtcp_logo.xml", encoding="utf-8", xml_declaration=True)

def icon(name, paths):
    vector = ET.Element("vector", {
        attribute("width"): "24dp", attribute("height"): "24dp",
        attribute("viewportWidth"): "24", attribute("viewportHeight"): "24",
    })
    for path in paths:
        ET.SubElement(vector, "path", {
            attribute("pathData"): path, attribute("fillColor"): "#00000000",
            attribute("strokeColor"): "#FF29251E", attribute("strokeWidth"): "1.8",
            attribute("strokeLineCap"): "round", attribute("strokeLineJoin"): "round",
        })
    ET.ElementTree(vector).write(RES / f"drawable/{name}.xml", encoding="utf-8", xml_declaration=True)

EN = {
    "hbtcp_wordmark": "HBTCP", "hbtcp_ready": "Ready to go", "hbtcp_departed": "Connected",
    "hbtcp_ready_hint": "Import a subscription, then tap Start.", "hbtcp_connected_hint": "Your connection is running.",
    "hbtcp_connected": "Connected", "hbtcp_disconnected": "Offline", "hbtcp_mode": "Proxy mode",
    "hbtcp_rule": "Rules", "hbtcp_global": "Global", "hbtcp_rule_hint": "Connect directly in China; proxy other traffic.",
    "hbtcp_global_hint": "Proxy all traffic except local networks.", "hbtcp_subscription": "Subscription",
    "hbtcp_import_link": "Import subscription link", "hbtcp_import_methods": "Link / QR code / Clipboard",
    "hbtcp_import_options": "Choose an import method", "hbtcp_imported": "Subscription imported",
    "hbtcp_node_count": "%1$d nodes · tap to manage", "hbtcp_scan": "Scan QR code", "hbtcp_clipboard": "Import from clipboard",
    "hbtcp_node": "Connection node", "hbtcp_select_after_import": "Select after importing",
    "hbtcp_switch_hint": "Switch nodes directly. No need to stop and start again.",
    "hbtcp_start": "Start", "hbtcp_disconnect": "Disconnect", "hbtcp_importing": "Importing…",
    "hbtcp_subscription_url": "Subscription link or share link", "hbtcp_import_help": "Subscription URLs refresh when you open the app. Individual node links must be imported again.",
    "hbtcp_import": "Import", "hbtcp_cancel": "Cancel", "hbtcp_close": "Close", "hbtcp_select_node": "Select a node",
    "hbtcp_import_empty": "Paste a subscription or share link first.",
    "hbtcp_import_invalid": "Enter a complete subscription URL with a valid host.",
    "hbtcp_import_failed": "No nodes imported. Check the link, network, or subscription format and try again.",
    "hbtcp_mode_failed": "Could not apply the mode. Try again.", "hbtcp_more": "More options",
    "hbtcp_refresh": "Refresh subscriptions", "hbtcp_manage_subscriptions": "Manage subscriptions",
    "hbtcp_logs": "Connection logs", "hbtcp_about": "About HBTCP", "hbtcp_launcher_name": "HBTCP", "hbtcp_customer_service": "Telegram support", "hbtcp_customer_service_handle": r"\@HBTCP_bot",
}
ZH = {
    "hbtcp_wordmark": "HBTCP", "hbtcp_ready": "准备出发", "hbtcp_departed": "已经出发",
    "hbtcp_ready_hint": "导入订阅后，点击启动。", "hbtcp_connected_hint": "连接已开启，随时切换节点。",
    "hbtcp_connected": "已连接", "hbtcp_disconnected": "未连接", "hbtcp_mode": "代理模式",
    "hbtcp_rule": "分流", "hbtcp_global": "全局", "hbtcp_rule_hint": "国内直连，其余流量通过代理。",
    "hbtcp_global_hint": "除局域网外，所有流量均通过代理。", "hbtcp_subscription": "订阅",
    "hbtcp_import_link": "导入订阅链接", "hbtcp_import_methods": "链接 / 二维码 / 剪贴板",
    "hbtcp_import_options": "选择订阅导入方式", "hbtcp_imported": "已导入订阅",
    "hbtcp_node_count": "%1$d 个节点 · 点击管理", "hbtcp_scan": "扫二维码", "hbtcp_clipboard": "从剪贴板导入",
    "hbtcp_node": "连接节点", "hbtcp_select_after_import": "导入后选择",
    "hbtcp_switch_hint": "切换节点无需停止后再启动，直接点击新节点即可",
    "hbtcp_start": "启动", "hbtcp_disconnect": "断开", "hbtcp_importing": "正在导入…",
    "hbtcp_subscription_url": "订阅链接或节点分享链接", "hbtcp_import_help": "订阅链接会在打开 App 时刷新。单条节点分享链接需重新导入。",
    "hbtcp_import": "导入订阅", "hbtcp_cancel": "取消", "hbtcp_close": "关闭", "hbtcp_select_node": "选择节点",
    "hbtcp_import_empty": "请先粘贴订阅链接或节点分享链接。",
    "hbtcp_import_invalid": "请输入包含有效服务器地址的完整订阅链接。",
    "hbtcp_import_failed": "没有导入节点，请检查链接、网络或订阅格式后重试。",
    "hbtcp_mode_failed": "模式切换失败，请重试。", "hbtcp_more": "更多选项",
    "hbtcp_refresh": "更新订阅", "hbtcp_manage_subscriptions": "管理订阅",
    "hbtcp_logs": "连接日志", "hbtcp_about": "关于 HBTCP", "hbtcp_launcher_name": "HBTCP", "hbtcp_customer_service": "Telegram 客服", "hbtcp_customer_service_handle": r"\@HBTCP_bot",
}

def strings():
    for locale in ("values", "values-zh-rCN", "values-zh-rTW", "values-vi", "values-ru", "values-fa", "values-ar", "values-az", "values-bn", "values-bqi-rIR"):
        directory = RES / locale
        directory.mkdir(exist_ok=True)
        values = ZH if "zh-" in locale else EN
        lines = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<resources>"]
        for key, value in values.items():
            lines.append(f'    <string name="{key}">{escape(value).replace(chr(39), chr(92) + chr(39))}</string>')
        lines.append("</resources>")
        (directory / "hbtcp_strings.xml").write_text("\n".join(lines) + "\n")
        original = directory / "strings.xml"
        if original.exists():
            text = original.read_text()
            text = re.sub(r'(<string name="app_name"[^>]*>).*?(</string>)', lambda m: m[1] + "HBTCP" + m[2], text)
            original.write_text(text)

def notices():
    assets = ROOT / "V2rayNG/app/src/main/assets"
    license_text = (ROOT / "branding/LUCIDE-LICENSE.txt").read_text()
    (assets / "HBTCP-THIRD-PARTY-NOTICES.txt").write_text(license_text)
    shutil.copy2(ROOT / "LICENSE", assets / "GPL-3.0.txt")

if __name__ == "__main__":
    logo_vector()
    # Lucide icon geometry (ISC); see branding/NOTICE.md for attribution.
    icon("hbtcp_power", ["M12,2L12,12", "M18.36,5.64A9,9 0,1 1,5.64,5.64"])
    icon("hbtcp_split", ["M16,3L21,3L21,8", "M8,3L3,3L3,8", "M12,22L12,11L3,3", "M12,11L21,3"])
    icon("hbtcp_globe", ["M22,12A10,10 0,1 1,2,12A10,10 0,1 1,22,12", "M2,12L22,12", "M12,2A19,19 0,0 1,12,22A19,19 0,0 1,12,2"])
    icon("hbtcp_link", ["M10,13a5,5 0,0 0,7.54,.54l3,-3a5,5 0,0 0,-7.07,-7.07l-1.72,1.71", "M14,11a5,5 0,0 0,-7.54,-.54l-3,3a5,5 0,0 0,7.07,7.07l1.71,-1.71"])
    strings()
    notices()
