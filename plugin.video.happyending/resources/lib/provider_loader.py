# -*- coding: utf-8 -*-
import importlib
from pathlib import Path
from .util import bool_setting

PROVIDERS = [
    {
        'id': 'template',
        'name': 'Example provider template',
        'module': 'resources.lib.sources.template_provider',
        'setting': 'enable_example_provider',
    },
]

def enabled_providers():
    out = []
    for provider in PROVIDERS:
        setting_id = provider.get('setting')
        if setting_id and not bool_setting(setting_id, True):
            continue
        out.append(provider)
    return out

def get_provider(provider_id):
    for provider in PROVIDERS:
        if provider['id'] == provider_id:
            module = importlib.import_module(provider['module'])
            return provider, module
    raise KeyError(provider_id)
