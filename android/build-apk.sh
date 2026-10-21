#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ANDROID_DIR="$ROOT_DIR/android"
SDK_DIR="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
BUILD_TOOLS="$SDK_DIR/build-tools/35.0.0"
PLATFORM="$SDK_DIR/platforms/android-35/android.jar"
JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk@17}"
export JAVA_HOME
export PATH="$JAVA_HOME/bin:$PATH"

if [[ ! -x "$BUILD_TOOLS/aapt2" || ! -f "$PLATFORM" ]]; then
  echo "Android SDK platform/build-tools are missing." >&2
  exit 1
fi

OUT="$ANDROID_DIR/build"
rm -rf "$OUT"
mkdir -p "$OUT/classes" "$OUT/res" "$OUT/generated" "$OUT/dex"

"$BUILD_TOOLS/aapt2" compile --dir "$ANDROID_DIR/app/src/main/res" -o "$OUT/res.zip"
"$BUILD_TOOLS/aapt2" link \
  -I "$PLATFORM" \
  --manifest "$ANDROID_DIR/app/src/main/AndroidManifest.xml" \
  --java "$OUT/generated" \
  --auto-add-overlay \
  -o "$OUT/app-unsigned.apk" \
  "$OUT/res.zip"

"$JAVA_HOME/bin/javac" -source 17 -target 17 \
  -classpath "$PLATFORM" \
  -d "$OUT/classes" \
  "$ANDROID_DIR/app/src/main/java/top/dgdlkj/dongdui/MainActivity.java"

"$BUILD_TOOLS/d8" --lib "$PLATFORM" --output "$OUT/dex" "$OUT/classes/top/dgdlkj/dongdui/MainActivity.class"
cp "$OUT/dex/classes.dex" "$OUT/classes.dex"
"$JAVA_HOME/bin/jar" uf "$OUT/app-unsigned.apk" -C "$OUT" classes.dex

KEYSTORE="$OUT/debug.keystore"
if [[ ! -f "$KEYSTORE" ]]; then
  "$JAVA_HOME/bin/keytool" -genkeypair -v \
    -keystore "$KEYSTORE" \
    -storepass android \
    -alias androiddebugkey \
    -keypass android \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -dname "CN=Android Debug,O=Android,C=US" >/dev/null 2>&1
fi

"$BUILD_TOOLS/zipalign" -f 4 "$OUT/app-unsigned.apk" "$OUT/FORMA-unsigned-aligned.apk"
"$BUILD_TOOLS/apksigner" sign \
  --ks "$KEYSTORE" \
  --ks-pass pass:android \
  --ks-key-alias androiddebugkey \
  --key-pass pass:android \
  --out "$OUT/FORMA-debug.apk" \
  "$OUT/FORMA-unsigned-aligned.apk"
"$BUILD_TOOLS/apksigner" verify --verbose "$OUT/FORMA-debug.apk"
echo "Built: $OUT/FORMA-debug.apk"
