#!/usr/bin/env python3
"""Reproduce Android vectors from the original Huban logo and localized app copy."""
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
    source = ET.parse(ROOT / "branding/huban-logo.svg").getroot()
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
    ET.ElementTree(vector).write(RES / "drawable/huban_logo.xml", encoding="utf-8", xml_declaration=True)

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
    "huban_wordmark": "HBTCP", "huban_ready": "Ready to go", "huban_departed": "Connected",
    "huban_ready_hint": "Import a subscription, then tap Start.", "huban_connected_hint": "Your connection is running.",
    "huban_connected": "Connected", "huban_disconnected": "Offline", "huban_mode": "Proxy mode",
    "huban_rule": "Rules", "huban_global": "Global", "huban_rule_hint": "Connect directly in China; proxy other traffic.",
    "huban_global_hint": "Proxy all traffic except local networks.", "huban_subscription": "Subscription",
    "huban_import_link": "Import subscription link", "huban_import_methods": "Link / QR code / Clipboard",
    "huban_import_options": "Choose an import method", "huban_imported": "Subscription imported",
    "huban_node_count": "%1$d nodes · tap to manage", "huban_scan": "Scan QR code", "huban_clipboard": "Import from clipboard",
    "huban_node": "Connection node", "huban_select_after_import": "Select after importing",
    "huban_switch_hint": "Switch nodes directly. No need to stop and start again.",
    "huban_start": "Start", "huban_disconnect": "Disconnect", "huban_importing": "Importing…",
    "huban_subscription_url": "Subscription link or share link", "huban_import_help": "Subscription URLs refresh when you open the app. Individual node links must be imported again.",
    "huban_import": "Import", "huban_cancel": "Cancel", "huban_close": "Close", "huban_select_node": "Select a node",
    "huban_import_empty": "Paste a subscription or share link first.",
    "huban_import_invalid": "Enter a complete subscription URL with a valid host.",
    "huban_import_failed": "No nodes imported. Check the link, network, or subscription format and try again.",
    "huban_mode_failed": "Could not apply the mode. Try again.", "huban_more": "More options",
    "huban_refresh": "Refresh subscriptions", "huban_manage_subscriptions": "Manage subscriptions",
    "huban_logs": "Connection logs", "huban_about": "About HBTCP", "huban_launcher_name": "HBTCP", "huban_customer_service": "Telegram support", "huban_customer_service_handle": r"\@HBTCP_bot",
}
ZH = {
    "huban_wordmark": "HBTCP", "huban_ready": "准备出发", "huban_departed": "已经出发",
    "huban_ready_hint": "导入订阅后，点击启动。", "huban_connected_hint": "连接已开启，随时切换节点。",
    "huban_connected": "已连接", "huban_disconnected": "未连接", "huban_mode": "代理模式",
    "huban_rule": "分流", "huban_global": "全局", "huban_rule_hint": "国内直连，其余流量通过代理。",
    "huban_global_hint": "除局域网外，所有流量均通过代理。", "huban_subscription": "订阅",
    "huban_import_link": "导入订阅链接", "huban_import_methods": "链接 / 二维码 / 剪贴板",
    "huban_import_options": "选择订阅导入方式", "huban_imported": "已导入订阅",
    "huban_node_count": "%1$d 个节点 · 点击管理", "huban_scan": "扫二维码", "huban_clipboard": "从剪贴板导入",
    "huban_node": "连接节点", "huban_select_after_import": "导入后选择",
    "huban_switch_hint": "切换节点无需停止后再启动，直接点击新节点即可",
    "huban_start": "启动", "huban_disconnect": "断开", "huban_importing": "正在导入…",
    "huban_subscription_url": "订阅链接或节点分享链接", "huban_import_help": "订阅链接会在打开 App 时刷新。单条节点分享链接需重新导入。",
    "huban_import": "导入订阅", "huban_cancel": "取消", "huban_close": "关闭", "huban_select_node": "选择节点",
    "huban_import_empty": "请先粘贴订阅链接或节点分享链接。",
    "huban_import_invalid": "请输入包含有效服务器地址的完整订阅链接。",
    "huban_import_failed": "没有导入节点，请检查链接、网络或订阅格式后重试。",
    "huban_mode_failed": "模式切换失败，请重试。", "huban_more": "更多选项",
    "huban_refresh": "更新订阅", "huban_manage_subscriptions": "管理订阅",
    "huban_logs": "连接日志", "huban_about": "关于 HBTCP", "huban_launcher_name": "HBTCP", "huban_customer_service": "Telegram 客服", "huban_customer_service_handle": r"\@HBTCP_bot",
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
        (directory / "huban_strings.xml").write_text("\n".join(lines) + "\n")
        original = directory / "strings.xml"
        if original.exists():
            text = original.read_text()
            text = re.sub(r'(<string name="app_name"[^>]*>).*?(</string>)', lambda m: m[1] + "HBTCP" + m[2], text)
            original.write_text(text)

def notices():
    assets = ROOT / "V2rayNG/app/src/main/assets"
    license_text = (ROOT / "branding/LUCIDE-LICENSE.txt").read_text()
    (assets / "HUBAN-THIRD-PARTY-NOTICES.txt").write_text(license_text)
    shutil.copy2(ROOT / "LICENSE", assets / "GPL-3.0.txt")

if __name__ == "__main__":
    logo_vector()
    # Lucide icon geometry (ISC); see branding/NOTICE.md for attribution.
    icon("huban_power", ["M12,2L12,12", "M18.36,5.64A9,9 0,1 1,5.64,5.64"])
    icon("huban_split", ["M16,3L21,3L21,8", "M8,3L3,3L3,8", "M12,22L12,11L3,3", "M12,11L21,3"])
    icon("huban_globe", ["M22,12A10,10 0,1 1,2,12A10,10 0,1 1,22,12", "M2,12L22,12", "M12,2A19,19 0,0 1,12,22A19,19 0,0 1,12,2"])
    icon("huban_link", ["M10,13a5,5 0,0 0,7.54,.54l3,-3a5,5 0,0 0,-7.07,-7.07l-1.72,1.71", "M14,11a5,5 0,0 0,-7.54,-.54l-3,3a5,5 0,0 0,7.07,7.07l1.71,-1.71"])
    strings()
    notices()
