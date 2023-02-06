# -*- coding: utf-8 -*-

import allure
import pytest
from deepdiff import DeepDiff
from common.client import MordaClient
from tests.portal_set.set_common import mordas_for_domains

@allure.feature('morda')
@allure.story('morda v15 blocks')
@pytest.mark.parametrize('morda', mordas_for_domains[:-2]) # no com com.tr
def test_blocks(morda):
    client = MordaClient(morda)

    params = {} # TODO: only v15 plain
    response = client.cleanvars(params=params).send()
    json = response.json()
    blocks = json['blocks']

    assert not DeepDiff(blocks, [[u'topnews'], [u'weather', u'traffic'], [], [], []])

    assert json.get('Weather').get('show')
    assert json.get('Topnews').get('show')
    assert json.get('Traffic').get('show')
