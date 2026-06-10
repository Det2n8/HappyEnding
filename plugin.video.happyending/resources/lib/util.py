# -*- coding: utf-8 -*-
from urllib.parse import urlencode, parse_qsl

try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
except Exception:
    xbmc = xbmcaddon = xbmcgui = xbmcplugin = None

ADDON_ID = 'plugin.video.happyending'

def addon():
    return xbmcaddon.Addon(ADDON_ID) if xbmcaddon else None

def setting(key, default=''):
    a = addon()
    if not a:
        return default
    try:
        return a.getSetting(key) or default
    except Exception:
        return default

def bool_setting(key, default=False):
    value = setting(key, 'true' if default else 'false')
    return str(value).lower() == 'true'

def int_setting(key, default=0):
    try:
        return int(setting(key, str(default)) or default)
    except Exception:
        return default

def parse_params(query):
    if not query:
        return {}
    return dict(parse_qsl(query.lstrip('?')))

def plugin_url(base, **params):
    return base + '?' + urlencode(params)

def notify(title, message):
    if xbmcgui:
        xbmcgui.Dialog().notification(title, message)

def log(message):
    if xbmc:
        xbmc.log('[HappyEnding] %s' % message, xbmc.LOGINFO)
