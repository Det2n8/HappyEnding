# -*- coding: utf-8 -*-
"""
Provider template.

Replace this file with source modules you are allowed to use.
Each module should expose:
- list_videos(page=1) -> list[VideoEntry]
- search(query, page=1) -> list[VideoEntry]

The example items are harmless placeholders so you can test the skin/views.
"""
from resources.lib.models import VideoEntry

NAME = 'Example provider template'

def list_videos(page=1):
    return [
        VideoEntry(
            title='Template item: 05 min visible thumbnail test',
            url='plugin://plugin.video.happyending/?mode=noop',
            thumb='special://home/addons/plugin.video.happyending/icon.png',
            poster='special://home/addons/plugin.video.happyending/icon.png',
            fanart='special://home/addons/plugin.video.happyending/icon.png',
            plot='Example entry for testing the HappyEnding SidePreview skin. Duration 05:00.',
            duration='05:00',
            source=NAME,
            playable=False,
        ),
        VideoEntry(
            title='Template item: 22 min custom length test',
            url='plugin://plugin.video.happyending/?mode=noop',
            thumb='special://home/addons/plugin.video.happyending/icon.png',
            poster='special://home/addons/plugin.video.happyending/icon.png',
            fanart='special://home/addons/plugin.video.happyending/icon.png',
            plot='Example entry for testing sorting. Duration 22:10.',
            duration='22:10',
            source=NAME,
            playable=False,
        ),
        VideoEntry(
            title='Template item: 75 min long-first test',
            url='plugin://plugin.video.happyending/?mode=noop',
            thumb='special://home/addons/plugin.video.happyending/icon.png',
            poster='special://home/addons/plugin.video.happyending/icon.png',
            fanart='special://home/addons/plugin.video.happyending/icon.png',
            plot='Example entry for testing long-first sorting. Duration 1:15:00.',
            duration='1:15:00',
            source=NAME,
            playable=False,
        ),
    ]

def search(query, page=1):
    q = (query or '').lower()
    return [item for item in list_videos(page) if q in item.title.lower()]
