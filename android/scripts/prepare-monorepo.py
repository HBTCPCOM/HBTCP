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
REMOTE = "https://github.com/HUBANTCP/HBTCP.git"

def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd)

if git("status", "--porcelain").strip():
    raise SystemExit("Commit the reviewed Android source before preparing its published snapshot.")
if DEST.exists():
    raise SystemExit(f"Destination already exists; inspect it before changing it: {DEST}")
git("clone", REMOTE, str(DEST), cwd=ROOT.parent)
git("checkout", "-b", "codex/initial-client", cwd=DEST)
source_commit = git("rev-parse", "HEAD").decode().strip()
android = DEST / "android"
android.mkdir()
with tarfile.open(fileobj=io.BytesIO(git("archive", "HEAD"))) as archive:
    # AI tool instructions are development context, not application source or build inputs.
    members = [m for m in archive.getmembers() if Path(m.name).name not in {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "copilot-instructions.md"}]
    archive.extractall(android, members=members, filter="data")
modules = (android / ".gitmodules").read_text()
(DEST / ".gitmodules").write_text(re.sub(r"(?m)^(\s*path\s*=\s*)(.+)$", r"\1android/\2", modules))
(android / ".gitmodules").unlink()
(DEST / ".gitignore").write_text(".DS_Store\n.finesse/\n")
readme = f"""# HBTCP 客户端

HBTCP 客户端的多平台源码仓库。每个平台独立组织源码、构建方法和许可证。

## 目录

| 平台 | 目录 | 状态 |
| --- | --- | --- |
| Android | [android/](android/README-HUBAN.md) | 原生客户端 1.0.2 |

其他平台后续按独立目录加入。

## Android

安卓客户端使用 Kotlin / Jetpack Compose、Xray 和 HEV，支持分流 / 全局、导入订阅、选择节点、VPN 连接，以及打开 App 时刷新订阅。

构建方法见 [安卓说明](android/README-HUBAN.md)，测试结果见 [验证记录](android/VALIDATION.md)。运行构建命令前先进入 `android/`。

不内置生产订阅、账号密码、发布签名私钥或测试节点。发布签名应由维护者在仓库外独立管理。

## 许可与来源

安卓客户端基于 [v2rayNG](https://github.com/2dust/v2rayNG)，许可见 [android/LICENSE](android/LICENSE)。Xray、HEV 和其他依赖的许可与归属说明保留在安卓目录及安装包中。

本次安卓源码来自本地提交 `{source_commit}`；构建输入及原生子模块版本固定在 `android/build-inputs.json` 和 Git 子模块中。
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
