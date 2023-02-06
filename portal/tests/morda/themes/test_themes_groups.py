# -*- coding: utf-8 -*-
import json
import logging

import allure
import pytest

from common.client import MordaClient
from common.geobase import Regions
from common.morda import DesktopMain

logger = logging.getLogger(__name__)

parameters = [DesktopMain(language='ru', region=region) for region in [Regions.MOSCOW, Regions.KYIV,
                                                                       Regions.MINSK, Regions.ASTANA]]


@pytest.skip('Not implemented yet')
@pytest.mark.parametrize('morda', parameters[:1])
def test_themes_group(morda):
    client = MordaClient(morda, 'rc')
    client.themes().send()
    client.theme_set('hots').send()
    json.dumps(client.cleanvars().send().json(), indent=4)

    # themes_group_export = themes.themes_group_export(client)
    # groups = client.themes().send().json()['Themes']['group']
    #
    # errors = check_groups(groups, themes_group_export)
    # if len(errors) > 0:
    #     allure.attach('errors.json', json.dumps(errors, indent=4))
    #     pytest.fail('Errors in theme groups')


def check_groups(actual, expected):
    error_buffer = []
    with allure.step('Check groups content'):
        for group in expected:
            actual_group = next((x for x in actual if x['id'] == group['id']), None)
            error = check_group(actual_group, group)
            if error is not None:
                error_buffer.append(error)

    with allure.step('Check groups count'):
        if len(actual) != len(expected):
            error_buffer.append('Expected {} groups, found {}'.format(len(expected), len(actual)))

    return error_buffer


def check_group(group, themes_expected):
    if group is None:
        return 'Group {} not found'.format(group['id'])
    with allure.step('Check group "{}"'.format(group['id'])):
        if sorted(group['themes_array']) != sorted(themes_expected['themes']):
            return 'For group {} \nexpected\t{}\ngot\t{}'.format(group['id'],
                                                                 themes_expected['themes'],
                                                                 group['themes_array'])
