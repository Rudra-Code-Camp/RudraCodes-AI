[app]
title = RudraCodes AI
package.name = rudracodesai
package.domain = com.rudracodes
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,urllib3
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
