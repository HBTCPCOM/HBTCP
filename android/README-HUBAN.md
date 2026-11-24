# HBTCP Android

HBTCP 是一个原生 Android 代理客户端，首页沿用已确认的虎斑老虎纸飞机标志、橘色和奶油色设计。应用使用 Kotlin / Jetpack Compose，连接基础来自 v2rayNG、Xray 和 HEV SOCKS5 Tunnel；不是网页封装。

## 安装

本机安装包在 `dist/`：

- `HBTCP-1.0.2-arm64-v8a.apk`：大多数现代安卓手机使用这个版本。
- `HBTCP-1.0.2-universal.apk`：包含全部四种 CPU 架构。
- 同时提供 `armeabi-v7a`、`x86`、`x86_64` 的单独版本。

包名为 `com.huban.client`，可以与原版 v2rayNG 同时安装。APK 是本地独立密钥签名的 release 版本。兼容范围由 `V2rayNG/app/build.gradle.kts` 的 `minSdk` 与打包架构决定。

首次点击启动时，需要在 Android 的系统弹窗中授权创建 VPN。应用不申请通知权限，不发送可选提醒。Android 要求 VPN 使用前台服务；Android 13 及以上未授权通知时，系统仍可在运行中的应用管理器显示服务状态。Android 12 及以下仍需保留系统要求的前台服务通知。

## 功能

- 分流：国内与局域网直连，其余流量使用所选节点。
- 全局：除局域网外，流量使用所选节点。
- 导入 HTTP(S) 订阅 URL、Base64 节点列表、节点分享链接与 Xray JSON 配置。
- 支持的节点协议沿用当前 Xray / v2rayNG 解析器，包括 VLESS、VMess、Trojan、Shadowsocks、SOCKS、HTTP、WireGuard、Hysteria2 等。
- 相机扫码与剪贴板导入都调用安卓原生功能。
- 订阅、节点与模式保存在本机；相同 URL 再次导入会更新现有订阅。
- 连接中选择新节点后，客户端自动重载连接，不需要手动停止、再启动。核心重载可能重建现有连接，不承诺保持每条 TCP 会话。
- 右上角齿轮菜单提供订阅更新、订阅管理、连接日志和关于虎斑。
- 关于虎斑保留源代码、翻译贡献者、Telegram 客服和版本；客服为 `@HBTCP_bot`，源代码链接指向 `https://github.com/HUBANTCP/HBTCP`。
- 已随 APK 打包国内分流规则数据，首次启动无需另外下载规则文件。

本应用不附赠代理服务器或付费订阅。请导入你自己的有效订阅。Clash YAML 不是本版的直接导入格式；使用服务商的 v2ray / 通用订阅地址。

## 1.0.2 打开 App 时刷新订阅

应用内品牌文字、系统名称、桌面名称和安装包名称统一为 HBTCP；保留原来的老虎与纸飞机图形。包名和发布签名保持不变，可以覆盖旧版本。用户订阅和节点自己的名字保持原样。

打开或返回主页面时，客户端在后台读取已保存的订阅 URL；10 秒内重复进入或刷新尚未结束时不会重复请求。此功能不新建后台定时任务，用户原先手动设置的周期更新保持原设置。单条节点分享链接、Base64 列表和原始 JSON 没有订阅 URL，需要重新导入后才能收到变更。

刷新成功后替换节点列表，并通过原有匹配机制保留当前选择；被删除的节点会选择合适的替代项。所选节点的连接参数未变化时保持现有连接；地址、端口、协议等实际参数变化时，通过 daemon 命令重载正在运行的连接，不会替用户启动闲置 VPN。HTTP 失败、空或无效响应保留已有节点；请求期间订阅被删除、禁用、编辑或已完成更新时，旧响应不再发布。

首页压缩顶部与区块间距，保留按钮尺寸；已验证 360×800、390×844、412×914 视口无需滚动即可显示底部提示。小屏或大字体仍可滚动，不裁掉内容。

多平台仓库目标为 [HUBANTCP/HBTCP](https://github.com/HUBANTCP/HBTCP)，安卓源码使用 `android/` 目录。`scripts/prepare-monorepo.py` 会从干净、已提交的本地安卓版本准备多平台仓库，保留固定版本的原生子模块；不打包签名配置、生成的二进制、测试数据或本地 AI 工具说明。

## 1.0.1 分流规则

内置分流与 2026-11-24 网站的 [Shadowrocket 配置](https://hbtcp.com/hbtcp-shadowrocket.conf) 对齐；原始快照在 `routing/hbtcp-shadowrocket.conf`。仅适配 `[Rule]`，安卓已有的 DNS、VPN 和全局模式保持原有机制。71 条显式域名规则映射为 Xray 的 `full:` 精确匹配和 `domain:` 后缀匹配：局域网域名 2 条、AI / 流媒体代理 14 条、国内平台及 `.cn` 直连 55 条。原有 `geosite:private`、`geoip:private` 与网站中的全部 8 条局域网 CIDR 一并保留。

普通连接的顺序是：局域网域名 → 明确代理域名 → 国内直连域名 → 局域网 IP → 大陆 IP → 默认所选节点。DNS 模块自己的入站规则由原有构建器插入。默认域名策略为 `IPIfNonMatch`；不添加匹配所有端口或网络的末尾规则，以免第一轮匹配提前结束、跳过域名解析后的大陆 IP 判断。Xray 第一条出站为 `proxy`，承担最终兜底。分流模式取消旧预设最前面的 UDP 443 拦截，抖音等明确直连域名的 QUIC 流量也可直连；全局预设文件完全不变。

覆盖安装使用原发布签名，版本码升为 `4000002`。程序在后台初始化资源或生成配置前，对比 1.0.0 完整默认规则；仅未修改过的默认预设自动更新。用户修改的顺序、启用状态、锁定、ID、备注与内容均保留，全局模式不迁移。只有未保存过域名策略的默认预设才初始化为 `IPIfNonMatch`，用户主动保存的 `AsIs` / `IPOnDemand` 等设置继续生效。写入失败会回滚并阻止使用半更新的配置；重复执行迁移不会重复添加规则。用户主动点击模式或重置预设按钮仍沿用原先的重置行为。

规则是随 APK 发布的快照，网站后续修改需要重新同步、验证和发版。

## 本地源码

- `V2rayNG/`：Android 工程，包含原有连接、订阅和相机能力。
- `V2rayNG/app/src/main/java/com/v2ray/ang/ui/main/HubanScreen.kt`：虎斑首页。
- `MainAction`、`MainViewModel`、`MainRepository`：首页操作、状态与持久化。
- `AndroidLibXrayLite/`：与 AAR 对应的原生核心源码子模块。
- `hev-socks5-tunnel/`：VPN TUN 与 SOCKS 之间的数据转发实现。
- `branding/`：用户提供的原始虎斑标志和图标授权说明。
- `build-inputs.json`：原始仓库提交、核心版本、规则版本和校验值。
- `scripts/`：依赖准备、发布构建、签名初始化和本地网络验证脚本。
- `VALIDATION.md`：本次实际验证结果及未运行的检查。

源码已在本地独立 Git 仓库中。多平台发布目标已确定为 `HUBANTCP/HBTCP`；本地安卓工程仍独立保留，发布准备目录为 `/Users/Cheelix/dev/HBTCP`。

## 重新构建

Android、Kotlin、Gradle 和依赖的配置见工程内 `build.gradle.kts`、`gradle/libs.versions.toml`、Gradle wrapper 与 `build-inputs.json`。本机已经准备好需要的工具和本地依赖。

新机器首次获取源码后运行：

```sh
python3 scripts/bootstrap.py
python3 scripts/create-local-signing.py
bash scripts/build-release.sh
```

`bootstrap.py` 会按固定版本下载 AAR 与分流规则，验证 SHA-256，并在需要时从子模块源码编译 HEV 库。Android SDK、NDK 和可用的 JDK 需先安装；可用 `ANDROID_HOME`、`NDK_HOME`、`JAVA_HOME` 指定路径。

签名配置和私钥保存在项目目录之外：`~/.local/share/huban-android/signing/`。备份这整个目录，后续更新版本继续用同一份签名。密钥、密码、用户订阅和构建产物均不上传 Git。

可以通过 `HUBAN_SIGNING_PROPERTIES` 指定已有签名配置文件。文件包含 `storeFile`、`storePassword`、`keyAlias`、`keyPassword` 四个字段。

## 验证与来源

```sh
cd V2rayNG
./gradlew :app:testPlaystoreDebugUnitTest :app:compilePlaystoreDebugKotlin :app:assemblePlaystoreDebug
```

本地网络验证先运行 `python3 scripts/qa-network-fixture.py`，再对已安装的 APK 运行 `python3 scripts/qa-emulator.py`。脚本只使用临时本地测试订阅，不包含生产服务凭据。

上游项目：[v2rayNG](https://github.com/2dust/v2rayNG)、[AndroidLibXrayLite](https://github.com/2dust/AndroidLibXrayLite)、[Xray-core](https://github.com/XTLS/Xray-core)、[HEV SOCKS5 Tunnel](https://github.com/heiher/hev-socks5-tunnel)、[分流数据](https://github.com/Loyalsoldier/v2ray-rules-dat)。v2rayN 的桌面机制参照来源为 [v2rayN](https://github.com/2dust/v2rayN)。

保留上游 GPL-3.0 许可、作者和原生子模块许可。虎斑修改随本仓库提供完整对应源码。图标说明见 `branding/NOTICE.md`。
