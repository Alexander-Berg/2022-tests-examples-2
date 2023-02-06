import pytest

URL = '/4.0/layers/v1/organization'

DEFAULT_APPLICATION = (
    'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=4,app_brand=yataxi'
)

USER_ID = '12345678901234567890123456789012'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-AppMetrica-UUID': 'UUID',
}

NOT_AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': '',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-AppMetrica-UUID': 'UUID',
}


def make_request(qr_id=None, oid=None, location=None):
    state = {}
    if location is not None:
        state['location'] = location
    if qr_id is not None:
        return {
            'id': {'type': 'qr', 'value': qr_id},
            'mode': 'suggest',
            'state': state,
        }
    if oid is not None:
        return {
            'id': {'type': 'geosearch', 'value': oid},
            'mode': 'suggest',
            'state': state,
        }
    raise Exception('some request info is missing')


L10N_QR_PAYMENT = {'restaurants.khleb.title': {'ru': 'Хлеб Насущный'}}

L10N_CLIENT_MESSAGES = {
    'qr.scan_title': {'ru': 'Вкусно покушал, хочу кэшбэк'},
    'qr.ride_title': {'ru': 'Го кушац'},
    'qr.not_found_title': {'ru': 'Этого ресторана не существует'},
    'qr.not_found_subtitle': {'ru': 'Быть может, обновление все починит'},
}

L10N = {'qr_payment': L10N_QR_PAYMENT, 'client_messages': L10N_CLIENT_MESSAGES}


@pytest.mark.experiments3(
    filename='experiments3_layers_organization_card.json',
)
@pytest.mark.translations(**L10N)
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
@pytest.mark.parametrize('qr_id', ['hleb_nasushny_000', 'restaurant01'])
async def test_v1_organization_simple(taxi_layers, load_json, qr_id, yamaps):
    response = await taxi_layers.post(
        URL, make_request(qr_id=qr_id), headers=AUTHORIZED_HEADERS,
    )
    expected_organization = load_json('expected_organizations_qr_cache.json')[
        qr_id
    ]
    assert response.status_code == 200
    assert response.json() == {'organization': expected_organization}
    assert yamaps.times_called() == 1


@pytest.mark.experiments3(
    filename='experiments3_layers_organization_card.json',
)
@pytest.mark.translations(**L10N)
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
@pytest.mark.parametrize(
    'params, requested_oid',
    [
        ({'qr_id': 'restaurant01'}, '1187143299'),
        ({'oid': '123123'}, '123123'),
        ({'oid': '123123', 'location': [13.37, 3.22]}, '123123'),
    ],
)
async def test_v1_organization_yamaps(
        taxi_layers, load_json, yamaps, params, requested_oid,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))
    checks = {'business_oid': requested_oid}
    if 'location' in params:
        checks['ull'] = '13.370000,3.220000'
    yamaps.set_checks(checks)

    response = await taxi_layers.post(
        URL, make_request(**params), headers=AUTHORIZED_HEADERS,
    )
    expected_organization = load_json('expected_organizations_yamaps.json')[
        'restaurant01'
    ]
    assert response.status_code == 200
    assert response.json() == {'organization': expected_organization}
    assert yamaps.times_called() == 1


@pytest.mark.experiments3(
    filename='experiments3_layers_organization_card.json',
)
@pytest.mark.translations(**L10N)
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
@pytest.mark.config(MAPS_QR_PAYMENT_SNIPPET='ololo')
async def test_v1_organization_yamaps_custom_snippet(
        taxi_layers, load_json, yamaps,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))
    yamaps.set_checks({'snippets': 'photos/2.x,ololo'})

    response = await taxi_layers.post(
        URL, make_request(oid='123'), headers=AUTHORIZED_HEADERS,
    )
    expected_organization = load_json('expected_organizations_yamaps.json')[
        'restaurant01'
    ]
    # mock did not return snippet named ololo, so cashback is not filled
    del expected_organization['list_items'][0]['trail']['cashback']
    assert response.status_code == 200
    assert response.json() == {'organization': expected_organization}
    assert yamaps.times_called() == 1


@pytest.mark.experiments3(
    filename='experiments3_layers_organization_card.json',
)
@pytest.mark.translations(**L10N)
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
@pytest.mark.parametrize('id_type', ['qr_id', 'oid'])
async def test_v1_organization_nonexisting(taxi_layers, yamaps, id_type):
    response = await taxi_layers.post(
        URL, make_request(**{id_type: 'ehe'}), headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'organization_not_found',
        'message': 'Этого ресторана не существует',
        'details': {'subtitle': 'Быть может, обновление все починит'},
    }
    assert yamaps.times_called() == int(id_type == 'oid')
