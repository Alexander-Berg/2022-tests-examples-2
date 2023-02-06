import pytest


def _is_feature_present(full_response, expected_feature):
    claim_features = set(
        feature['id'] for feature in full_response['features']
    )
    return expected_feature in claim_features


def _c2c_create_event(corp_client_id=None, phoenix_claim=False):
    event = {
        'kind': 'status-change-requested',
        'status': 'accepted',
        'data': {
            'claim_version': 1,
            'accept_language': 'ru',
            'accept_as_create_event': True,
            'claim_revision': 1,
            'is_terminal': False,
            'phoenix_claim': phoenix_claim,
            'claim_origin': 'yandexgo',
            'skip_client_notify': False,
            'claim_accepted': True,
            'offer_id': 'cargo-pricing/v1/123',
            'notify_pricing_claim_accepted': True,
        },
    }
    if corp_client_id:
        event['data']['corp_client_id'] = corp_client_id
    return event


@pytest.mark.parametrize(
    'payment_type, payment_method_id, payment_scheme',
    [
        ('cash', None, 'cash'),
        ('card', 'card-xef3bda890c0555a6b47f8654', 'individual'),
        ('cargocorp', 'cargocorp:{}:card:456:789', 'corp_agent'),
        ('cargocorp', 'cargocorp:{}:balance:456:contract:789', 'decoupling'),
    ],
)
async def test_create_c2c(
        taxi_cargo_claims,
        get_full_claim,
        create_default_cargo_c2c_order,
        mock_create_event,
        get_default_headers,
        payment_type,
        payment_method_id,
        payment_scheme,
        pgsql,
        mock_cargo_corp_up,
        mock_cargo_finance,
        get_default_corp_client_id,
):
    if payment_scheme == 'decoupling':
        mock_cargo_corp_up.is_agent_scheme = False
    corp_client_id = None
    if payment_type == 'cargocorp':
        corp_client_id = get_default_corp_client_id
        payment_method_id = payment_method_id.format(corp_client_id)
    mock_cargo_finance.method_id = payment_method_id

    mock_create_event(
        idempotency_token='accept_1',
        event=_c2c_create_event(
            corp_client_id, payment_scheme == 'corp_agent',
        ),
    )

    claim = await create_default_cargo_c2c_order(
        payment_type=payment_type,
        payment_method_id=payment_method_id,
        skip_mock_create_event=True,
    )

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        headers=get_default_headers(),
        params={'claim_id': claim.claim_id},
    )
    assert response.status_code == 200
    response = response.json()

    calc_id = response['taxi_offer']['offer_id']

    expected_c2c_data = {
        'payment_method_id': payment_method_id,
        'payment_type': payment_type,
        'cargo_c2c_order_id': 'cargo_c2c_order_id',
    }
    if payment_method_id is None:
        del expected_c2c_data['payment_method_id']
    assert response['c2c_data'] == expected_c2c_data
    assert response['yandex_uid'] == 'user_id'
    assert response['initiator_yandex_uid'] == 'user_id'
    assert response.get('corp_client_id', None) == corp_client_id

    assert response['status'] == 'accepted'
    assert response['dispatch_flow'] == 'newway'
    if payment_scheme == 'decoupling':
        assert response['just_client_payment']
        assert response['is_new_logistic_contract']
    else:
        assert not response.get('just_client_payment', None)
    assert calc_id == 'cargo-pricing/v1/123'
    assert response['taxi_requirements'] == {'door_to_door': True}
    assert response['matched_cars'] == [
        {'door_to_door': True, 'taxi_class': 'express'},
    ]
    if payment_scheme == 'corp_agent':
        assert response['pricing_payment_methods'] == {
            'card': {'cardstorage_id': '789', 'owner_yandex_uid': '456'},
        }
    else:
        assert 'pricing_payment_methods' not in response

    if payment_scheme == 'decoupling':
        assert response['pricing']['offer']['price'] == '1198.8012'
        assert response['pricing']['final_price'] == '1198.8012'
    else:
        assert response['pricing']['offer']['price'] == '999.0010'
        assert response['pricing']['final_price'] == '999.0010'

    for point in response['route_points']:
        assert point['address']['description'] == 'some description'
    assert response['origin_info'] == {
        'origin': 'yandexgo',
        'displayed_origin': 'Яндекс GO',
        'user_agent': 'Mozilla',
    }
    assert response['customer_ip'] == '1.1.1.1'

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute('select is_delayed from cargo_claims.claims')
    assert list(cursor) == [(False,)]

    assert _is_feature_present(response, 'c2c_interface')
    if payment_scheme == 'corp_agent':
        assert _is_feature_present(response, 'phoenix_claim')
        assert _is_feature_present(response, 'phoenix_corp')
    elif payment_scheme == 'decoupling':
        assert _is_feature_present(response, 'phoenix_corp')
        assert not _is_feature_present(response, 'phoenix_claim')
    else:
        assert not _is_feature_present(response, 'phoenix_claim')
        assert not _is_feature_present(response, 'phoenix_corp')


@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariff_settings(filename='tariff_settings_moscow_tel_aviv.json')
@pytest.mark.parametrize(
    'zone_id,expected_meta_code,point1_coords',
    [
        pytest.param('moscow', 200, [37.617617, 55.755811], id='moscow_ok'),
        pytest.param(
            'tel_aviv', 400, [34.855499, 32.109333], id='tel_aviv_forbidden',
        ),
    ],
)
async def test_create_c2c_receipt_availability(
        taxi_cargo_claims,
        create_default_cargo_c2c_order,
        mock_cargo_corp_up,
        mock_create_event,
        get_default_headers,
        zone_id,
        expected_meta_code,
        point1_coords,
):
    corp_client_id = '123'
    payment_type = 'cargocorp'
    payment_method_id = 'cargocorp:' + corp_client_id + ':card:456:789'

    mock_create_event(
        idempotency_token='accept_1',
        event={
            'kind': 'status-change-requested',
            'status': 'accepted',
            'data': {
                'claim_version': 1,
                'accept_language': 'ru',
                'corp_client_id': corp_client_id,
                'accept_as_create_event': True,
                'claim_revision': 1,
                'is_terminal': False,
                'phoenix_claim': True,
                'claim_origin': 'yandexgo',
                'skip_client_notify': False,
                'claim_accepted': True,
                'offer_id': 'cargo-pricing/v1/123',
                'notify_pricing_claim_accepted': True,
            },
        },
    )

    await create_default_cargo_c2c_order(
        payment_type=payment_type,
        payment_method_id=payment_method_id,
        zone_id=zone_id,
        expected_meta_code=expected_meta_code,
        point1_coords=point1_coords,
    )


@pytest.mark.config(
    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={'__cargo_c2c__': ['combo_order']},
    CARGO_CLAIMS_FEATURES_VALIDATION_ENABLED=True,
)
@pytest.mark.parametrize(
    'feature,meta_code', [('combo_order', 200), ('some_feature', 400)],
)
async def test_create_c2c_with_combo_order_feature(
        taxi_cargo_claims,
        create_default_cargo_c2c_order,
        mock_create_event,
        get_default_headers,
        feature,
        meta_code,
):
    mock_create_event()

    claim = await create_default_cargo_c2c_order(
        expected_meta_code=meta_code, features=[{'id': feature}],
    )

    if meta_code == 200:
        response = await taxi_cargo_claims.get(
            '/v2/claims/full',
            headers=get_default_headers(),
            params={'claim_id': claim.claim_id},
        )
        assert response.status_code == 200
        assert _is_feature_present(response.json(), feature)
