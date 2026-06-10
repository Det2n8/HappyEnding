# HappyEnding

A Kodi video add-on framework built for your specs:

- Left list + large right thumbnail when used with `skin.happyending.sidepreview`.
- Custom length presets and custom min/max length settings.
- Long-first, short-first, or source-order sorting.
- Forced artwork fields so skins can show `thumb`, `poster`, `icon`, and `fanart`.
- Provider module system so you can add your own allowed sites.

## Important

This zip is a framework. It does not include media sites by default. Add provider
modules only for sites you are allowed to use, and do not bypass restrictions.

## Add a site

1. Copy `resources/lib/sources/template_provider.py`.
2. Rename it, for example `my_site.py`.
3. Return `VideoEntry(...)` objects from `list_videos()` and `search()`.
4. Register the provider in `resources/lib/provider_loader.py`.

## Best thumbnail behaviour

For every item, set at least `thumb`. The add-on will copy the best available
image to `thumb`, `poster`, `icon`, and `fanart` so the skin has something to show.

## Exact second presets

The bundled add-on supports exact custom ranges, including 10 seconds to 4:59, 5:00 to 9:59, 10:00 to 19:59, and 20:00+.
