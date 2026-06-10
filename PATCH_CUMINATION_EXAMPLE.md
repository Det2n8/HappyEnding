# CumiNation patch example: thumbnails + custom length sorting

This repo gives you two things:

1. `skin.happyending.sidepreview`: a skin/view layout.
2. `script.module.happyending`: helper functions for HappyEnding-style video listings.

The helper module must be imported inside the actual HappyEnding add-on code. Kodi skins can display fields, but the video add-on must supply those fields first.

## 1. Add the module dependency to HappyEnding `addon.xml`

Inside `<requires>` add:

```xml
<import addon="script.module.happyending" version="1.0.0"/>
```

## 2. Patch the listing function

Where HappyEnding builds each video item, use this pattern.

```python
from happyending import (
    parse_duration_to_seconds,
    should_keep_item,
    apply_art,
    set_video_duration,
    add_standard_sort_methods,
    maybe_set_sidepreview_view,
)

# Example variables from scraper/listing code:
# title, url, thumb, poster, fanart, plot, duration

seconds = parse_duration_to_seconds(duration) or parse_duration_to_seconds(plot)

# Skip items outside your custom min/max range from settings.
if not should_keep_item(title=title, duration=seconds, plot=plot):
    continue

li = xbmcgui.ListItem(label=title, path=url)
li.setProperty('IsPlayable', 'true')

# Modern Kodi-safe duration metadata, with fallback.
set_video_duration(li, seconds)

# Make thumbnails visible in more skins: thumb/poster/icon/fanart.
apply_art(li, thumb=thumb, poster=poster, fanart=fanart, icon=thumb)

# Optional old-style info fallback.
try:
    li.setInfo('video', {'title': title, 'plot': plot, 'duration': seconds, 'mediatype': 'video'})
except Exception:
    pass

xbmcplugin.addDirectoryItem(handle, url, li, isFolder=False)

# After adding all items:
add_standard_sort_methods(handle)
maybe_set_sidepreview_view()
xbmcplugin.endOfDirectory(handle)
```

## 3. For true custom sort before display

If the site returns entries as dictionaries before `ListItem` objects are created, sort them before building list items:

```python
from happyending import filter_and_sort_entries

entries = filter_and_sort_entries(entries)
for entry in entries:
    # build ListItem here
    pass
```

Expected keys:

```python
{
    'title': 'Video title',
    'url': 'https://...',
    'thumb': 'https://...',
    'poster': 'https://...',
    'fanart': 'https://...',
    'plot': '...',
    'duration': '01:22:30',
}
```

## Notes

- This cannot create thumbnails if a website does not provide an image and the video stream is not available to Kodi yet. It can only use the best available image or a placeholder.
- Custom length sorting works best when the scraper gets duration before creating the list.
- Kodi native sort by duration only works after the add-on supplies `duration` metadata.


## Alternative: use the new add-on instead of patching CumiNation

This package now includes `plugin.video.happyending`, a clean video add-on framework.
Instead of editing HappyEnding directly, add provider modules under:

```text
plugin.video.happyending/resources/lib/sources/
```

Then register them in:

```text
plugin.video.happyending/resources/lib/provider_loader.py
```

This is safer than modifying another add-on because your view types, thumbnail rules, and length sorting stay inside your own add-on.
