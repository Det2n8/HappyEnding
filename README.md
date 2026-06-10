# HappyEnding Kodi Repo

GitHub-ready Kodi repository for your custom HappyEnding build.

## Add-ons included

- `plugin.video.happyending`: custom video add-on framework with provider modules, visible thumbnails, custom length sorting, and view shortcuts.
- `repository.happyending`: repository installer.
- `skin.happyending.sidepreview`: experimental Kodi 21 Omega skin with a left list and large right thumbnail.
- `script.module.happyending`: helper module for thumbnail fallbacks and custom length filtering/sorting.

## What this gives you

- Your own Kodi video add-on shell so you are not editing another add-on directly.
- More visible thumbnail fields: `thumb`, `poster`, `icon`, `fanart`.
- Custom length presets and custom min/max seconds.
- A side-preview skin layout: list on the left, big thumbnail on the right, mini info underneath.

## Install order for local testing

1. Install `script.module.happyending`.
2. Install `skin.happyending.sidepreview`.
3. Install `plugin.video.happyending`.
4. Optional: install `repository.happyending` after uploading to GitHub.

## GitHub repo name

Recommended repo name: `happyending-repo` under your GitHub account `det2n8`.

Install zip after upload:

`zips/repository.happyending/repository.happyending-1.0.0.zip`
