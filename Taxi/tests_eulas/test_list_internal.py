import operator

import pytest


SORT_KEY = operator.itemgetter('type')
URL = 'eulas/v1/list'

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
        URL, json={'filters': ['all'], 'yandex_uids': ['1234']},
    )

    assert response.status_code == 405, response.text


@pytest.mark.config(EULAS_SERVICE_ENABLED=False)
async def test_service_disabled(taxi_eulas):
    response = await taxi_eulas.post(
        URL, json={'filters': ['all'], 'yandex_uids': ['1234']},
    )

    assert response.status_code == 403, response.text
    assert response.json() == {'code': '403', 'message': 'Eulas: forbidden'}


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_simple(taxi_eulas, pgsql):
    """
    Config has 4 eulas: gdpr, eula, a, b
    User signed a, b.
    Handlers should return gdpr, eula
    """
    json = {
        'filters': ['unknown'],
        'zone_name': 'moscow',
        'country': 'rus',
        'consumer': 'zoneinfo',
        'yandex_uids': ['1'],
    }
    headers = {'Accept-Language': 'en'}

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
async def test_filters(taxi_eulas, pgsql, filters, expected_response):
    json = {
        'filters': filters,
        'zone_name': 'moscow',
        'country': 'rus',
        'consumer': 'zoneinfo',
        'yandex_uids': ['1'],
    }
    headers = {'Accept-Language': 'en'}
    response = await taxi_eulas.post(URL, json=json, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.parametrize(
    'request_update, config_update, expected_response',
    [
        ({}, {'zones': []}, get_eulas_response(['gdpr'])),
        ({'zone_name': 'moscow'}, {'zones': []}, get_eulas_response(['gdpr'])),
        ({}, {'zones': ['moscow']}, get_eulas_response([])),
        (
            {'zone_name': 'moscow'},
            {
                'zones': ['moscow'],
                'consumers': ['zoneinfo'],
                'yandex_uids': ['1'],
            },
            get_eulas_response([]),
        ),
        (
            {'zone_name': 'moscow'},
            {'zones': ['piter', 'moscow']},
            get_eulas_response(['gdpr']),
        ),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_zonename_filter(
        taxi_eulas,
        taxi_config,
        request_update,
        config_update,
        expected_response,
):
    """
    Check filtration by zone_name
    """
    headers = {'Accept-Language': 'en'}
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

    request_body = {'filters': ['unknown'], 'yandex_uids': ['1']}
    request_body.update(request_update)

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
        ({}, {'countries': []}, get_eulas_response(['gdpr'])),
        ({'country': 'rus'}, {'countries': []}, get_eulas_response(['gdpr'])),
        ({}, {'countries': ['rus']}, get_eulas_response([])),
        (
            {'country': 'rus'},
            {
                'countries': ['rus'],
                'consumers': ['zoneinfo'],
                'yandex_uids': ['1'],
            },
            get_eulas_response([]),
        ),
        (
            {'country': 'rus'},
            {'countries': ['rus', 'usa']},
            get_eulas_response(['gdpr']),
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
):
    """
    Check filtration by zone_name
    """
    headers = {'Accept-Language': 'en'}
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

    request_body = {'filters': ['unknown'], 'yandex_uids': ['1']}
    request_body.update(request_update)

    taxi_config.set_values(dict(EULAS=eulas_config))
    response = await taxi_eulas.post(URL, json=request_body, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.parametrize(
    'request_update, config_update, samples',
    [
        ({}, {}, ['gdpr']),
        ({}, {'countries': ['rus']}, []),
        ({}, {'zones': ['moscow']}, []),
        ({}, {'countries': ['rus'], 'zones': ['kiev']}, []),
        ({}, {'countries': ['rus'], 'zones': ['moscow']}, []),
        ({'zone_name': 'moscow'}, {}, ['gdpr']),
        ({'zone_name': 'moscow'}, {'countries': ['rus']}, []),
        ({'zone_name': 'moscow'}, {'zones': ['moscow']}, ['gdpr']),
        (
            {'zone_name': 'moscow'},
            {'countries': ['rus'], 'zones': ['kiev']},
            [],
        ),
        (
            {'zone_name': 'moscow'},
            {'countries': ['rus'], 'zones': ['moscow']},
            [],
        ),
        ({'country': 'rus'}, {}, ['gdpr']),
        ({'country': 'rus'}, {'countries': ['rus']}, ['gdpr']),
        ({'country': 'rus'}, {'zones': ['moscow']}, []),
        (
            {'country': 'rus'},
            {'countries': ['rus'], 'zones': ['kiev']},
            ['gdpr'],
        ),
        (
            {'country': 'rus'},
            {'countries': ['rus'], 'zones': ['moscow']},
            ['gdpr'],
        ),
        ({'country': 'rus', 'zone_name': 'moscow'}, {}, ['gdpr']),
        (
            {'country': 'rus', 'zone_name': 'moscow'},
            {'countries': ['rus']},
            ['gdpr'],
        ),
        (
            {'country': 'rus', 'zone_name': 'moscow'},
            {'zones': ['moscow']},
            ['gdpr'],
        ),
        (
            {'country': 'rus', 'zone_name': 'moscow'},
            {'countries': ['rus'], 'zones': ['kiev']},
            ['gdpr'],
        ),
        (
            {'country': 'rus', 'zone_name': 'moscow'},
            {'countries': ['rus'], 'zones': ['moscow']},
            ['gdpr'],
        ),
        ({'country': 'rus', 'zone_name': 'kiev'}, {}, ['gdpr']),
        (
            {'country': 'rus', 'zone_name': 'kiev'},
            {'countries': ['rus']},
            ['gdpr'],
        ),
        ({'country': 'rus', 'zone_name': 'kiev'}, {'zones': ['moscow']}, []),
        (
            {'country': 'rus', 'zone_name': 'kiev'},
            {'countries': ['rus'], 'zones': ['kiev']},
            ['gdpr'],
        ),
        (
            {'country': 'rus', 'zone_name': 'kiev'},
            {'countries': ['rus'], 'zones': ['moscow']},
            ['gdpr'],
        ),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_country_zone_combination(
        taxi_eulas,
        taxi_config,
        taxi_tariffs,
        request_update,
        config_update,
        samples,
):
    """
    Check filtration by zone_name
    """
    headers = {'Accept-Language': 'en'}
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

    request_body = {'filters': ['unknown'], 'yandex_uids': ['1']}
    request_body.update(request_update)

    taxi_config.set_values(dict(EULAS=eulas_config))
    response = await taxi_eulas.post(URL, json=request_body, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response = get_eulas_response(samples)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.parametrize(
    'request_body, config_update, expected_response',
    [
        (
            {'filters': ['unknown'], 'yandex_uids': ['1']},
            {'consumers': []},
            get_eulas_response(['gdpr']),
        ),
        (
            {
                'filters': ['unknown'],
                'consumer': 'zoneinfo',
                'yandex_uids': ['1'],
            },
            {'consumers': []},
            get_eulas_response(['gdpr']),
        ),
        (
            {
                'filters': ['unknown'],
                'consumer': 'zoneinfo',
                'yandex_uids': ['1'],
            },
            {'consumers': ['launch', 'zoneinfo']},
            get_eulas_response(['gdpr']),
        ),
        (
            {'filters': ['unknown'], 'yandex_uids': ['1']},
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
):
    """
    Check filtration by consumer
    """
    headers = {'Accept-Language': 'en'}
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


@pytest.mark.experiments3(filename='test_experiments3.json')
@pytest.mark.parametrize(
    'match_enabled,application',
    [
        (True, {'name': 'android', 'version': [1, 1, 1]}),
        (False, {'name': 'iphone', 'version': [1, 1, 1]}),
        (False, {'name': 'android', 'version': [4, 0, 0]}),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_experiments_filter(
        taxi_eulas, taxi_config, taxi_tariffs, match_enabled, application,
):
    headers = {'Accept-Language': 'en'}
    request_body = {
        'filters': ['unknown'],
        'application': {**application, 'platform_version': [1, 1, 1]},
        'zone_name': 'moscow',
        'consumer': 'zoneinfo',
        'yandex_uids': ['1'],
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


@pytest.mark.config(
    EULAS={
        'gdpr': {
            'accept_button_key': 'accept.title',
            'cancel_button_key': 'cancel.title',
            'consumer': ['zoneinfo'],
            'content_key': 'eulas.gdpr.content',
            'title_key': 'eulas.gdpr.title',
            'ttl_accepted': 365,
            'ttl_rejected': 180,
            'zones': ['moscow'],
        },
    },
)
@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.parametrize(
    'locale, translation',
    [
        ('', get_eulas_response(['default_gdpr'])),
        ('ru', get_eulas_response(['default_gdpr'])),
        ('en', get_eulas_response(['gdpr'])),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_locale(taxi_eulas, locale, translation):
    json = {
        'filters': ['unknown'],
        'zone_name': 'moscow',
        'consumer': 'zoneinfo',
        'yandex_uids': ['1'],
    }
    headers = {'Accept-Language': locale}

    response = await taxi_eulas.post(URL, json=json, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    assert data == translation


@pytest.mark.parametrize('show', [None, True, False])
async def test_show_eulas_for_unauthorized(taxi_eulas, taxi_config, show):
    headers = {'Accept-Language': 'en'}
    request_body = {'filters': ['unknown']}
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
    if show is not None:
        eulas_config['gdpr']['show_for_unauthorized'] = show

    taxi_config.set_values(dict(EULAS=eulas_config))
    response = await taxi_eulas.post(URL, json=request_body, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()
    assert (
        data == get_eulas_response(['gdpr'])
        if show is True
        else get_eulas_response([])
    )


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.pgsql('eulas', files=['users.sql'])
@pytest.mark.config(
    EULAS={
        'gdpr': {
            'accept_button_key': 'accept.title',
            'cancel_button_key': 'cancel.title',
            'consumer': ['zoneinfo'],
            'content_key': 'eulas.gdpr.content',
            'title_key': 'eulas.gdpr.title',
            'ttl_accepted': 365,
            'ttl_rejected': 180,
            'zones': ['moscow'],
        },
    },
)
async def test_good_request(taxi_eulas):
    json = {
        'filters': ['unknown'],
        'zone_name': 'moscow',
        'yandex_uids': ['1'],
    }
    response = await taxi_eulas.post(URL, json=json)
    expected_response = get_eulas_response(['gdpr'])

    assert response.status_code == 200, response.text

    data = response.json()
    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.parametrize('missing_field', ['filters'])
async def test_4xx_on_missing_required_field(taxi_eulas, missing_field):
    json = {'filters': ['unknown'], 'yandex_uids': ['1']}
    json.pop(missing_field)
    response = await taxi_eulas.post(URL, json=json)

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


@pytest.mark.parametrize('field', ['filters', 'yandex_uids'])
async def test_4xx_on_required_list_has_zero_len(taxi_eulas, field):
    json = {'filters': ['unknown'], 'yandex_uids': ['1'], field: []}
    response = await taxi_eulas.post(URL, json=json)

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


@pytest.mark.parametrize('field', ['consumer', 'zone_name'])
async def test_4xx_on_int_instead_of_string(taxi_eulas, field):
    json = {'filters': ['unknown'], 'yandex_uids': ['1'], field: 10}
    response = await taxi_eulas.post(URL, json=json)

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'


async def test_4xx_on_unexpected_filter(taxi_eulas):
    response = await taxi_eulas.post(
        URL,
        json={'filters': ['gg'], 'yandex_uids': ['1'], 'zone_name': 'moscow'},
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'
