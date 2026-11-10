[app]
title = FLEX DLS Bot
package.name = flexdls
package.domain = org.flex
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0
requirements = python3,kivy==2.3.0,pyjnius,android,adb-shell,rsa,pyasn1,pillow,requests,certifi,urllib3,idna,charset-normalizer
orientation = portrait
fullscreen = 0
services = Bot:service.py:foreground
android.permissions = INTERNET,FOREGROUND_SERVICE,WAKE_LOCK,POST_NOTIFICATIONS
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
