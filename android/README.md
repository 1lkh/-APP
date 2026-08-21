# 动得对 Android

这是一个轻量 Android WebView 壳，加载线上 `https://dgdlkj.top`，与网页端共用同一套界面和动作数据。

## 构建 APK

在项目根目录执行：

```bash
./android/build-apk.sh
```

输出文件：`android/build/动得对-debug.apk`

这是用于内测和安装验证的 debug 签名 APK。正式上架 Google Play 或国产应用市场前，需要使用独立的 release keystore、隐私政策、应用图标和商店素材重新签名。
