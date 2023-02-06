# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from api_search_common import app_info, all_langs, validate_schema_for_block, gen_params, ids
from common import env
from common.client import MordaClient
from common.geobase import Regions

logger = logging.getLogger(__name__)

BLOCK = 'zen'

app_info = {
    'android': [v for v in app_info['android'] if v >= 6020001]
}


def get_regions():
    return [Regions.MOSCOW, Regions.SAINT_PETERSBURG, Regions.YEKATERINBURG, Regions.VORONEZH,
            Regions.NIZHNY_NOVGOROD, Regions.ROSTOV_NA_DONU, Regions.KRASNODAR, Regions.CHELYABINSK,
            Regions.SAMARA, Regions.NOVOSIBIRSK, Regions.VOLGOGRAD, Regions.UFA, Regions.PERM,
            Regions.SARATOV, Regions.PETROPAVLOVSK]


def zen_schema_params():
    return gen_params(
        app_info=app_info,
        regions=get_regions(),
        langs=all_langs
    )


@pytest.mark.yasm
@allure.feature('api_search_v2_unstable', 'zen')
@allure.story('api_search_v2_schema')
@pytest.mark.parametrize('params', zen_schema_params(), ids=ids)
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    validate_schema_for_block(client, 'zen', params, yasm=yasm)
