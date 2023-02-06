import pytest


def get_proc(order_id, status, taxi_status, performer_found):
    proc = {
        '_id': order_id,
        'order': {
            'status': status,
            'taxi_status': taxi_status,
            'request': {
                'corp': {'client_id': '5e36732e2bc54e088b1466e08e31c486'},
                'class': ['courier'],
                'source': {
                    'uris': ['some uri'],
                    'geopoint': [37.642859, 55.735316],
                    'fullname': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'description': 'Москва, Россия',
                    'porchnumber': '4',
                    'extra_data': {},
                },
                'destinations': [
                    {
                        'uris': ['some uri'],
                        'geopoint': [38.642859, 56.735316],
                        'fullname': 'Россия, Москва, Садовническая улица 82',
                        'short_text': 'БЦ Аврора',
                        'description': 'Москва, Россия',
                        'porchnumber': '4',
                        'extra_data': {},
                    },
                ],
            },
        },
        'candidates': [
            {
                'first_name': 'Иван',
                'name': 'Petr',
                'phone_personal_id': '+7123_id',
                'driver_id': 'clid_driverid1',
                'db_id': 'parkid1',
                'car_model': 'BMW',
                'car_number': 'A001AA77',
            },
        ],
        'performer': {},
    }
    if performer_found:
        proc['performer'] = {'candidate_index': 0}
    return proc


@pytest.fixture(name='mock_vgw', autouse=True)
def _mock_vgw(mockserver, load_json):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_request(request):
        if context.expected_request:
            req_json = request.json
            req_json.pop('nonce')
            assert request.json == context.expected_request
        resp = {
            'phone': '+71234567890',
            'ext': '101',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }
        return mockserver.make_response(json=resp)

    class Context:
        def __init__(self):
            self.expected_request = None

    context = Context()
    return context


async def test_taxi_voiceforwarding(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_id = get_default_order_id()
    order_archive_mock.set_order_proc(
        get_proc(order_id, 'assigned', 'driving', True),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={'delivery_id': 'taxi/' + order_id, 'forwarding_id': 'performer'},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['ext'] == '101'
    assert response.json()['phone'] == '+71234567890'


async def test_taxi_voiceforwarding_without_performer(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_id = get_default_order_id()
    order_archive_mock.set_order_proc(
        get_proc(order_id, 'assigned', 'driving', False),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={'delivery_id': 'taxi/' + order_id, 'forwarding_id': 'performer'},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 404


async def test_c2c_voiceforwarding(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        load_json,
        mock_claims_full,
):
    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'forwarding_id': 'performer',
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['ext'] == '101'
    assert response.json()['phone'] == '+71234567890'


async def test_c2c_voiceforwarding_without_performer(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        load_json,
        mock_claims_full,
):
    mock_claims_full.file_name = 'claim_full_response_without_performer.json'
    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'forwarding_id': 'performer',
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 404


async def test_cargo_claims_voiceforwarding(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mock_claims_full,
):
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
            'forwarding_id': 'performer',
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['ext'] == '101'
    assert response.json()['phone'] == '+71234567890'


async def test_cargo_claims_voiceforwarding_without_performer(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mock_claims_full,
):
    mock_claims_full.file_name = 'claim_full_response_without_performer.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
            'forwarding_id': 'performer',
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 404


@pytest.mark.parametrize('file_name', ['delivering.json', 'delivered.json'])
@pytest.mark.experiments3(filename='experiment.json')
async def test_logistic_platform_voiceforwarding(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mock_claims_full,
        file_name,
        mock_logistic_platform,
        mock_order_statuses_history,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = file_name
    mock_order_statuses_history.file_name = file_name
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={
            'delivery_id': 'logistic-platform/' + get_default_order_id(),
            'forwarding_id': 'performer',
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['ext'] == '101'
    assert response.json()['phone'] == '+71234567890'


@pytest.mark.parametrize(
    'file_name',
    ['in_middle_node.json', 'order_created.json', 'cancelled.json'],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_logistic_platform_without_performer(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_driver_trackstory,
        mock_order_statuses_history,
        mock_logistic_platform,
        file_name,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = file_name
    mock_order_statuses_history.file_name = file_name
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/voiceforwarding',
        json={
            'delivery_id': 'logistic-platform/' + get_default_order_id(),
            'forwarding_id': 'performer',
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 404
