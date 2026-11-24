# 安卓规则同步与验证

`hbtcp-shadowrocket.conf` 是本次网站配置快照。`[Rule]` 中 `DOMAIN` 映射 `full:`，`DOMAIN-SUFFIX` 映射 `domain:`；相同出站的连续域名合并到安卓的 `custom_routing_white`，保持条目次序。仅局域网 IP 移到显式域名之后，确保嗅探出 Claude 等域名时，明确代理规则优先于大陆 IP 兜底。最终代理依赖第一条出站，不放无条件规则提前吞掉 `IPIfNonMatch` 的第二轮匹配。旧版完整预设保存在 `hbtcp_routing_white_v1`，用于安全识别可升级的默认值。

重新验证：

```sh
# 在 V2rayNG/ 中，以项目可用 JDK 运行。
./gradlew :app:testPlaystoreDebugUnitTest :app:compilePlaystoreDebugKotlin :app:assemblePlaystoreDebug

# 在仓库根目录构建同发布签名的安装包与独立测试 APK。
bash scripts/build-release.sh -PhbtcpTestBuildType=release :app:assemblePlaystoreReleaseAndroidTest :app:lintPlaystoreRelease
python3 scripts/qa-routing-upgrade.py V2rayNG/app/build/outputs/apk/androidTest/playstore/release/app-playstore-release-androidTest.apk
```

升级脚本只接受 `emulator-5554`，会卸载其虎斑 QA 数据，分别安装已保留的 1.0.0 发布包、种入合成设置，再用 `install -r` 覆盖到 1.0.1，验证默认、自定义、全局三类用户。脚本导出的配置只包含本地测试 SOCKS 节点，不包含生产凭据。

从新 APK 提取 `assets/geoip.dat`、`assets/geosite.dat` 和 `assets/geoip-only-cn-private.dat` 到 `dist/qa/routing-assets/`。在 `scripts/qa-routing/` 中运行：

```sh
go run . ../../dist/qa/routing-upgrade ../../dist/qa/routing-assets
```

该工具的 Xray 依赖固定为 AndroidLibXrayLite 使用的相同提交。它加载安装后实际生成的完整配置，仅移除宿主监听器、注入确定的 DNS 应答及无行为影响的规则名称，使用 Xray 自己的路由器执行 46 次判定，覆盖 TCP / UDP、国内资源域名、Claude 域名优先于大陆 IP、IPv4 / IPv6、DNS 后大陆 IP 判断、后缀边界、局域网和全局模式。输出 `xray-rule-hits.json`。这验证路由决策，不代表微信登录或抖音客户端播放的生产网络实测。
