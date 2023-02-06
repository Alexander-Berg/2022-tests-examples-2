# -*- coding: utf-8 -*-

import pytest
from deepdiff import DeepDiff

from common.client import MordaClient
from tests.portal_set.set_common import mordas_for_domains


@pytest.mark.parametrize('morda', mordas_for_domains[:1])
def test_yabs_info_options(morda):
    client = MordaClient(morda)

    params = {'options': 'yabs_info_options_on:all'}
    response_yabs_info = client.cleanvars(blocks=['Banner_debug'], params=params).send()
    options_yabs_info = response_yabs_info.json()['Banner_debug']['yabs_info_options']['options']
    bkflags_yabs_info = response_yabs_info.json()['Banner_debug']['yabs_info_options']['BKFlags']
    targetinginfo_yabs_info = response_yabs_info.json()['Banner_debug']['yabs_info_options']['TargetingInfo']

    params = {'options': 'yabs_info_options_on:0'}
    response = client.cleanvars(blocks=['Banner_debug'], params=params).send()
    options = response.json()['Banner_debug']['options']
    bkflags = response.json()['Banner_debug']['BKFlags']
    targetinginfo = response.json()['Banner_debug']['TargetingInfo']

    assert options_yabs_info
    assert options
    assert bkflags_yabs_info
    assert bkflags
    assert targetinginfo_yabs_info
    assert targetinginfo

    assert not DeepDiff(options_yabs_info, options)
    assert not DeepDiff(bkflags_yabs_info.keys(), bkflags.keys())
    assert not DeepDiff(targetinginfo_yabs_info, targetinginfo)
