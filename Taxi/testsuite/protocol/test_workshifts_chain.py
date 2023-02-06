import datetime
import json

import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)


@pytest.fixture
def driver_info(mockserver):
    class Context:
        clid = 'clid1'
        license = 'license'
        uuid = 'uuid1'
        db_id = 'dbid1'

    context = Context()

    @mockserver.json_handler(
        '/driver-authorizer.taxi.yandex.net/driver_session',
    )
    def mock_taximeter_core(request):
        if request.args['session'].isdigit():
            return mockserver.make_response('', int(request.args['session']))
        return {'uuid': context.uuid}

    @mockserver.json_handler('/tracker/1.0/profiles')
    def mock_tracker_profile(request):
        data = json.loads(request.get_data())
        if data['db_id'] == context.db_id:
            return {'clid': context.clid, 'license': context.license}
        return mockserver.make_response('', 404)

    return context


def _get_driver_workshift(db, query):
    return db.driver_workshifts.find_one(
        query,
        projection=[
            'created',
            'date_finish',
            'driver_id',
            'workshifts_counter',
            'home_zone',
            'zones',
            'tariffs',
            'workshift_id',
            'title_key',
            'price',
            'park_price',
            'offer_id',
            'hiring_price',
            'without_vat',
            'park_without_vat',
            'hiring_without_vat',
            'currency',
            'driver_profile_id',
            'db_id',
            'usages',
            'park_contract_currency',
        ],
    )


@pytest.mark.now('2018-09-01T12:00:00+0300')
@pytest.mark.translations(
    geoareas={'moscow': {'en': 'Москва'}},
    tariff={
        'old_category_name.econom': {'en': 'Econom'},
        'old_category_name.comfortplus': {'en': 'Comfort+'},
    },
)
@pytest.mark.config(
    WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00',
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    WORKSHIFTS_TAGS_ENABLED=True,
    WORKSHIFTS_MIN_TAXIMETER_VERSION_FOR_SHIFTS_WITH_TARIFFS='8.55',
    WORKSHIFTS_ENABLED_SHIFTS_WITH_TARIFFS=True,
    WORKSHIFTS_PREFERRED_TARIFFS_ORDER=['econom', 'comfort', 'comfortplus'],
)
@pytest.mark.parametrize('buy_using_offers_allowed', [False, True])
@pytest.mark.driver_tags_match(
    dbid='dbid1', uuid='uuid1', tags=['show_workshift0', 'show_workshift1'],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_workshifts_chain(
        taxi_protocol,
        mockserver,
        config,
        db,
        driver_info,
        buy_using_offers_allowed,
        individual_tariffs_switch_on,
):
    config.set_values(
        dict(WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=buy_using_offers_allowed),
    )

    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': 'clid1',
            'db': 'dbid1',
            'uuid': 'uuid1',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    workshifts_response = response.json()

    if buy_using_offers_allowed:
        offer_id = workshifts_response['offer_id']
        workshifts_response.pop('offer_id')

        workshift_offer = db.workshift_offers.find_one({'_id': offer_id})
        assert workshift_offer == {
            '_id': offer_id,
            'driver_id': 'clid1_uuid1',
            'home_zone': 'moscow',
            'created': datetime.datetime(2018, 9, 1, 9, 0),
            'due': datetime.datetime(2018, 9, 1, 9, 15),
            'workshifts': [
                {
                    'id': 'shift1',
                    'price': '250',
                    'duration_hours': 24,
                    'zones': ['moscow'],
                    'tariffs': ['econom', 'comfortplus'],
                },
            ],
        }

    assert workshifts_response == {
        'available_workshifts': [
            {
                'begin': '2018-08-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 24,
                'home_zone': 'moscow',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [
                    {'name': 'econom', 'title': 'Econom'},
                    {'name': 'comfortplus', 'title': 'Comfort+'},
                ],
                'id': 'shift1',
                'price': '250',
            },
        ],
        'active_workshifts': [],
    }

    workshift_id = workshifts_response['available_workshifts'][0]['id']

    params = {'db': 'dbid1', 'session': 'session_id', 'version': '8.58 (850)'}
    json = {'home_zone': 'moscow', 'workshift_id': workshift_id}
    if buy_using_offers_allowed:
        json['offer_id'] = offer_id

    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=params, json=json,
    )

    assert response.status_code == 200
    buy_workshift_response = response.json()

    assert buy_workshift_response['date_finish'] == '2018-09-02T09:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    data.pop('_id')

    expected_driver_workshift = {
        'created': datetime.datetime(2018, 9, 1, 9, 0),
        'date_finish': datetime.datetime(2018, 9, 2, 9, 0),
        'driver_id': 'clid1_uuid1',
        'workshifts_counter': 'clid1_uuid1:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': ['econom', 'comfortplus'],
        'workshift_id': workshift_id,
        'price': '250',
        'park_price': '250',
        'hiring_price': '0',
        'without_vat': '211.86440677966101694915254237288135593220338983051',
        'park_without_vat': (
            '211.86440677966101694915254237288135593220338983051'
        ),
        'hiring_without_vat': '0',
        'currency': 'RUB',
        'db_id': 'dbid1',
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '250',
            'park_price': '250',
            'hiring_price': '0',
            'without_vat': (
                '211.86440677966101694915254237288135593220338983051'
            ),
            'park_without_vat': (
                '211.86440677966101694915254237288135593220338983051'
            ),
            'hiring_without_vat': '0',
        },
    }
    if buy_using_offers_allowed:
        expected_driver_workshift['offer_id'] = offer_id

    response = taxi_protocol.get(
        '/utils/1.0/workshifts',
        params={
            'clid': 'clid1',
            'db': 'dbid1',
            'uuid': 'uuid1',
            'version': '8.58 (850)',
            'latitude': '55.733863',
            'longitude': '37.590533',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    workshifts_response = response.json()

    if buy_using_offers_allowed:
        workshifts_response.pop('offer_id')

    assert workshifts_response == {
        'available_workshifts': [
            {
                'begin': '2018-08-09T10:35:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'duration_hours': 24,
                'home_zone': 'moscow',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [
                    {'name': 'econom', 'title': 'Econom'},
                    {'name': 'comfortplus', 'title': 'Comfort+'},
                ],
                'id': 'shift1',
                'price': '250',
            },
        ],
        'active_workshifts': [
            {
                'begin': '2018-09-01T09:00:00+0000',
                'end': '2018-09-02T09:00:00+0000',
                'title': 'Москва',
                'currency': 'RUB',
                'home_zone': 'moscow',
                'zones': [{'name': 'moscow', 'title': 'Москва'}],
                'tariffs': [
                    {'name': 'econom', 'title': 'Econom'},
                    {'name': 'comfortplus', 'title': 'Comfort+'},
                ],
                'id': 'shift1',
                'price': '250',
            },
        ],
    }
