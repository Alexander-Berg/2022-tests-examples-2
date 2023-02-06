# -*- coding: utf-8 -*-
import logging
import re

import allure

logger = logging.getLogger(__name__)

default_theme = 'default'
random_theme = 'random'


def themes_group_export(client):
    res = client.export('themes_group').send()

    assert res.is_ok(), 'Failed to get themes_group export'
    data = res.json()['data']

    assert len(data) > 0, 'No groups found in export'

    def format_group(group):
        split = re.split(' |,', group['themes'])
        group['themes'] = [t.strip() for t in split if t]
        return group

    return [format_group(group) for group in data]


@allure.step('Should see theme "{1}"')
def should_see_theme(dump, theme):
    assert dump['Skin'] == theme, 'Invalid "Skin"'
    assert dump['Themes']['current']['id'] == theme, 'Invalid "Themes.current.id"'
    assert dump['WPSettings']['defskin'] == theme, 'Invalid "WPSettings.defskin"'


@allure.step('Should see default theme')
def should_see_default_theme(dump):
    assert dump['Skin'] is None, 'Invalid "Skin"'
    assert 'current' not in dump['Themes'], 'Invalid "Themes.current"'
    assert 'defskin' not in dump['WPSettings'], 'Invalid "WPSettings.defskin"'


@allure.step('Should see random theme')
def should_see_random_theme(dump):
    assert dump['Skin'] == 'random', 'Invalid "Skin"'
    assert dump['Themes']['current']['id'] == 'random', 'Invalid "Themes.current.id"'
    assert dump['WPSettings']['defskin'] == 'random', 'Invalid "WPSettings.defskin"'
