[app]
title = انتقام الصبار
package.name = cactusrevenge
package.domain = org.cactusrevenge.game
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt
version = 1.0.0
requirements = python3,kivy==2.3.1
orientation = landscape
fullscreen = 1
android.permissions = VIBRATE
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
