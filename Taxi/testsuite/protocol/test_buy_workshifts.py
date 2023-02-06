import datetime

import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)


@pytest.fixture
def driver_info(mockserver):
    class Context:
        clid = 'clid1'
        license = 'ABCLID1_NO-HIRE-UUID'
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


@pytest.mark.driver_experiments('show_experiment1')
@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
def test_buy_workshifts(taxi_protocol, mockserver, db, driver_info):
    get_good = {
        'db': 'dbid1',
        'session': 'session_id',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}
    get, post = get_good.copy(), post_good.copy()
    response = taxi_protocol.get('taximeter/buy-workshifts', params=get)
    assert response.status_code == 405

    get, post = get_good.copy(), post_good.copy()
    get['session'] = '401'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 401

    get, post = get_good.copy(), post_good.copy()
    get['session'] = '403'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 403

    get, post = get_good.copy(), post_good.copy()
    get['db'] = 'dbid228'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 404

    get, post = get_good.copy(), post_good.copy()
    post['home_zone'] = 'ekb'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 404

    get, post = get_good.copy(), post_good.copy()
    post['home_zone'] = 'spb'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 404

    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'w'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 404

    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2017-04-26T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_uuid1',
        'workshifts_counter': 'clid1_uuid1:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': [],
        'workshift_id': 'workshift2',
        'price': '500000',
        'park_price': '560000',
        'hiring_price': '60000',
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '474576.27118644067796610169491525423728813559322034'
        ),
        'hiring_without_vat': (
            '50847.457627118644067796610169491525423728813559322'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'uuid1',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
        },
    }

    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 409

    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 409

    driver_info.uuid = 'with-rent-uuid'
    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2017-04-26T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_with-rent-uuid'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_with-rent-uuid',
        'workshifts_counter': 'clid1_with-rent-uuid:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': [],
        'workshift_id': 'workshift2',
        'price': '500000',
        'park_price': '560000',
        'hiring_price': '60000',
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '474576.27118644067796610169491525423728813559322034'
        ),
        'hiring_without_vat': (
            '50847.457627118644067796610169491525423728813559322'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'with-rent-uuid',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
        },
    }


@pytest.mark.driver_experiments('show_experiment1')
@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(dbparks='clid2')
def test_buy_workshifts_clid2(taxi_protocol, mockserver, db, driver_info):
    get_good = {
        'db': 'dbid1',
        'session': 'session_id',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}
    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 406

    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'workshift1'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 200

    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 409


@pytest.mark.driver_experiments('show_experiment1')
@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(dbparks='clid3')
def test_buy_workshifts_clid3(taxi_protocol, mockserver, db, driver_info):
    get_good = {
        'db': 'dbid1',
        'session': 'session_id',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}
    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 406


@pytest.mark.driver_experiments('show_experiment1')
@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
def test_buy_workshift_hiring(taxi_protocol, mockserver, db, driver_info):
    driver_info.uuid = 'no-hire-uuid'
    get_good = {
        'db': 'dbid1',
        'session': 'session_id',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}
    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2017-04-26T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_no-hire-uuid'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_no-hire-uuid',
        'workshifts_counter': 'clid1_no-hire-uuid:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': [],
        'workshift_id': 'workshift2',
        'price': '500000',
        'park_price': '500000',
        'hiring_price': '0',
        'hiring_without_vat': '0',
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '423728.81355932203389830508474576271186440677966102'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'no-hire-uuid',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '500000',
            'hiring_price': '0',
            'hiring_without_vat': '0',
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
        },
    }

    driver_info.clid = 'clid1'
    driver_info.uuid = 'old-hire-uuid'
    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2017-04-26T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_old-hire-uuid'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_old-hire-uuid',
        'workshifts_counter': 'clid1_old-hire-uuid:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': [],
        'workshift_id': 'workshift2',
        'price': '500000',
        'park_price': '500000',
        'hiring_price': '0',
        'hiring_without_vat': '0',
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '423728.81355932203389830508474576271186440677966102'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'old-hire-uuid',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '500000',
            'hiring_price': '0',
            'hiring_without_vat': '0',
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
        },
    }


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(
    WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00',
    ENABLE_DYNAMIC_PARK_THRESHOLD=True,
)
def test_buy_workshifts_with_threshold(
        taxi_protocol, mockserver, db, driver_info,
):
    driver_info.clid = 'clid4'
    driver_info.db_id = 'dbid4'
    params = {'db': 'dbid4', 'session': 'session_id', 'version': '8.58 (850)'}
    post = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}

    # driver_info.clid = 'clid4'
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=params, json=post,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2017-04-26T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid4_uuid1'})
    data.pop('_id')
    data.pop('without_vat')
    data.pop('park_without_vat')
    data['park_contract_currency'].pop('without_vat')
    data['park_contract_currency'].pop('park_without_vat')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid4_uuid1',
        'workshifts_counter': 'clid4_uuid1:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': [],
        'workshift_id': 'workshift1',
        'price': '500',
        'park_price': '500',
        'hiring_price': '0',
        'hiring_without_vat': '0',
        'currency': 'RUB',
        'driver_profile_id': 'uuid1',
        'db_id': 'dbid4',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500',
            'park_price': '500',
            'hiring_price': '0',
            'hiring_without_vat': '0',
        },
    }

    driver_info.clid = 'clid5'
    driver_info.db_id = 'dbid5'
    params['db'] = driver_info.db_id
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=params, json=post,
    )
    assert response.status_code == 406


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.parametrize(
    'workshift,expected_status', [('workshift3', 200), ('workshift4', 404)],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_buy_workshift_price_testing(
        taxi_protocol,
        mockserver,
        db,
        driver_info,
        workshift,
        expected_status,
        individual_tariffs_switch_on,
):
    get_good = {
        'db': 'dbid1',
        'session': 'session_id',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': workshift}
    get, post = get_good.copy(), post_good.copy()
    post['workshift_id'] = workshift
    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=get, json=post,
    )
    assert response.status_code == expected_status
    data = response.json()
    if response.status_code == 200:
        assert data['date_finish'] == '2017-04-26T07:00:00+0000'
        data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
        data.pop('_id')
        assert data == {
            'created': datetime.datetime(2017, 4, 25, 7, 0),
            'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:0',
            'home_zone': 'moscow',
            'workshift_id': workshift,
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'currency': 'RUB',
            'driver_profile_id': 'uuid1',
            'db_id': 'dbid1',
            'usages': [],
            'zones': ['moscow'],
            'tariffs': [],
            'park_contract_currency': {
                'currency': 'RUB',
                'price': '500000',
                'park_price': '560000',
                'hiring_price': '60000',
                'hiring_without_vat': (
                    '50847.457627118644067796610169491525423728813559322'
                ),
                'without_vat': (
                    '423728.81355932203389830508474576271186440677966102'
                ),
                'park_without_vat': (
                    '474576.27118644067796610169491525423728813559322034'
                ),
            },
        }
    else:
        assert data == {
            'error': {
                'text': (
                    'Workshift availaible only for '
                    'experiment: show_experiment1'
                ),
            },
        }


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(workshift_rules='with_title')
def test_buy_workshift_with_title(taxi_protocol, mockserver, db, driver_info):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 200
    data = response.json()
    data.pop('id')
    assert data == {'date_finish': '2017-04-26T07:00:00+0000'}

    # check db
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_uuid1',
        'workshifts_counter': 'clid1_uuid1:0',
        'title_key': 'moscow_key',
        'home_zone': 'moscow',
        'workshift_id': 'workshift3',
        'price': '500000',
        'park_price': '560000',
        'hiring_price': '60000',
        'hiring_without_vat': (
            '50847.457627118644067796610169491525423728813559322'
        ),
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '474576.27118644067796610169491525423728813559322034'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'uuid1',
        'db_id': 'dbid1',
        'usages': [],
        'zones': ['moscow'],
        'tariffs': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
        },
    }


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(workshift_rules='with_zones')
def test_buy_workshift_with_zones(taxi_protocol, mockserver, db, driver_info):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 200
    data = response.json()
    data.pop('id')
    assert data == {'date_finish': '2017-04-26T07:00:00+0000'}

    # check db
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_uuid1',
        'workshifts_counter': 'clid1_uuid1:0',
        'home_zone': 'moscow',
        'zones': ['almaty', 'moscow'],
        'tariffs': [],
        'workshift_id': 'workshift3',
        'price': '500000',
        'park_price': '560000',
        'hiring_price': '60000',
        'hiring_without_vat': (
            '50847.457627118644067796610169491525423728813559322'
        ),
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '474576.27118644067796610169491525423728813559322034'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'uuid1',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
        },
    }


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(workshift_rules='with_title_and_zones')
def test_buy_workshift_with_title_and_zones(
        taxi_protocol, mockserver, db, driver_info,
):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 200
    data = response.json()
    data.pop('id')
    assert data == {'date_finish': '2017-04-26T07:00:00+0000'}

    # check db
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_uuid1',
        'workshifts_counter': 'clid1_uuid1:0',
        'title_key': 'moscow_key',
        'home_zone': 'moscow',
        'zones': ['almaty', 'moscow'],
        'tariffs': [],
        'workshift_id': 'workshift3',
        'price': '500000',
        'park_price': '560000',
        'hiring_price': '60000',
        'hiring_without_vat': (
            '50847.457627118644067796610169491525423728813559322'
        ),
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '474576.27118644067796610169491525423728813559322034'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'uuid1',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
        },
    }


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(driver_workshifts='without_counter')
def test_buy_workshift_without_counter(
        taxi_protocol, mockserver, db, driver_info,
):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 200
    data = response.json()
    data.pop('id')
    assert data == {'date_finish': '2017-04-26T07:00:00+0000'}

    # check db
    query = {'driver_id': 'clid1_uuid1'}
    assert db.driver_workshifts.count(query) == 3
    data = [w for w in db.driver_workshifts.find(query, sort=[('created', 1)])]
    for w in data:
        w.pop('_id')
        w.pop('updated')
        w.pop('created_ts')
    assert data == [
        {
            'created': datetime.datetime(2016, 12, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2016, 12, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '1111',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 1, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2017, 1, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '2222',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 4, 25, 7, 0),
            'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:0',
            'home_zone': 'moscow',
            'zones': ['moscow'],
            'tariffs': [],
            'workshift_id': 'workshift3',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'currency': 'RUB',
            'db_id': 'dbid1',
            'driver_profile_id': 'uuid1',
            'usages': [],
            'park_contract_currency': {
                'currency': 'RUB',
                'price': '500000',
                'park_price': '560000',
                'hiring_price': '60000',
                'hiring_without_vat': (
                    '50847.457627118644067796610169491525423728813559322'
                ),
                'without_vat': (
                    '423728.81355932203389830508474576271186440677966102'
                ),
                'park_without_vat': (
                    '474576.27118644067796610169491525423728813559322034'
                ),
            },
        },
    ]


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(driver_workshifts='incorrect_counter')
def test_buy_workshift_incorrect_counter(
        taxi_protocol, mockserver, db, driver_info,
):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 500

    # check db
    query = {'driver_id': 'clid1_uuid1'}
    assert db.driver_workshifts.count(query) == 2
    data = [w for w in db.driver_workshifts.find(query, sort=[('created', 1)])]
    for w in data:
        w.pop('_id')
        w.pop('updated')
        w.pop('created_ts')
    assert data == [
        {
            'created': datetime.datetime(2016, 12, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2016, 12, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '1111',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 1, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2017, 1, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '2222',
            'workshifts_counter': 'bla-bla-bla',
            'zones': ['moscow'],
        },
    ]


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(driver_workshifts='correct_counters')
def test_buy_workshift_correct_counters(
        taxi_protocol, mockserver, db, driver_info,
):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 200
    data = response.json()
    data.pop('id')
    assert data == {'date_finish': '2017-04-26T07:00:00+0000'}

    # check db
    query = {'driver_id': 'clid1_uuid1'}
    assert db.driver_workshifts.count(query) == 3
    data = [w for w in db.driver_workshifts.find(query, sort=[('created', 1)])]
    for w in data:
        w.pop('_id')
        w.pop('updated')
        w.pop('created_ts')
    assert data == [
        {
            'created': datetime.datetime(2016, 12, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2016, 12, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:5',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '1111',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 1, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2017, 1, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:10',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '2222',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 4, 25, 7, 0),
            'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:11',
            'home_zone': 'moscow',
            'zones': ['moscow'],
            'tariffs': [],
            'workshift_id': 'workshift3',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'currency': 'RUB',
            'driver_profile_id': 'uuid1',
            'db_id': 'dbid1',
            'usages': [],
            'park_contract_currency': {
                'currency': 'RUB',
                'price': '500000',
                'park_price': '560000',
                'hiring_price': '60000',
                'hiring_without_vat': (
                    '50847.457627118644067796610169491525423728813559322'
                ),
                'without_vat': (
                    '423728.81355932203389830508474576271186440677966102'
                ),
                'park_without_vat': (
                    '474576.27118644067796610169491525423728813559322034'
                ),
            },
        },
    ]


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(driver_workshifts='mixed_counters')
def test_buy_workshift_mixed_counters(
        taxi_protocol, mockserver, db, driver_info,
):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 200
    data = response.json()
    data.pop('id')
    assert data == {'date_finish': '2017-04-26T07:00:00+0000'}

    # check db
    query = {'driver_id': 'clid1_uuid1'}
    assert db.driver_workshifts.count(query) == 3
    data = [w for w in db.driver_workshifts.find(query, sort=[('created', 1)])]
    for w in data:
        w.pop('_id')
        w.pop('updated')
        w.pop('created_ts')
    assert data == [
        {
            'created': datetime.datetime(2016, 12, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2016, 12, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '1111',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 1, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2017, 1, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:10',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '2222',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 4, 25, 7, 0),
            'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:11',
            'home_zone': 'moscow',
            'zones': ['moscow'],
            'tariffs': [],
            'workshift_id': 'workshift3',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'currency': 'RUB',
            'driver_profile_id': 'uuid1',
            'db_id': 'dbid1',
            'usages': [],
            'park_contract_currency': {
                'currency': 'RUB',
                'price': '500000',
                'park_price': '560000',
                'hiring_price': '60000',
                'hiring_without_vat': (
                    '50847.457627118644067796610169491525423728813559322'
                ),
                'without_vat': (
                    '423728.81355932203389830508474576271186440677966102'
                ),
                'park_without_vat': (
                    '474576.27118644067796610169491525423728813559322034'
                ),
            },
        },
    ]


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(driver_workshifts='has_active_workshift')
def test_buy_workshift_has_active_workshift(
        taxi_protocol, mockserver, db, driver_info,
):
    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 409
    data = response.json()
    assert data == {'error': {'text': 'has active workshift'}}

    # check db
    query = {'driver_id': 'clid1_uuid1'}
    assert db.driver_workshifts.count(query) == 2
    data = [w for w in db.driver_workshifts.find(query, sort=[('created', 1)])]
    for w in data:
        w.pop('_id')
        w.pop('updated')
        w.pop('created_ts')
    assert data == [
        {
            'created': datetime.datetime(2016, 12, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2016, 12, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:5',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '1111',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 4, 24, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2017, 4, 25, 9, 35),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:10',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '2222',
            'zones': ['moscow'],
        },
    ]


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.driver_experiments('workshifts_ab_testing')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(driver_workshifts='correct_counters')
def test_buy_workshift_race_condition(
        taxi_protocol, mockserver, testpoint, db, driver_info,
):

    testpoint.parallel_cals_counter = 0

    @testpoint('buy-workshifts::workshift_counter_obtained')
    def do_parallel_call(data):
        testpoint.parallel_cals_counter += 1
        if testpoint.parallel_cals_counter > 1:
            return
        response = taxi_protocol.post(
            'taximeter/buy-workshifts',
            params={
                'db': 'dbid1',
                'session': 'session_id',
                'version': '8.58 (850)',
            },
            json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
        )
        # check response
        assert response.status_code == 200
        data = response.json()
        data.pop('id')
        assert data == {'date_finish': '2017-04-26T07:00:00+0000'}

    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )

    # check response
    assert response.status_code == 409
    data = response.json()
    assert data == {'error': {'text': 'race condition'}}

    # check db
    query = {'driver_id': 'clid1_uuid1'}
    assert db.driver_workshifts.count(query) == 3
    data = [w for w in db.driver_workshifts.find(query, sort=[('created', 1)])]
    for w in data:
        w.pop('_id')
        w.pop('updated')
        w.pop('created_ts')
    assert data == [
        {
            'created': datetime.datetime(2016, 12, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2016, 12, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:5',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '1111',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 1, 15, 9, 35),
            'currency': 'RUB',
            'date_finish': datetime.datetime(2017, 1, 16, 9, 35),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:10',
            'home_zone': 'moscow',
            'price': '1000',
            'workshift_id': '2222',
            'zones': ['moscow'],
        },
        {
            'created': datetime.datetime(2017, 4, 25, 7, 0),
            'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
            'driver_id': 'clid1_uuid1',
            'workshifts_counter': 'clid1_uuid1:11',
            'home_zone': 'moscow',
            'zones': ['moscow'],
            'tariffs': [],
            'workshift_id': 'workshift3',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'currency': 'RUB',
            'driver_profile_id': 'uuid1',
            'db_id': 'dbid1',
            'usages': [],
            'park_contract_currency': {
                'currency': 'RUB',
                'price': '500000',
                'park_price': '560000',
                'hiring_price': '60000',
                'hiring_without_vat': (
                    '50847.457627118644067796610169491525423728813559322'
                ),
                'without_vat': (
                    '423728.81355932203389830508474576271186440677966102'
                ),
                'park_without_vat': (
                    '474576.27118644067796610169491525423728813559322034'
                ),
            },
        },
    ]


@pytest.mark.now('2018-07-07T10:00:00+0300')
@pytest.mark.parametrize(
    'park_id,db_id,driver_id,json,without_vat,workshift',
    [
        (
            'clid6',
            'dbid6',
            'uuid1',
            {'home_zone': 'minsk', 'workshift_id': 'workshift5'},
            '2018-07-08 00:00:00',
            {
                'created': datetime.datetime(2018, 7, 7, 7, 0),
                'date_finish': datetime.datetime(2018, 7, 8, 7, 0),
                'driver_id': 'clid6_uuid1',
                'workshifts_counter': 'clid6_uuid1:0',
                'home_zone': 'minsk',
                'zones': ['minsk'],
                'tariffs': [],
                'workshift_id': 'workshift5',
                'price': '8',
                'park_price': '8',
                'hiring_price': '0',
                'currency': 'BYN',
                'driver_profile_id': 'uuid1',
                'db_id': 'dbid6',
                'usages': [],
                'park_contract_currency': {
                    'currency': 'USD',
                    'price': '4.0596772556581751750735816504',
                    'park_price': '4.0596772556581751750735816504',
                    'hiring_price': '0',
                },
            },
        ),
        (
            'clid6',
            'dbid6',
            'uuid2',
            {'home_zone': 'minsk', 'workshift_id': 'workshift5'},
            '2018-07-08 00:00:00',
            {
                'created': datetime.datetime(2018, 7, 7, 7, 0),
                'date_finish': datetime.datetime(2018, 7, 8, 7, 0),
                'driver_id': 'clid6_uuid2',
                'workshifts_counter': 'clid6_uuid2:0',
                'home_zone': 'minsk',
                'zones': ['minsk'],
                'tariffs': [],
                'workshift_id': 'workshift5',
                'price': '8',
                'park_price': '8.96',
                'hiring_price': '0.96',
                'currency': 'BYN',
                'driver_profile_id': 'uuid2',
                'db_id': 'dbid6',
                'usages': [],
                'park_contract_currency': {
                    'currency': 'USD',
                    'price': '4.0596772556581751750735816504',
                    'park_price': '4.546838526337156196082411448448',
                    'hiring_price': '0.487161270678981021008829798048',
                },
            },
        ),
        (
            'clid6',
            'dbid6',
            'uuid2',
            {'home_zone': 'minsk', 'workshift_id': 'workshift5'},
            '2018-07-06 00:00:00',
            {
                'created': datetime.datetime(2018, 7, 7, 7, 0),
                'date_finish': datetime.datetime(2018, 7, 8, 7, 0),
                'driver_id': 'clid6_uuid2',
                'workshifts_counter': 'clid6_uuid2:0',
                'home_zone': 'minsk',
                'zones': ['minsk'],
                'tariffs': [],
                'workshift_id': 'workshift5',
                'price': '8',
                'park_price': '8.96',
                'hiring_price': '0.96',
                'hiring_without_vat': (
                    '0.81355932203389830508474576271186440677966101694915'
                ),
                'without_vat': (
                    '6.7796610169491525423728813559322033898305084745763'
                ),
                'park_without_vat': (
                    '7.5932203389830508474576271186440677966101694915254'
                ),
                'currency': 'BYN',
                'driver_profile_id': 'uuid2',
                'db_id': 'dbid6',
                'usages': [],
                'park_contract_currency': {
                    'currency': 'USD',
                    'price': '4.0596772556581751750735816504',
                    'park_price': '4.546838526337156196082411448448',
                    'hiring_price': '0.487161270678981021008829798048',
                    'hiring_without_vat': (
                        '0.41284853447371272966849982885423728813559322033898'
                    ),
                    'without_vat': (
                        '3.4404044539476060805708319071186440677966101694915'
                    ),
                    'park_without_vat': (
                        '3.8532529884213188102393317359728813559322033898305'
                    ),
                },
            },
        ),
    ],
)
@pytest.mark.filldb(cities='foreign')
@pytest.mark.filldb(countries='foreign')
@pytest.mark.filldb(tariff_settings='foreign')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_buy_workshift_in_other_countries(
        config,
        taxi_protocol,
        mockserver,
        db,
        driver_info,
        park_id,
        driver_id,
        json,
        without_vat,
        workshift,
        db_id,
        individual_tariffs_switch_on,
):
    config.set_values(dict(WORKSHIFT_WITHOUT_VAT_START=without_vat))
    driver_info.clid = park_id
    driver_info.uuid = driver_id
    driver_info.db_id = db_id

    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid6',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json=json,
    )

    # check response
    assert response.status_code == 200
    data = response.json()
    data.pop('id')
    assert data == {'date_finish': '2018-07-08T07:00:00+0000'}

    # check db
    query = {'driver_id': park_id + '_' + driver_id}
    assert db.driver_workshifts.count(query) == 1
    data = _get_driver_workshift(db, query)
    data.pop('_id')
    assert data == workshift


@pytest.mark.now('2018-07-08T22:00:00+0600')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.parametrize(
    'park_id,json,error,msg',
    [
        pytest.param(
            'clid6',
            {'home_zone': 'almaty', 'workshift_id': 'workshift6'},
            406,
            'not allowed buy workshift in other country',
            marks=pytest.mark.filldb(dbparks='clid6'),
        ),
    ],
)
@pytest.mark.filldb(cities='foreign')
@pytest.mark.filldb(countries='foreign')
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_buy_workshift_errors(
        taxi_protocol,
        mockserver,
        db,
        driver_info,
        park_id,
        json,
        error,
        msg,
        individual_tariffs_switch_on,
):
    driver_info.clid = park_id

    # call
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json=json,
    )

    # check response
    assert response.status_code == error
    data = response.json()
    assert data == {'error': {'text': msg}}


@pytest.mark.now('2018-08-20T10:00:00+0300')
@pytest.mark.config(
    WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00',
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
)
@pytest.mark.parametrize(
    'workshift,offer,clid,expected_code,' 'expected_response',
    [
        ('workshift1', 'offer1', 'clid1', 200, None),
        pytest.param(
            'workshift1',
            'offer1',
            'clid2',
            404,
            {'error': {'text': 'offer not found'}},
            marks=pytest.mark.filldb(dbparks='clid2'),
        ),
        (
            'workshift2',
            'offer1',
            'clid1',
            404,
            {
                'error': {
                    'text': (
                        'workshift is not found in offer, offer_id: offer1, '
                        'id: workshift2'
                    ),
                },
            },
        ),
        (
            'workshift1',
            'offer2',
            'clid1',
            404,
            {
                'error': {
                    'text': 'workshift offer is obsolete, offer_id: offer2',
                },
            },
        ),
    ],
    ids=[
        'buy workshfit from offer',
        'offer not found',
        'workshift not found in offer',
        'offer is obsolete',
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_buy_workshift_use_offer(
        taxi_protocol,
        mockserver,
        db,
        driver_info,
        workshift,
        offer,
        clid,
        expected_code,
        expected_response,
        individual_tariffs_switch_on,
):
    params = {'db': 'dbid1', 'session': 'session_id', 'version': '8.58 (850)'}
    json = {
        'home_zone': 'moscow',
        'workshift_id': workshift,
        'offer_id': offer,
    }

    driver_info.clid = clid

    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=params, json=json,
    )

    assert response.status_code == expected_code
    data = response.json()

    if response.status_code == 200:
        assert data['date_finish'] == '2018-08-20T22:00:00+0000'
        data = _get_driver_workshift(db, {'driver_id': clid + '_uuid1'})
        data.pop('_id')
        assert data == {
            'created': datetime.datetime(2018, 8, 20, 7, 0),
            'date_finish': datetime.datetime(2018, 8, 20, 22, 0),
            'driver_id': clid + '_uuid1',
            'workshifts_counter': 'clid1_uuid1:0',
            'home_zone': 'moscow',
            'zones': ['moscow', 'svo'],
            'tariffs': [],
            'workshift_id': workshift,
            'title_key': 'random_title',
            'price': '250',
            'park_price': '250',
            'offer_id': offer,
            'hiring_price': '0',
            'without_vat': (
                '211.86440677966101694915254237288135593220338983051'
            ),
            'park_without_vat': (
                '211.86440677966101694915254237288135593220338983051'
            ),
            'hiring_without_vat': '0',
            'currency': 'RUB',
            'driver_profile_id': 'uuid1',
            'db_id': 'dbid1',
            'usages': [],
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
    else:
        assert data == expected_response


@pytest.mark.now('2018-08-20T10:00:00+0300')
@pytest.mark.config(
    WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00',
    WORKSHIFTS_BUY_USING_OFFERS_ALLOWED=True,
)
def test_buy_workshift_with_tariffs(
        taxi_protocol, mockserver, db, driver_info,
):
    params = {'db': 'dbid1', 'session': 'session_id', 'version': '8.58 (850)'}
    json = {
        'home_zone': 'moscow',
        'workshift_id': 'workshift1',
        'offer_id': 'offer3',
    }

    driver_info.clid = 'clid1'

    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=params, json=json,
    )

    assert response.status_code == 200
    data = response.json()

    assert data['date_finish'] == '2018-08-20T22:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2018, 8, 20, 7, 0),
        'date_finish': datetime.datetime(2018, 8, 20, 22, 0),
        'driver_id': 'clid1_uuid1',
        'workshifts_counter': 'clid1_uuid1:0',
        'home_zone': 'moscow',
        'zones': ['moscow', 'svo'],
        'tariffs': ['econom', 'comfort'],
        'workshift_id': 'workshift1',
        'title_key': 'random_title',
        'price': '250',
        'park_price': '250',
        'offer_id': 'offer3',
        'hiring_price': '0',
        'without_vat': '211.86440677966101694915254237288135593220338983051',
        'park_without_vat': (
            '211.86440677966101694915254237288135593220338983051'
        ),
        'hiring_without_vat': '0',
        'currency': 'RUB',
        'driver_profile_id': 'uuid1',
        'db_id': 'dbid1',
        'usages': [],
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


@pytest.mark.now('2018-08-20T10:00:00+0300')
@pytest.mark.config(
    WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00',
    WORKSHIFTS_TAGS_ENABLED=True,
    DRIVER_PROMOCODES_COMMISSION_TAGS=['commission_promocode'],
)
@pytest.mark.parametrize(
    'clid,uuid,db_id,expected_code,expected_response,' 'check_promocodes',
    [
        ('clid1', 'uuid1', 'dbid1', 200, None, True),
        ('clid2', 'uuid2', 'dbid2', 200, None, True),
        (
            'clid7',
            'uuid7',
            'dbid7',
            400,
            {'error': {'text': 'driver has active promocode'}},
            True,
        ),
        ('clid7', 'uuid7', 'dbid7', 200, None, False),
        pytest.param(
            'clid1',
            'uuid1',
            'dbid1',
            400,
            {'error': {'text': 'driver has active promocode v2'}},
            True,
            marks=pytest.mark.driver_tags_match(
                dbid='dbid1',
                uuid='uuid1',
                tags=['commission_promocode', 'tag0'],
            ),
        ),
    ],
    ids=[
        'with obsolete promocode',
        'with not activated promocode',
        'with active promocode',
        'config disabled',
        'with active promocode v2',
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_buy_workshift_promocode(
        taxi_protocol,
        mockserver,
        db,
        driver_info,
        config,
        clid,
        uuid,
        db_id,
        expected_code,
        expected_response,
        check_promocodes,
        individual_tariffs_switch_on,
):
    config.set_values(
        dict(
            WORKSHIFTS_CHECK_DRIVER_PROMOCODES=check_promocodes,
            WORKSHIFTS_CHECK_DRIVER_PROMOCODES_V2=check_promocodes,
        ),
    )

    params = {'db': db_id, 'session': 'session_id', 'version': '8.58 (850)'}
    json = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}

    driver_info.clid = clid
    driver_info.uuid = uuid
    driver_info.db_id = db_id

    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=params, json=json,
    )

    assert response.status_code == expected_code
    data = response.json()

    if response.status_code == 200:
        assert data['date_finish'] == '2018-08-21T07:00:00+0000'
        data = _get_driver_workshift(db, {'driver_id': clid + '_' + uuid})
        data.pop('_id')
        assert data == {
            'created': datetime.datetime(2018, 8, 20, 7, 0),
            'date_finish': datetime.datetime(2018, 8, 21, 7, 0),
            'driver_id': clid + '_' + uuid,
            'workshifts_counter': clid + '_' + uuid + ':0',
            'home_zone': 'moscow',
            'zones': ['moscow'],
            'tariffs': [],
            'workshift_id': 'workshift1',
            'price': '500',
            'park_price': '500',
            'hiring_price': '0',
            'without_vat': (
                '423.72881355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '423.72881355932203389830508474576271186440677966102'
            ),
            'hiring_without_vat': '0',
            'currency': 'RUB',
            'driver_profile_id': uuid,
            'db_id': db_id,
            'usages': [],
            'park_contract_currency': {
                'currency': 'RUB',
                'price': '500',
                'park_price': '500',
                'hiring_price': '0',
                'without_vat': (
                    '423.72881355932203389830508474576271186440677966102'
                ),
                'park_without_vat': (
                    '423.72881355932203389830508474576271186440677966102'
                ),
                'hiring_without_vat': '0',
            },
        }
    else:
        assert data == expected_response


@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.filldb(workshift_rules='match_experiment')
@pytest.mark.config(
    WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00',
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
)
@pytest.mark.parametrize(
    'tags_enabled,expected_code', [(True, 200), (False, 404)],
)
@pytest.mark.driver_tags_match(
    dbid='dbid1',
    uuid='uuid_tags',
    tags=['show_workshift0', 'show_workshift1'],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_buy_tags_service(
        taxi_protocol,
        db,
        config,
        driver_info,
        tags_enabled,
        expected_code,
        individual_tariffs_switch_on,
):
    config.set_values(dict(WORKSHIFTS_TAGS_ENABLED=tags_enabled))

    params = {'db': 'dbid1', 'session': 'session_id', 'version': '8.58 (850)'}
    json = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}

    driver_info.uuid = 'uuid_tags'
    driver_info.clid = 'clid1'

    response = taxi_protocol.post(
        'taximeter/buy-workshifts', params=params, json=json,
    )

    assert response.status_code == expected_code
    data = response.json()

    if response.status_code == 200:
        assert data['date_finish'] == '2017-04-26T13:00:00+0000'
        data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid_tags'})
        data.pop('_id')
        assert data == {
            'created': datetime.datetime(2017, 4, 25, 7, 0),
            'date_finish': datetime.datetime(2017, 4, 26, 13, 0),
            'driver_id': 'clid1_uuid_tags',
            'workshifts_counter': 'clid1_uuid_tags:0',
            'home_zone': 'moscow',
            'zones': ['moscow'],
            'tariffs': [],
            'workshift_id': 'workshift1',
            'price': '300',
            'park_price': '300',
            'hiring_price': '0',
            'without_vat': (
                '254.23728813559322033898305084745762711864406779661'
            ),
            'park_without_vat': (
                '254.23728813559322033898305084745762711864406779661'
            ),
            'hiring_without_vat': '0',
            'currency': 'RUB',
            'driver_profile_id': 'uuid_tags',
            'db_id': 'dbid1',
            'usages': [],
            'park_contract_currency': {
                'currency': 'RUB',
                'price': '300',
                'park_price': '300',
                'hiring_price': '0',
                'without_vat': (
                    '254.23728813559322033898305084745762711864406779661'
                ),
                'park_without_vat': (
                    '254.23728813559322033898305084745762711864406779661'
                ),
                'hiring_without_vat': '0',
            },
        }
    else:
        assert data == {
            'error': {
                'text': (
                    'Workshift availaible only for experiment: '
                    'show_workshift1'
                ),
            },
        }


@pytest.mark.now('2019-01-01T10:00:00+0300')
@pytest.mark.config(
    WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00',
    COUNTRY_VAT_BY_DATE={
        'rus': [
            {
                'end': '2019-01-01 00:00:00',
                'start': '1970-01-01 00:00:00',
                'value': 11800,
            },
            {
                'end': '2030-12-31 00:00:00',
                'start': '2019-01-01 00:00:00',
                'value': 12000,
            },
        ],
    },
)
def test_buy_workshift_vat(taxi_protocol, mockserver, db, driver_info):
    response = taxi_protocol.post(
        'taximeter/buy-workshifts',
        params={
            'db': 'dbid1',
            'session': 'session_id',
            'version': '8.58 (850)',
        },
        json={'home_zone': 'moscow', 'workshift_id': 'workshift3'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2019-01-02T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    assert (
        data['without_vat']
        == '416666.66666666666666666666666666666666666666666667'
    )


TVM_CONFIGS = {
    'TVM_ENABLED': True,
    'TVM_RULES': [{'src': 'mock', 'dst': 'protocol'}],
    'TVM_SERVICES': {'mock': 2020659, 'protocol': 13},
}


@pytest.mark.config(**TVM_CONFIGS)
@pytest.mark.driver_experiments('show_experiment1')
@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
def test_v2_buy_workshifts(taxi_protocol, load, db, driver_info):
    # to generate use `tvmknife unittest service --src 2020659 --dst 13`
    ticket = load('tvm2_ticket_2020659_13')
    headers_good = {'X-Ya-Service-Ticket': ticket}
    get_good = {
        'db': 'dbid1',
        'driver_profile_id': 'uuid1',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}
    headers_good = {'X-Ya-Service-Ticket': ticket}
    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    response = taxi_protocol.get(
        'taximeter/v2/buy-workshifts', params=get, headers=headers,
    )
    assert response.status_code == 405

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    del headers['X-Ya-Service-Ticket']
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 401

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    get['db'] = 'dbid222'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 404

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    post['home_zone'] = 'ekb'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 404

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    post['home_zone'] = 'spb'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 404

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    post['workshift_id'] = 'w'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 404

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2017-04-26T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_uuid1'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_uuid1',
        'workshifts_counter': 'clid1_uuid1:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': [],
        'workshift_id': 'workshift2',
        'price': '500000',
        'park_price': '560000',
        'hiring_price': '60000',
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '474576.27118644067796610169491525423728813559322034'
        ),
        'hiring_without_vat': (
            '50847.457627118644067796610169491525423728813559322'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'uuid1',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
        },
    }

    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 409

    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 409

    driver_info.uuid = 'with-rent-uuid'
    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    get['driver_profile_id'] = 'with-rent-uuid'
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['date_finish'] == '2017-04-26T07:00:00+0000'
    data = _get_driver_workshift(db, {'driver_id': 'clid1_with-rent-uuid'})
    data.pop('_id')
    assert data == {
        'created': datetime.datetime(2017, 4, 25, 7, 0),
        'date_finish': datetime.datetime(2017, 4, 26, 7, 0),
        'driver_id': 'clid1_with-rent-uuid',
        'workshifts_counter': 'clid1_with-rent-uuid:0',
        'home_zone': 'moscow',
        'zones': ['moscow'],
        'tariffs': [],
        'workshift_id': 'workshift2',
        'price': '500000',
        'park_price': '560000',
        'hiring_price': '60000',
        'without_vat': '423728.81355932203389830508474576271186440677966102',
        'park_without_vat': (
            '474576.27118644067796610169491525423728813559322034'
        ),
        'hiring_without_vat': (
            '50847.457627118644067796610169491525423728813559322'
        ),
        'currency': 'RUB',
        'driver_profile_id': 'with-rent-uuid',
        'db_id': 'dbid1',
        'usages': [],
        'park_contract_currency': {
            'currency': 'RUB',
            'price': '500000',
            'park_price': '560000',
            'hiring_price': '60000',
            'without_vat': (
                '423728.81355932203389830508474576271186440677966102'
            ),
            'park_without_vat': (
                '474576.27118644067796610169491525423728813559322034'
            ),
            'hiring_without_vat': (
                '50847.457627118644067796610169491525423728813559322'
            ),
        },
    }


@pytest.mark.config(**TVM_CONFIGS)
@pytest.mark.driver_experiments('show_experiment1')
@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(dbparks='clid2')
def test_v2_buy_workshifts_clid2(taxi_protocol, load, db, driver_info):
    ticket = load('tvm2_ticket_2020659_13')
    headers_good = {'X-Ya-Service-Ticket': ticket}
    get_good = {
        'db': 'dbid1',
        'driver_profile_id': 'uuid1',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}
    headers_good = {'X-Ya-Service-Ticket': ticket}

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 406

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    post['workshift_id'] = 'workshift1'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 200

    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 409


@pytest.mark.config(**TVM_CONFIGS)
@pytest.mark.driver_experiments('show_experiment1')
@pytest.mark.now('2017-04-25T10:00:00+0300')
@pytest.mark.config(WORKSHIFT_WITHOUT_VAT_START='2017-04-25 00:00:00')
@pytest.mark.filldb(dbparks='clid3')
def test_v2_buy_workshifts_clid3(taxi_protocol, load, db, driver_info):
    ticket = load('tvm2_ticket_2020659_13')
    headers_good = {'X-Ya-Service-Ticket': ticket}
    get_good = {
        'db': 'dbid1',
        'driver_profile_id': 'uuid1',
        'version': '8.58 (850)',
    }
    post_good = {'home_zone': 'moscow', 'workshift_id': 'workshift1'}
    headers_good = {'X-Ya-Service-Ticket': ticket}

    get, post, headers = get_good.copy(), post_good.copy(), headers_good.copy()
    post['workshift_id'] = 'workshift2'
    response = taxi_protocol.post(
        'taximeter/v2/buy-workshifts', params=get, json=post, headers=headers,
    )
    assert response.status_code == 406
