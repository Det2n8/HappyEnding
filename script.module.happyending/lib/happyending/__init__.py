# HappyEnding Tools
# Helper functions for Kodi video add-ons. Python 3 / Kodi 19+.
# This module does not scrape or bypass content. It only improves metadata handling
# for items that a video add-on already lists legitimately.

import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
except Exception:  # Allows unit testing outside Kodi.
    xbmc = xbmcaddon = xbmcgui = xbmcplugin = None

_DURATION_PATTERNS = [
    re.compile(r'(?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?!\d)'),  # hh:mm:ss or mm:ss
    re.compile(r'(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours)\b', re.I),
    re.compile(r'(\d+(?:\.\d+)?)\s*(m|min|mins|minute|minutes)\b', re.I),
    re.compile(r'(\d+(?:\.\d+)?)\s*(s|sec|secs|second|seconds)\b', re.I),
]

def addon_setting(key: str, default: str = '') -> str:
    if xbmcaddon is None:
        return default
    try:
        return xbmcaddon.Addon('script.module.happyending').getSetting(key) or default
    except Exception:
        return default

def parse_duration_to_seconds(value: Any) -> int:
    """Parse seconds, mm:ss, hh:mm:ss, or text like '1h 20m 05s'."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return max(0, int(value))
    text = str(value).strip()
    if not text:
        return 0
    if text.isdigit():
        # If a site gives raw seconds, keep it as seconds.
        return int(text)

    # 01:20:05 or 20:05
    m = _DURATION_PATTERNS[0].search(text)
    if m:
        first, second, third = m.groups()
        if first is None:
            return int(second) * 60 + int(third)
        return int(first) * 3600 + int(second) * 60 + int(third)

    total = 0.0
    for num, unit in re.findall(r'(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)\b', text, re.I):
        n = float(num)
        u = unit.lower()
        if u.startswith('h'):
            total += n * 3600
        elif u.startswith('m'):
            total += n * 60
        else:
            total += n
    return int(total)

def duration_from_text(*parts: Any) -> int:
    """Search title/plot/metadata text for a duration and return seconds."""
    for part in parts:
        seconds = parse_duration_to_seconds(part)
        if seconds:
            return seconds
    return 0

def length_filter_enabled() -> bool:
    return addon_setting('enable_length_filter', 'false').lower() == 'true'

def _int_setting(key: str, default: int = 0) -> int:
    try:
        return int(addon_setting(key, str(default)) or default)
    except ValueError:
        return default

def configured_range_seconds() -> Tuple[int, Optional[int]]:
    min_seconds = _int_setting('min_minutes', 0) * 60 + _int_setting('min_extra_seconds', 0)
    max_seconds = _int_setting('max_minutes', 0) * 60 + _int_setting('max_extra_seconds', 0)
    return max(0, min_seconds), (max_seconds if max_seconds > 0 else None)

def in_configured_length_range(seconds: int) -> bool:
    if not length_filter_enabled():
        return True
    low, high = configured_range_seconds()
    if seconds < low:
        return False
    if high is not None and seconds > high:
        return False
    return True

def should_keep_item(title: str = '', duration: Any = None, plot: str = '') -> bool:
    seconds = parse_duration_to_seconds(duration) or duration_from_text(title, plot)
    return in_configured_length_range(seconds)

def sort_entries_by_duration(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort dictionaries that contain duration/length/title/plot keys."""
    direction = addon_setting('sort_direction', 'long_first')
    if direction == 'none':
        return entries
    def key(entry):
        return parse_duration_to_seconds(entry.get('duration') or entry.get('length')) or duration_from_text(entry.get('title'), entry.get('plot'))
    return sorted(entries, key=key, reverse=(direction == 'long_first'))

def filter_and_sort_entries(entries: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    kept = []
    for entry in entries:
        seconds = parse_duration_to_seconds(entry.get('duration') or entry.get('length')) or duration_from_text(entry.get('title'), entry.get('plot'))
        entry['duration_seconds'] = seconds
        if in_configured_length_range(seconds):
            kept.append(entry)
    return sort_entries_by_duration(kept)

def best_art(primary: str = '', fallback: str = '') -> str:
    return primary or fallback or addon_setting('placeholder_art', '')

def apply_art(listitem: Any, thumb: str = '', poster: str = '', fanart: str = '', icon: str = '') -> Any:
    """Force Kodi art fields so skins have a visible image to show."""
    if listitem is None or not hasattr(listitem, 'setArt'):
        return listitem
    force = addon_setting('force_art_fallbacks', 'true').lower() == 'true'
    if not force:
        return listitem
    chosen_thumb = best_art(thumb, poster or icon or fanart)
    chosen_poster = best_art(poster, chosen_thumb)
    chosen_icon = best_art(icon, chosen_thumb)
    chosen_fanart = best_art(fanart, chosen_thumb)
    art = {
        'thumb': chosen_thumb,
        'poster': chosen_poster,
        'icon': chosen_icon,
        'fanart': chosen_fanart,
    }
    # Remove empty strings, because some Kodi builds don't like empty art values.
    listitem.setArt({k: v for k, v in art.items() if v})
    return listitem

def set_video_duration(listitem: Any, seconds: int) -> Any:
    """Set duration in modern Kodi, with a compatibility fallback."""
    if not listitem or not seconds:
        return listitem
    try:
        tag = listitem.getVideoInfoTag()
        if hasattr(tag, 'setDuration'):
            tag.setDuration(int(seconds))
            return listitem
    except Exception:
        pass
    try:
        listitem.setInfo('video', {'duration': int(seconds)})
    except Exception:
        pass
    return listitem

def add_standard_sort_methods(handle: int) -> None:
    """Expose Kodi native sort options after the add-on has supplied metadata."""
    if xbmcplugin is None:
        return
    try:
        xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DURATION)
        xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
    except Exception:
        pass

def maybe_set_sidepreview_view() -> None:
    """Switch to the configured view id if Kodi and the active skin allow it."""
    if xbmc is None:
        return
    if addon_setting('auto_sidepreview_view', 'true').lower() != 'true':
        return
    view_id = addon_setting('sidepreview_view_id', '50') or '50'
    try:
        xbmc.executebuiltin(f'Container.SetViewMode({int(view_id)})')
    except Exception:
        pass
