import operator

import pytest


SORT_KEY = operator.itemgetter('type')
URL = '4.0/eulas/v1/list'

YANDEX_UID = 0
EULA_TYPE = 1

RESPONSE_SAMPLES = {
    'default_eula': {
        'show_on_action': True,
        'type': 'eula',
        'title': 'default eula title',
        'content': 'default eula content',
        'accept_button_title': 'accept',
        'cancel_button_title': 'cancel',
        'header_image_tag': 'eula_image',
        'ttl': 260,
    },
    'eula': {
        'show_on_action': True,
        'type': 'eula',
        'title': 'en eula title',
        'content': 'en eula content',
        'accept_button_title': 'accept',
        'cancel_button_title': 'cancel',
        'header_image_tag': 'eula_image',
        'ttl': 260,
    },
    'default_gdpr': {
        'show_on_action': False,
        'type': 'gdpr',
        'title': 'default gdpr title',
        'content': 'default gdpr content',
        'accept_button_title': 'accept',
        'cancel_button_title': 'cancel',
        'ttl': 365,
    },
    'gdpr': {
        'show_on_action': False,
        'type': 'gdpr',
        'title': 'en gdpr title',
        'content': 'en gdpr content',
        'accept_button_title': 'accept',
        'cancel_button_title': 'cancel',
        'ttl': 365,
    },
    'a': {
        'show_on_action': True,
        'type': 'a',
        'title': 'en a title',
        'content': 'en a content',
        'accept_button_title': 'accept',
        'cancel_button_title': 'cancel',
        'ttl': 365,
        'yandex_uid': '1',
        'status': 'accepted',
        'valid_till': '2019-01-01T16:11:13+0000',
        'signed_at': '2018-01-01T16:11:13+0000',
    },
    'b': {
        'show_on_action': False,
        'type': 'b',
        'title': 'en b title',
        'content': 'en b content',
        'accept_button_title': 'accept',
        'cancel_button_title': 'cancel',
        'ttl': 790,
        'yandex_uid': '1',
        'status': 'rejected',
        'valid_till': '2019-03-02T16:11:13+0000',
        'signed_at': '2017-01-01T16:11:13+0000',
    },
}


def get_eulas_response(eulas):
    return {'eulas': [RESPONSE_SAMPLES[eula] for eula in eulas]}


async def test_get_not_allowed(taxi_eulas):
    response = await taxi_eulas.get(
        URL, json={'filters': ['all']}, headers={'X-Yandex-UID': '1234'},
    )

    assert response.status_code == 405, response.text


@pytest.mark.config(EULAS_SERVICE_ENABLED=False)
async def test_service_disabled(taxi_eulas):
    response = await taxi_eulas.post(
        URL, json={'filters': ['all']}, headers={'X-Yandex-UID': '1234'},
    )

    assert response.status_code == 403, response.text
    assert response.json() == {'code': '403', 'message': 'Eulas: forbidden'}


async def test_unauthorized(taxi_eulas):
    """
    no header X-Yandex-UID
    """
    response = await taxi_eulas.post(URL, json={'filters': ['all']})

    assert response.status_code == 401, response.text
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_simple(taxi_eulas, pgsql, taxi_tariffs):
    """
    Config has 4 eulas: gdpr, eula, a, b
    User signed a, b.
    Handlers should return gdpr, eula
    """
    json = {
        'filters': ['unknown'],
        'zone_name': 'moscow',
        'consumer': 'zoneinfo',
    }
    headers = {'X-Yandex-UID': '1', 'Accept-Language': 'en'}

    def get_users():
        cursor = pgsql['eulas'].cursor()
        cursor.execute('SELECT * FROM eulas.users')
        result = list((row[YANDEX_UID], row[EULA_TYPE]) for row in cursor)
        cursor.close()
        return result

    assert get_users() == [('1', 'a'), ('1', 'b'), ('2', 'b'), ('3', 'c')]

    response = await taxi_eulas.post(URL, json=json, headers=headers)
    expected_response = get_eulas_response(['gdpr', 'eula'])

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.parametrize(
    'filters, expected_response',
    [
        (['unknown'], get_eulas_response(['gdpr', 'eula'])),
        (['signed'], get_eulas_response(['a', 'b'])),
        (['accepted'], get_eulas_response(['a'])),
        (['rejected'], get_eulas_response(['b'])),
        (['all'], get_eulas_response(['gdpr', 'eula', 'a', 'b'])),
        (
            ['signed', 'unknown'],
            get_eulas_response(['gdpr', 'eula', 'a', 'b']),
        ),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_filters(
        taxi_eulas, pgsql, filters, expected_response, taxi_tariffs,
):
    json = {'filters': filters, 'zone_name': 'moscow', 'consumer': 'zoneinfo'}
    headers = {'X-Yandex-UID': '1', 'Accept-Language': 'en'}
    response = await taxi_eulas.post(URL, json=json, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.parametrize(
    'request_body, config_update, expected_response',
    [
        (
            {'filters': ['unknown'], 'zone_name': 'moscow', 'country': 'rus'},
            {'zones': ['moscow'], 'consumers': ['zoneinfo']},
            get_eulas_response([]),
        ),
        (
            {'filters': ['unknown']},
            {'zones': []},
            get_eulas_response(['gdpr']),
        ),
        (
            {'filters': ['unknown'], 'zone_name': 'moscow'},
            {'zones': []},
            get_eulas_response(['gdpr']),
        ),
        (
            {'filters': ['unknown'], 'zone_name': 'moscow'},
            {'zones': ['piter', 'moscow']},
            get_eulas_response(['gdpr']),
        ),
        (
            {'filters': ['unknown']},
            {'zones': ['moscow']},
            get_eulas_response([]),
        ),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_zonename_filter(
        taxi_eulas,
        taxi_config,
        request_body,
        config_update,
        expected_response,
        taxi_tariffs,
):
    """
    Check filtration by zone_name
    """
    headers = {'X-Yandex-UID': '1', 'Accept-Language': 'en'}
    eulas_config = {
        'gdpr': {
            'title_key': 'eulas.gdpr.title',
            'content_key': 'eulas.gdpr.content',
            'accept_button_key': 'accept.title',
            'cancel_button_key': 'cancel.title',
            'ttl_accepted': 365,
            'ttl_rejected': 180,
        },
    }
    eulas_config['gdpr'].update(config_update)
    taxi_config.set_values(dict(EULAS=eulas_config))
    response = await taxi_eulas.post(URL, json=request_body, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.parametrize(
    'request_body, config_update, expected_response',
    [
        (
            {'filters': ['unknown']},
            {'consumers': []},
            get_eulas_response(['gdpr']),
        ),
        (
            {'filters': ['unknown'], 'consumer': 'zoneinfo'},
            {'consumers': []},
            get_eulas_response(['gdpr']),
        ),
        (
            {'filters': ['unknown'], 'consumer': 'zoneinfo'},
            {'consumers': ['launch', 'zoneinfo']},
            get_eulas_response(['gdpr']),
        ),
        (
            {'filters': ['unknown']},
            {'consumers': ['zoneinfo']},
            get_eulas_response([]),
        ),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_consumers_filter(
        taxi_eulas,
        taxi_config,
        request_body,
        config_update,
        expected_response,
        taxi_tariffs,
):
    """
    Check filtration by consumer
    """
    headers = {'X-Yandex-UID': '1', 'Accept-Language': 'en'}
    eulas_config = {
        'gdpr': {
            'title_key': 'eulas.gdpr.title',
            'content_key': 'eulas.gdpr.content',
            'accept_button_key': 'accept.title',
            'cancel_button_key': 'cancel.title',
            'ttl_accepted': 365,
            'ttl_rejected': 180,
        },
    }
    eulas_config['gdpr'].update(config_update)
    taxi_config.set_values(dict(EULAS=eulas_config))
    response = await taxi_eulas.post(URL, json=request_body, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.parametrize(
    'request_update, config_update, expected_response',
    [
        (
            {'zone_name': 'moscow'},
            {'countries': ['rus']},
            get_eulas_response(['gdpr']),
        ),
        (
            {'zone_name': 'moscow'},
            {'countries': ['usa']},
            get_eulas_response([]),
        ),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_country_filter(
        taxi_eulas,
        taxi_config,
        request_update,
        config_update,
        expected_response,
        taxi_tariffs,
):
    """
    Check filtration by country
    """
    headers = {'X-Yandex-UID': '1', 'Accept-Language': 'en'}
    eulas_config = {
        'gdpr': {
            'title_key': 'eulas.gdpr.title',
            'content_key': 'eulas.gdpr.content',
            'accept_button_key': 'accept.title',
            'cancel_button_key': 'cancel.title',
            'ttl_accepted': 365,
            'ttl_rejected': 180,
            **config_update,
        },
    }
    request_body = {'filters': ['unknown'], **request_update}
    taxi_config.set_values(dict(EULAS=eulas_config))

    response = await taxi_eulas.post(URL, json=request_body, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.experiments3(filename='test_experiments3.json')
@pytest.mark.parametrize(
    'match_enabled,application',
    [
        (True, 'app_name=android,app_ver1=1,app_ver2=1,app_ver3=1'),
        (False, 'app_name=iphone,app_ver1=1,app_ver2=1,app_ver3=1'),
        (False, 'app_name=android,app_ver1=4,app_ver2=0,app_ver3=0'),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_experiments_filter(
        taxi_eulas, taxi_config, taxi_tariffs, match_enabled, application,
):
    headers = {
        'X-Yandex-UID': '1',
        'X-Request-Application': application,
        'Accept-Language': 'en',
    }
    request_body = {
        'filters': ['unknown'],
        'zone_name': 'moscow',
        'consumer': 'zoneinfo',
    }

    eulas_config = {
        'gdpr': {
            'title_key': 'eulas.gdpr.title',
            'content_key': 'eulas.gdpr.content',
            'accept_button_key': 'accept.title',
            'cancel_button_key': 'cancel.title',
            'ttl_accepted': 365,
            'ttl_rejected': 180,
            'experiments3': 'gdpr_config',
        },
    }
    taxi_config.set_values(dict(EULAS=eulas_config))
    response = await taxi_eulas.post(URL, json=request_body, headers=headers)
    expected_response = get_eulas_response(['gdpr'] if match_enabled else [])

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.parametrize(
    'locale, expected_response',
    [
        ('', get_eulas_response(['default_eula', 'default_gdpr'])),
        ('ru', get_eulas_response(['default_eula', 'default_gdpr'])),
        ('en', get_eulas_response(['eula', 'gdpr'])),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_locale(taxi_eulas, locale, expected_response, taxi_tariffs):
    json = {
        'filters': ['unknown'],
        'zone_name': 'moscow',
        'consumer': 'zoneinfo',
    }
    headers = {'X-Yandex-UID': '1', 'Accept-Language': locale}

    response = await taxi_eulas.post(URL, json=json, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_eulas_takes_country_by_zone_name(
        taxi_tariffs, taxi_config, taxi_eulas,
):
    eulas_config = {
        'gdpr': {
            'title_key': 'eulas.gdpr.title',
            'content_key': 'eulas.gdpr.content',
            'accept_button_key': 'accept.title',
            'cancel_button_key': 'cancel.title',
            'ttl_accepted': 365,
            'ttl_rejected': 180,
            'countries': ['rus'],
        },
    }
    taxi_config.set_values(dict(EULAS=eulas_config))

    headers = {'X-Yandex-UID': '1', 'Accept-Language': 'en'}
    json = {'filters': ['unknown'], 'zone_name': 'moscow'}
    response = await taxi_eulas.post(URL, json=json, headers=headers)
    expected_data = get_eulas_response(['gdpr'])
    assert response.status_code == 200, response.text

    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_data['eulas'].sort(key=SORT_KEY)
    assert data == expected_data


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_good_request(taxi_eulas, taxi_tariffs):
    expected_response = get_eulas_response(['gdpr', 'eula'])
    response = await taxi_eulas.post(
        URL,
        json={'filters': ['unknown'], 'zone_name': 'moscow'},
        headers={'X-Yandex-UID': '1'},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


async def test_4xx_without_uid(taxi_eulas):
    response = await taxi_eulas.post(
        URL, json={'filters': []}, headers={'X-Yandex-UID': ''},
    )

    assert response.status_code == 401, response.text
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_4xx_without_filters(taxi_eulas):
    response = await taxi_eulas.post(
        URL, json={}, headers={'X-Yandex-UID': '1'},
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


async def test_4xx_on_zero_filters_len(taxi_eulas):
    response = await taxi_eulas.post(
        URL,
        json={'filters': [], 'zone_name': 'moscow'},
        headers={'X-Yandex-UID': '1'},
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


async def test_4xx_on_unexpected_filter(taxi_eulas):
    response = await taxi_eulas.post(
        URL,
        json={'filters': ['gg'], 'zone_name': 'moscow'},
        headers={'X-Yandex-UID': '1'},
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


@pytest.mark.parametrize('field', ['zone_name', 'consumer'])
async def test_4xx_on_incorrect_field_type(taxi_eulas, field):
    response = await taxi_eulas.post(
        URL,
        json={'filters': ['unknown'], field: 5},
        headers={'X-Yandex-UID': '1'},
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'
