#!/usr/bin/env python3
"""Create a persistent local release identity without writing secrets into the repository."""
from pathlib import Path
import os
import secrets
import subprocess

directory = Path.home() / ".local/share/hbtcp-android/signing"
directory.mkdir(parents=True, exist_ok=True)
directory.chmod(0o700)
properties = directory / "signing.properties"
keystore = directory / "hbtcp-release.jks"
if properties.exists() or keystore.exists():
    if not properties.exists() or not keystore.exists():
        raise SystemExit("Incomplete signing identity; restore both files before rebuilding.")
    print("Existing local release identity retained.")
else:
    password = secrets.token_hex(24)
    environment = {**os.environ, "HBTCP_KEY_PASSWORD": password}
    subprocess.run([
        "keytool", "-genkeypair", "-keystore", str(keystore), "-storetype", "JKS",
        "-alias", "hbtcp-release", "-keyalg", "RSA", "-keysize", "3072", "-validity", "10000",
        "-storepass:env", "HBTCP_KEY_PASSWORD", "-keypass:env", "HBTCP_KEY_PASSWORD",
        "-dname", "CN=HBTCP Android, O=HBTCP, C=CA", "-noprompt"
    ], env=environment, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    properties.write_text(f"storeFile={keystore}\nstorePassword={password}\nkeyAlias=hbtcp-release\nkeyPassword={password}\n")
    properties.chmod(0o600)
    keystore.chmod(0o600)
    print("Created local release identity outside the source repository.")
