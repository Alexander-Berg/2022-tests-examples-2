# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common import env, schema
from common.client import MordaClient
from common.geobase import Regions
from common.schema import get_schema_validator

logger = logging.getLogger(__name__)

TESTEE = 'ntp_notifications'


# Sample request:
# /portal/ntp/notifications?cards=districts,stream&geo=2
#


cards = [
    'disaster_alert',
    'disaster_fatal',
    'disaster_metro',
    'disaster_promo',
    'disaster_traffic',
    'district',
    'districts',
    'domik',
    'nowcast',
    # 'plus',            # 204 No Content, as disabled in MADM ntp_notifications
    'promo',
    # 'rates',           # 204 No Content, as disabled in MADM ntp_notifications
    'route',
    'stream',
    'traffic',
    'weather',
    'vitals',
    'stream,plus,rates'  # Safe way to test 'plus' and 'rates' if suddenly re-enabled in MADM 
]
regions = [Regions.MOSCOW, Regions.SAINT_PETERSBURG, Regions.VORONEZH, Regions.MINSK, Regions.KYIV, Regions.LVIV, Regions.ASTANA, Regions.LONDON]


def test_params():
    res = []
    res.extend([dict(cards=card, geo=geo)
                    for card in cards
                    for geo in regions])
    return res


@pytest.mark.yasm
@allure.feature(TESTEE)
@allure.story('portal_ntp_notifications_response')
@pytest.mark.parametrize('params', test_params())
def test_schema(params, yasm):
    client = MordaClient(env=env.morda_env())
    response = client.portal_ntp_notifications(**params).send()
    assert response.is_ok(), 'Failed to get portal/ntp/notifications response'
    data = response.json()
    # print json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8')
    validator = get_schema_validator('schema/ntp/notifications/notifications-response.json')

    try:
        schema.validate_schema(data, validator)
        add_schema_signal(yasm, True)
    except Exception as e:
        add_schema_signal(yasm, False)
        raise e


def add_schema_signal(yasm, is_ok):
    if not yasm:
        return
    passed = 1 if is_ok else 0
    failed = 1 - passed

    yasm.add_to_signal('morda_portal_ntp_notifications_passed_tttt', passed)
    yasm.add_to_signal('morda_portal_ntp_notifications_failed_tttt', failed)

