[app]
title = Circuit Merge
package.name = circuitmerge
package.domain = fr.alexisjouin
source.dir = .
source.include_exts = py,png,jpg,ttf,otf,wav,ogg,json
source.exclude_dirs = tests,test-wheels,docs,experiences,atelier_nsi,android,.git,.github,bin,.buildozer
version = 0.2.0
requirements = python3,pygame,pymunk,cffi,android
orientation = portrait
fullscreen = 1
android.api = 36
android.minapi = 26
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True
android.debug_artifact = apk
android.release_artifact = aab
p4a.bootstrap = sdl2
p4a.local_recipes = ./android/recipes
p4a.branch = develop
p4a.commit = 8ef9d1dbbf769d2c14681dbc3c116c85e2e93bae
[buildozer]
log_level = 2
warn_on_root = 1
