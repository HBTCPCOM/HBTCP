# 虎斑 Android 本地验证记录

日期：2026-11-24（America/Edmonton）。

## 1.0.2 启动刷新与界面调整

- 新增启动刷新节流、连接参数比较、取消、旧响应保护和旧版默认规则品牌备注迁移的 JVM 测试。覆盖首次打开、重复生命周期事件、同一请求尚未结束、再次打开、时钟重置、节点显示信息变化、地址 / 端口 / 密钥 / 协议变化、已删除 / 禁用 / 编辑 / 已更新的订阅，以及请求开始前取消。
- Playstore debug 全量单测、Kotlin 编译、debug APK、release APK 和 release lint 通过；四种 ABI 与通用包使用原签名构建。最终结果及 SHA-256 见本机 `dist/release-manifest.json`。
- Android 15 / arm64 release APK 实测：空订阅启动不发请求；导入真实本地 HTTP 订阅；返回主页面时自动拉取；保持原选中节点；参数不变时核心启动次数不增加，真实 VPN HTTP 请求仍到节点 A；服务端把同名节点改到新端口并增删节点后，列表变为 A / C，后台重载后的真实 VPN HTTP 请求到节点 B；HTTP 503 和无效内容均保留旧列表与原连接。证据在 `dist/qa/startup-refresh/report.json`。
- 清空 QA 数据后打开应用，不出现通知许可弹窗；没有为 QA 人工授予通知权限，VPN 仍完成系统授权、建立真实 TUN 通路并正常停止。主 manifest 明确排除 POST_NOTIFICATIONS，普通提醒和流量提醒调用被禁用，系统要求的前台服务通知构造保留。
- 360×800、390×844、412×914 三种普通字体视口：完整显示节点切换提示与底部启动按钮；尝试向上滑动后标题位置不变，没有多余滚动。浅色 / 深色主页面和齿轮菜单均截图检查。证据在 `dist/qa/1.0.2-layout-report.json` 和对应截图。
- 菜单触摸进入与 D-pad 导航检查通过；齿轮菜单不显示高级设置，订阅菜单保留链接 / 二维码 / 剪贴板入口；关于虎斑不显示隐私政策、反馈、开源许可证，客服显示 `@HBTCP_bot`。开源许可文件仍随包保留。
- 原生规则、Geo 数据、四种 ABI 和包名保持 1.0.1 的已验证版本；1.0.1 分流同步记录见下方。

### Not run

- 使用生产订阅、微信 / 抖音客户端及真实远端节点的运行测试：未提供生产测试凭据，自动刷新与改址使用本地可变 HTTP / SOCKS 服务实测。
- Android 12 及以下通知表现、厂商实体手机后台策略、代理模式 / root 模式的本轮通知和重载运行：本轮验证使用 Android 15 / arm64 VPN 模式；没有相应版本或具备应用 su 权限的测试设备。
- TalkBack 逐项朗读和整站全部快捷键遍历：模拟器没有 TalkBack；已检查本轮菜单的可见标签、原生可点击节点及部分键盘 / D-pad 交互。

GitHub 发布另行核验远端提交。连接只读或写入返回 403 时，不把准备好的本地源码说成已上传。

## 1.0.1 网站分流同步

- `curl` 下载线上 `https://hbtcp.com/hbtcp-shadowrocket.conf` 与 `/Users/Cheelix/dev/机场/public/hbtcp-shadowrocket.conf`、仓库 `routing/hbtcp-shadowrocket.conf` 逐字节一致。
- `:app:testPlaystoreDebugUnitTest --tests com.v2ray.ang.handler.HubanRoutingUpgradeTest`：6 项新增测试通过。覆盖前版真实格式、首次默认策略、显式策略保留、顺序 / 启用 / 锁定 / ID / 备注等用户编辑、编码返回失败或抛异常时回滚，以及网站 71 条域名和 8 条局域网 CIDR 的完整对应。
- `:app:testPlaystoreDebugUnitTest`：183 项通过，0 失败、0 跳过；`:app:compilePlaystoreDebugKotlin`、`:app:assemblePlaystoreDebug`、`:app:lintPlaystoreRelease` 通过。
- `bash scripts/build-release.sh -PhubanTestBuildType=release :app:assemblePlaystoreReleaseAndroidTest :app:lintPlaystoreRelease`：四种 ABI 和通用 release APK 以及独立设备测试 APK 构建成功。`hubanTestBuildType=release` 时 AGP 仅生成 release 测试任务，debug 单元测试单独以默认参数执行。
- 五份新发布 APK 的签名验证通过，证书与 1.0.0 一致；版本号 `1.0.1`、版本码 `4000002`。ZIP 检查确认每个 ABI 的三份原生库、最新分流预设、未改动的全局预设与规则数据均在包内。
- Android 15 / arm64 模拟器真实覆盖安装三组独立场景：先安装已发布的 1.0.0，植入合成设置，再 `adb install -r` 安装 1.0.1。默认规则升级并初始化 `IPIfNonMatch`；自定义规则及 `IPOnDemand` 保留；全局规则、模式标记及 `AsIs` 保留。三组均通过，证据在 `dist/qa/routing-upgrade/upgrade-report.json` 和各 instrumentation 日志。
- 从安装后的 release 应用调用真实 `CoreConfigManager.getV2rayConfig`，导出 `split-config.json`、`global-config.json` 和 `custom-config.json`。分流最终顺序：内部 domestic-dns 直连 → 局域网域名 → AI / 流媒体代理域名 → 国内平台域名 → 局域网 IP → 大陆 IP → 内部 dns-module 代理。第一出站为 `proxy`，承担普通未匹配连接的兜底；没有无条件规则提前终止 `IPIfNonMatch`。全局的 UDP 443 阻断、局域网规则、全端口代理规则保持原样。
- 用与 AAR 相同提交的 Xray 26.11.9 加载实际生成的配置和从新 APK 提取的三份 Geo 数据。仅注入固定 DNS 应答、无行为影响的规则标记并关闭宿主监听器；46 项真实路由引擎判定通过。微信 / 小红书资源、抖音 TCP 和 UDP 443 视频、B 站视频直连；`claude.com` / `claudeusercontent.com` / `claude.ai` 走代理；Claude 即使对应大陆 IP 仍优先走代理；未知域名解析为大陆 IP 后直连；其他 IPv4 / IPv6 与未知域名默认走代理；后缀边界与局域网通过。全局模式同组用例按原有行为通过。证据在 `dist/qa/routing-upgrade/xray-rule-hits.json`。
- 1.0.1 release 分流模式还完成 Android VPN 系统授权 → TUN → HEV → Xray → 本地 SOCKS 测试节点 → HTTP 回显 `HUBAN_VPN_OK_NODE_A` 的真实数据通路，随后停止并强制重开，模式与合成节点保留。证据在 `dist/qa/routing-vpn-smoke.json`。

上述域名命中使用确定的 DNS 测试数据，不代表已登录微信、小红书或在真实抖音客户端播放视频。生产订阅跨网和实体手机检查仍列于下方 `Not run`。

## 1.0.0 基线已执行

- `:app:testPlaystoreDebugUnitTest`：通过，包括新增的空输入、无效 URL、节点分享链接、原始 JSON 与 Base64 输入边界测试，以及上游已有单元测试。
- `:app:compilePlaystoreDebugKotlin`：通过。
- `:app:assemblePlaystoreDebug`：通过。
- `:app:lintPlaystoreRelease`：通过。
- `:app:assemblePlaystoreRelease`：通过，使用独立本地发布密钥签名。
- `apksigner verify --verbose --print-certs`：release APK 签名验证通过。
- 对 APK ZIP 逐一检查：arm64-v8a、armeabi-v7a、x86、x86_64 均含 `libgojni.so`、`libhev-socks5-tunnel.so` 和 `libhevsockstun.so`。通用包包含全部四个 ABI。
- `geoip.dat`、`geosite.dat` 和原生 AAR 的 SHA-256 与固定下载来源一致；规则数据随 APK 打包。
- `scripts/bootstrap.py`、发布脚本及测试脚本做了语法和本机执行检查。
- CameraX 扫码界面已在模拟器打开；从安卓系统图片选择器选择合成二维码后，真实 ZXing 解码并成功导入对应订阅。证据见 `dist/qa/qr-report.json`。
- 对本地测试 URL 做安卓剪贴板复制 / 粘贴回环校验，再通过首页「从剪贴板导入」成功导入新订阅。证据见 `dist/qa/clipboard-report.json`。

## Android 模拟器真实数据路径

设备为 Android 15 / arm64 模拟器。测试对安装后的 release APK 操作，没有替换客户端的网络栈，也没有在 UI 中注入连接成功状态。

1. 打开虎斑首页，提交空订阅输入，确认显示可操作的错误提示。
2. 在软键盘保持打开时输入本地测试订阅 URL，并完成导入。
3. 从 HTTP 订阅返回两条 Base64 编码的 SOCKS 节点，确认列表与选中节点显示正确。
4. 切换全局模式，通过 Android 系统 VPN 授权启动连接。
5. 由安卓系统 shell 发起独立 HTTP 请求。流量经过 Android VPN TUN → HEV → Xray → 测试 SOCKS 节点 A，得到 `HUBAN_VPN_OK_NODE_A`。
6. 保持连接，在节点列表直接点击 B。客户端自动重载，再次发起 HTTP 请求，得到 `HUBAN_VPN_OK_NODE_B`。
7. 点击断开，确认 daemon 状态回到未连接。
8. 强制停止并重开应用，确认节点 B 与全局模式从本机存储恢复。

证据在本机 `dist/qa/network-report.json`、`dist/qa/vpn-response-A.txt`、`dist/qa/vpn-response-B.txt` 和对应模拟器截图。测试订阅及 SOCKS 服务只绑定本机回环地址，不是内置的生产代理服务。

## Not run

- 使用用户真实订阅和远端生产节点的跨网验证：尚未提供真实订阅或测试凭据。
- 各品牌实体安卓手机、其他 Android 版本与其他 CPU 架构的运行检查：本机只有上述 arm64 模拟器；其他架构已构建并检查原生打包内容。
- TalkBack 逐项朗读、完整 D-pad 导航和厂商后台保活行为：本模拟器未安装 TalkBack，且不代表实体设备的系统定制。
- 真实相机对实体二维码的光学扫描：没有实体相机设备。应用保留 CameraX / ZXing 原生扫描和相册识码实现，上游对应 JVM 测试已随单元测试执行。

上游既有的 Kotlin / Gradle 弃用警告仍存在，未为此次客户端定制改写无关模块。安装包没有内置测试订阅、用户凭据或签名私钥。
