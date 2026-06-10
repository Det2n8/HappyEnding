# -*- coding: utf-8 -*-
import sys

try:
    import xbmc
    import xbmcgui
    import xbmcplugin
except Exception:
    xbmc = xbmcgui = xbmcplugin = None

from happyending import (
    parse_duration_to_seconds,
    apply_art,
    set_video_duration,
    add_standard_sort_methods,
)
from .util import parse_params, plugin_url, setting, bool_setting, int_setting, notify
from .provider_loader import enabled_providers, get_provider

HANDLE = None
BASE = None

def _li(label, icon=''):
    item = xbmcgui.ListItem(label=label) if xbmcgui else None
    if item and icon:
        item.setArt({'thumb': icon, 'icon': icon, 'poster': icon, 'fanart': icon})
    return item

def add_dir(label, mode, **params):
    url = plugin_url(BASE, mode=mode, **params)
    item = _li(label, 'special://home/addons/plugin.video.happyending/icon.png')
    xbmcplugin.addDirectoryItem(HANDLE, url, item, isFolder=True)

def add_action(label, mode, **params):
    url = plugin_url(BASE, mode=mode, **params)
    item = _li(label, 'special://home/addons/plugin.video.happyending/icon.png')
    xbmcplugin.addDirectoryItem(HANDLE, url, item, isFolder=False)

def end(content='videos', view=True):
    try:
        xbmcplugin.setContent(HANDLE, content)
    except Exception:
        pass
    xbmcplugin.endOfDirectory(HANDLE)
    if view and bool_setting('force_view', True) and xbmc:
        view_id = int_setting('default_view_id', 50)
        try:
            xbmc.executebuiltin('Container.SetViewMode(%s)' % view_id)
        except Exception:
            pass

def root():
    add_dir('Sites', 'sites')
    add_action('Search all enabled sites', 'search_prompt')
    add_dir('Length presets', 'length_presets')
    add_dir('View type shortcuts', 'viewtypes')
    add_action('Open add-on settings', 'settings')
    end('files', view=False)

def sites():
    for provider in enabled_providers():
        add_dir(provider['name'], 'list', site=provider['id'], page='1')
    end('videos')

def length_presets():
    add_dir('All lengths, long first', 'preset', minsec='0', maxsec='0', sort='long_first')
    add_dir('10 sec to 4:59 min', 'preset', minsec='10', maxsec='299', sort='short_first')
    add_dir('5 to 9:59 min', 'preset', minsec='300', maxsec='599', sort='long_first')
    add_dir('10 to 19:59 min', 'preset', minsec='600', maxsec='1199', sort='long_first')
    add_dir('20 min and over', 'preset', minsec='1200', maxsec='0', sort='long_first')
    add_action('Open settings for exact custom numbers', 'settings')
    end('files', view=False)

def _split_seconds(total):
    total = max(0, int(total or 0))
    return str(total // 60), str(total % 60)

def apply_preset(params):
    # Kodi settings are string-backed. We set them here for fast remote-control use.
    try:
        import xbmcaddon
        minsec = int(params.get('minsec', '0') or 0)
        maxsec = int(params.get('maxsec', '0') or 0)
        min_m, min_s = _split_seconds(minsec)
        max_m, max_s = _split_seconds(maxsec)
        for addon_id in ('plugin.video.happyending', 'script.module.happyending'):
            a = xbmcaddon.Addon(addon_id)
            a.setSetting('enable_length_filter', 'false' if minsec == 0 and maxsec == 0 else 'true')
            a.setSetting('min_minutes', min_m)
            a.setSetting('min_extra_seconds', min_s)
            a.setSetting('max_minutes', max_m)
            a.setSetting('max_extra_seconds', max_s)
            a.setSetting('sort_direction', params.get('sort', 'long_first'))
        notify('HappyEnding', 'Length preset applied')
    except Exception:
        pass
    sites()

def viewtypes():
    add_action('Use HappyEnding Preview: left list + big right thumbnail', 'setview', view='50')
    add_action('Use Poster wall', 'setview', view='500')
    add_action('Use Large landscape thumbs', 'setview', view='501')
    add_action('Use Compact list', 'setview', view='502')
    add_action('Open settings', 'settings')
    end('files', view=False)

def setview(params):
    view_id = params.get('view', '50')
    try:
        import xbmcaddon
        xbmcaddon.Addon('plugin.video.happyending').setSetting('default_view_id', view_id)
        xbmcaddon.Addon('script.module.happyending').setSetting('sidepreview_view_id', view_id)
    except Exception:
        pass
    if xbmc:
        xbmc.executebuiltin('Container.SetViewMode(%s)' % view_id)
    notify('HappyEnding', 'View set to %s' % view_id)
    viewtypes()

def entry_to_listitem(entry):
    title = entry.title
    seconds = parse_duration_to_seconds(entry.duration) or parse_duration_to_seconds(entry.plot)
    if bool_setting('show_duration_in_title', True) and seconds:
        mins = seconds // 60
        sec = seconds % 60
        title = '%s  [%d:%02d]' % (title, mins, sec)
    item = xbmcgui.ListItem(label=title, path=entry.url)
    if entry.playable:
        item.setProperty('IsPlayable', 'true')
    else:
        item.setProperty('IsPlayable', 'false')
    set_video_duration(item, seconds)
    apply_art(item, thumb=entry.thumb, poster=entry.poster, fanart=entry.fanart, icon=entry.thumb)
    try:
        item.setInfo('video', {
            'title': entry.title,
            'plot': entry.plot,
            'duration': seconds,
            'mediatype': 'video',
            'studio': entry.source,
        })
    except Exception:
        pass
    return item, seconds

def _configured_length_range():
    min_total = int_setting('min_minutes', 0) * 60 + int_setting('min_extra_seconds', 0)
    max_total = int_setting('max_minutes', 0) * 60 + int_setting('max_extra_seconds', 0)
    return max(0, min_total), (max(0, max_total) if max_total > 0 else None)

def _entry_seconds(entry):
    return parse_duration_to_seconds(entry.duration) or parse_duration_to_seconds(entry.plot) or parse_duration_to_seconds(entry.title)

def add_video_entries(entries):
    require_thumb = bool_setting('require_thumb', False)
    enable_filter = bool_setting('enable_length_filter', False)
    low, high = _configured_length_range()
    prepared = []
    for entry in entries:
        if require_thumb and not (entry.thumb or entry.poster or entry.fanart):
            continue
        seconds = _entry_seconds(entry)
        if enable_filter:
            if seconds < low:
                continue
            if high is not None and seconds > high:
                continue
        prepared.append((entry, seconds))

    direction = setting('sort_direction', 'long_first')
    if direction != 'none':
        prepared.sort(key=lambda pair: pair[1], reverse=(direction == 'long_first'))

    for entry, _seconds in prepared:
        item, _seconds = entry_to_listitem(entry)
        xbmcplugin.addDirectoryItem(HANDLE, entry.url, item, isFolder=entry.is_folder)
    add_standard_sort_methods(HANDLE)
    end('videos')

def list_site(params):
    site_id = params.get('site', 'template')
    page = int(params.get('page', '1') or 1)
    _provider, module = get_provider(site_id)
    entries = module.list_videos(page=page)
    add_video_entries(entries)

def search_prompt():
    if not xbmcgui:
        return root()
    keyboard = xbmc.Keyboard('', 'Search')
    keyboard.doModal()
    if keyboard.isConfirmed():
        query = keyboard.getText()
        return search_results({'q': query})
    root()

def search_results(params):
    query = params.get('q', '')
    results = []
    for provider in enabled_providers():
        try:
            _p, module = get_provider(provider['id'])
            results.extend(module.search(query, page=1))
        except Exception:
            continue
    add_video_entries(results)

def open_settings():
    try:
        import xbmcaddon
        xbmcaddon.Addon('plugin.video.happyending').openSettings()
    except Exception:
        pass
    root()

def noop():
    notify('HappyEnding', 'Template item only. Add real provider modules.')
    root()

def run(argv=None):
    global HANDLE, BASE
    argv = argv or sys.argv
    BASE = argv[0]
    HANDLE = int(argv[1]) if len(argv) > 1 else -1
    params = parse_params(argv[2] if len(argv) > 2 else '')
    mode = params.get('mode', 'root')
    routes = {
        'root': root,
        'sites': sites,
        'list': lambda: list_site(params),
        'search_prompt': search_prompt,
        'search': lambda: search_results(params),
        'length_presets': length_presets,
        'preset': lambda: apply_preset(params),
        'viewtypes': viewtypes,
        'setview': lambda: setview(params),
        'settings': open_settings,
        'noop': noop,
    }
    routes.get(mode, root)()
