# HBTCP 客户端

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

本次安卓源码来自本地提交 `4da92460ecc362b86b41388e322b29b7008ae507`；构建输入及原生子模块版本固定在 `android/build-inputs.json` 和 Git 子模块中。
