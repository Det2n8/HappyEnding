# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional

@dataclass
class VideoEntry:
    title: str
    url: str
    thumb: str = ''
    poster: str = ''
    fanart: str = ''
    plot: str = ''
    duration: str = ''
    source: str = ''
    playable: bool = True
    is_folder: bool = False

    def as_dict(self):
        return {
            'title': self.title,
            'url': self.url,
            'thumb': self.thumb,
            'poster': self.poster,
            'fanart': self.fanart,
            'plot': self.plot,
            'duration': self.duration,
            'source': self.source,
        }
