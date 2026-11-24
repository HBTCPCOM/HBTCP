# HBTCP Android

HBTCP 安卓客户端，支持 Android 7.0 及以上版本。

[下载 APK](https://github.com/HUBANTCP/HBTCP/releases/latest/download/HBTCP-Android.apk) · [版本记录](https://github.com/HUBANTCP/HBTCP/releases) · [官网](https://hbtcp.com)

## 功能

- 分流模式：局域网、国内平台域名和大陆 IP 直连；明确的海外代理域名和其他流量使用所选节点。
- 全局模式：局域网之外的流量使用所选节点。
- 导入 HTTP(S) 订阅、Base64 节点列表、分享链接与 Xray JSON；支持扫码和剪贴板。
- 连接中选择新节点即可切换，无需手动停止再启动。
- 打开或返回 App 时刷新已保存的订阅 URL；刷新失败时保留已有节点与连接。10 秒内重复进入不会重复请求。
- 服务端修改所选节点的连接参数后，刷新成功会重载正在运行的连接；闲置时不会自行启动 VPN。
- Telegram 客服：[@HBTCP_bot](https://t.me/HBTCP_bot)。

不内置生产订阅或账号。请导入有效订阅；Clash YAML 请改用服务商提供的通用 / v2ray 订阅。

## 源码结构

- `V2rayNG/`：Android 工程，首页为 `ui/main/HubanScreen.kt`。
- `AndroidLibXrayLite/`、`hev-socks5-tunnel/`：固定版本的原生核心子模块。
- `routing/`：内置分流规则及网站规则快照。
- `branding/`：应用图标及授权说明。
- `build-inputs.json`：构建依赖版本与校验值。
- `scripts/`：依赖准备、签名、构建及开发辅助脚本。

## 构建

从多平台仓库获取源码时，先进入 `android/` 目录。准备 Android SDK、NDK 与适用的 JDK；版本见 Gradle 配置、wrapper 和 `build-inputs.json`。

```sh
python3 scripts/bootstrap.py
python3 scripts/create-local-signing.py
bash scripts/build-release.sh
```

安装包输出到 `dist/`。`bootstrap.py` 按固定版本获取并校验依赖，必要时从子模块编译 HEV。可通过 `ANDROID_HOME`、`NDK_HOME` 和 `JAVA_HOME` 指定工具路径。

发布签名存放在仓库外；后续覆盖安装须使用同一份签名。可通过 `HUBAN_SIGNING_PROPERTIES` 指定已有签名配置，包含 `storeFile`、`storePassword`、`keyAlias`、`keyPassword`。

## 分流规则

内置规则适配自 [HBTCP Shadowrocket 配置](https://hbtcp.com/hbtcp-shadowrocket.conf)。顺序为：局域网域名 → 明确代理域名 → 国内直连域名 → 局域网 IP → 大陆 IP → 默认节点。域名策略为 `IPIfNonMatch`，网站更新通过新版 APK 同步。

升级仅迁移未修改过的内置默认规则，保留用户主动修改的配置和全局模式。

## 第三方许可

连接底座基于 [v2rayNG](https://github.com/2dust/v2rayNG)，遵循 [GPL-3.0](LICENSE)。原生核心与依赖的许可证随源码和安装包保留；完整第三方文本见 `V2rayNG/app/src/main/assets/THIRD-PARTY-LICENSES.txt`，图标说明见 `branding/NOTICE.md`。
