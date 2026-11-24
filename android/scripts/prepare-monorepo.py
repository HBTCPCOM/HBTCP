#!/usr/bin/env python3
"""Prepare the public multi-platform checkout from committed Android source; never uploads credentials or build artifacts."""
from pathlib import Path
import io
import re
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT.parent / "HBTCP"
REMOTE = "https://github.com/HBTCPCOM/HBTCP.git"

def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd)

if git("status", "--porcelain").strip():
    raise SystemExit("Commit the reviewed Android source before preparing its published snapshot.")
if DEST.exists():
    raise SystemExit(f"Destination already exists; inspect it before changing it: {DEST}")
git("clone", REMOTE, str(DEST), cwd=ROOT.parent)
git("checkout", "-b", "codex/initial-client", cwd=DEST)
android = DEST / "android"
android.mkdir()
with tarfile.open(fileobj=io.BytesIO(git("archive", "HEAD"))) as archive:
    # AI tool instructions are development context, not application source or build inputs.
    members = [m for m in archive.getmembers() if Path(m.name).name not in {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "copilot-instructions.md", "VALIDATION.md"}]
    archive.extractall(android, members=members, filter="data")
modules = (android / ".gitmodules").read_text()
(DEST / ".gitmodules").write_text(re.sub(r"(?m)^(\s*path\s*=\s*)(.+)$", r"\1android/\2", modules))
(android / ".gitmodules").unlink()
(DEST / ".gitignore").write_text(".DS_Store\n.finesse/\n")
readme = """# HBTCP

HBTCP 客户端的多平台源码仓库。

[![下载 Android APK](https://img.shields.io/badge/Android-下载_HBTCP_APK-874009?style=for-the-badge&logo=android&logoColor=white)](https://github.com/HBTCPCOM/HBTCP/releases/latest/download/HBTCP-Android.apk)

[全部安装包与版本记录](https://github.com/HBTCPCOM/HBTCP/releases) · [HBTCP 官网](https://hbtcp.com)

## Android

- 分流 / 全局模式，一键启动与切换节点。
- 支持订阅链接、扫码和剪贴板导入。
- 打开 App 时刷新订阅，自动同步服务端节点变更。
- 内置国内直连与海外代理分流规则。
- Telegram 客服：[@HBTCP_bot](https://t.me/HBTCP_bot)。

通用 APK 适合大多数安卓设备；按处理器架构区分的精简安装包可在版本页面下载。

## 源码

| 平台 | 目录 | 说明 |
| --- | --- | --- |
| Android | [android/](android/README-HBTCP.md) | Kotlin / Jetpack Compose 原生客户端 |

其他平台后续按独立目录加入。安卓构建说明见 [android/README-HBTCP.md](android/README-HBTCP.md)。
"""
if (DEST / "README.md").exists():
    raise SystemExit("Remote already has a README; preserve and merge it manually before publication.")
(DEST / "README.md").write_text(readme)
git("add", "README.md", ".gitignore", ".gitmodules", cwd=DEST)
# The archive contains only reviewed tracked source; retain the tracked Gradle wrapper despite *.jar ignores.
git("add", "-f", "android", cwd=DEST)
for record in git("ls-tree", "-z", "HEAD").split(b"\0"):
    if not record: continue
    metadata, name = record.split(b"\t", 1)
    mode, kind, sha = metadata.decode().split()
    if mode == "160000":
        git("update-index", "--add", "--cacheinfo", f"160000,{sha},android/{name.decode()}", cwd=DEST)
print(DEST)
print("Prepared reviewed source and pinned native gitlinks. Commit and push only after checking the staged files.")
