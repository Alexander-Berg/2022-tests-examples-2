import uuid

import pytest


from .. import utils_v2


async def test_post_payment_basic(
        create_segment_with_payment,
        get_default_corp_client_id,
        mock_payment_create,
        exp_cargo_payment_virtual_clients,
        payment_method='card',
):
    claim_info = await create_segment_with_payment(
        payment_method=payment_method,
    )

    mock_payment_create.requests.sort(
        key=lambda x: x['details']['external_id'],
    )
    assert mock_payment_create.requests == [
        {
            'details': {
                'client_id': {
                    'type': 'corp_client_id',
                    'id': get_default_corp_client_id,
                },
                'external_id': f'{claim_info.claim_id}/2',
                'virtual_client_id': 'yandex_virtual_client',
                'customer': {
                    'email_pd_id': 'customer@yandex.ru_id',
                    'phone_pd_id': '+79999999991_id',
                },
                'geo_data': {'zone_id': 'moscow'},
            },
            'items': [
                {
                    'article': 'article of item title 1',
                    'count': 2,
                    'nds': 'nds_10',
                    'price': '10.4',
                    'title': 'item title 1',
                    'supplier_inn': '0123456788',
                    'currency': 'RUB',
                },
            ],
        },
        {
            'details': {
                'client_id': {
                    'type': 'corp_client_id',
                    'id': get_default_corp_client_id,
                },
                'external_id': f'{claim_info.claim_id}/3',
                'virtual_client_id': 'yandex_virtual_client',
                'customer': {
                    'email_pd_id': 'customer@yandex.ru_id',
                    'phone_pd_id': '+79999999991_id',
                },
                'geo_data': {'zone_id': 'moscow'},
            },
            'items': [
                {
                    'article': 'article of item title 2',
                    'count': 2,
                    'nds': 'nds_10',
                    'price': '53',
                    'title': 'item title 2',
                    'supplier_inn': '0123456788',
                    'currency': 'RUB',
                },
            ],
        },
    ]


async def test_post_payment_skip_confirmation(
        create_segment_with_payment,
        mock_payment_create,
        exp_cargo_payment_virtual_clients,
):
    """
        Check skip_confirmation is not validated for post-payment.
    """
    await create_segment_with_payment(skip_confirmation=True)


async def test_post_payment_mark(
        create_segment_with_payment,
        mock_payment_create,
        exp_cargo_payment_virtual_clients,
):
    """
        Check fiscalization mark passed to cargo-payments
    """

    items = [
        {
            'title': 'item_title 1',
            'extra_id': '1',
            'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
            'cost_value': '10.40',
            'cost_currency': 'RUB',
            'weight': 10.2,
            'pickup_point': 1,
            'droppof_point': 2,
            'quantity': 1,
        },
        {
            'title': 'item_title 2',
            'extra_id': '2',
            'size': {'length': 10.0, 'width': 5.8, 'height': 0.5},
            'cost_value': '53.00',
            'cost_currency': 'RUB',
            'weight': 3.7,
            'pickup_point': 1,
            'droppof_point': 3,
            'quantity': 1,
        },
    ]

    item_mark = {
        'kind': 'gs1_data_matrix_base64',
        'code': '444D00000000003741',
    }

    await create_segment_with_payment(
        payment_method='card', post_payment_mark=item_mark, custom_items=items,
    )

    mock_payment_create.requests.sort(
        key=lambda x: x['details']['external_id'],
    )

    assert mock_payment_create.requests[0]['items'][0]['mark'] == item_mark


async def test_post_payment_nonunique_article(
        taxi_cargo_claims,
        claim_creator_v2,
        build_create_request,
        enable_payment_on_delivery,
        payment_method='card',
):
    """
        Check claim create when there are items with the same articles.

        - According to Federal Law 54 same item can appear on different
        positions of the receipt
        - Different suppliers can have identical articles
    """
    request, _ = build_create_request(payment_method=payment_method)
    # duplicate items to emulate same article (single item in default context)
    request['items'] += request['items']

    response = await claim_creator_v2(request)

    assert response.status_code == 200


async def test_post_payment_multipoint(
        taxi_cargo_claims,
        claim_creator_v2,
        mock_payment_validate,
        build_create_request,
        enable_payment_on_delivery,
        payment_method='card',
):
    """
        Check that validation works correctly in multipoint order with
        non-payment-on-delivery points.
    """
    request, _ = build_create_request(payment_method=payment_method)

    for point in request['route_points']:
        if point['point_id'] == 3:
            del point['payment_on_delivery']
            break

    for item in request['items']:
        if item['droppof_point'] == 3:
            del item['fiscalization']
            break
    response = await claim_creator_v2(request)

    assert response.status_code == 200

    assert mock_payment_validate.handler.times_called > 0
    assert mock_payment_validate.handler.times_called == len(
        list(
            filter(
                lambda x: 'payment_on_delivery' in x, request['route_points'],
            ),
        ),
    )


async def test_post_payment_external_flow(
        create_segment_with_payment,
        mock_payment_create,
        exp_cargo_payment_virtual_clients,
):
    """
        Check cargo-payments wasn't notified for external_payment flow.
    """
    await create_segment_with_payment(
        payment_method='card', external_postpayment_flow=True,
    )

    assert mock_payment_create.handler.times_called == 0


async def test_post_payment_same_external_id(
        taxi_cargo_claims,
        create_segment_with_payment,
        mock_payment_create,
        exp_cargo_payment_virtual_clients,
        build_create_request,
):
    """
        Check error is processed on same external_payment_id.
    """
    external_payment_id = str(uuid.uuid4())
    await create_segment_with_payment(
        payment_method='card',
        external_payment_id=external_payment_id,
        multipoints=False,
        with_return=False,
    )

    assert mock_payment_create.handler.times_called == 0

    request, _ = build_create_request(
        payment_method='card',
        external_payment_id=external_payment_id,
        multipoints=False,
        with_return=False,
    )
    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )
    assert response.status_code == 200


async def test_nds_none(
        create_segment_with_payment,
        get_default_corp_client_id,
        mock_payment_create,
        exp_cargo_payment_virtual_clients,
        payment_method='card',
):
    """
        Check nds_none is handled correctly.
    """
    await create_segment_with_payment(
        payment_method=payment_method, post_payment_nds='vat_none',
    )

    cargo_payments_nds_set = set()
    for request in mock_payment_create.requests:
        for item in request['items']:
            cargo_payments_nds_set.add(item['nds'])
    assert cargo_payments_nds_set == {'nds_none'}


async def test_service_item(
        create_segment_with_payment,
        get_default_corp_client_id,
        mock_payment_create,
        exp_cargo_payment_virtual_clients,
        payment_method='card',
):
    """
        Check custom item_type is handled correctly.
    """
    await create_segment_with_payment(
        payment_method=payment_method, post_payment_item_type='service',
    )

    cargo_payments_types_set = set()
    for request in mock_payment_create.requests:
        for item in request['items']:
            cargo_payments_types_set.add(item['type'])
    assert cargo_payments_types_set == {'service'}


@pytest.mark.parametrize(
    'item_title',
    [
        'Royal Canin Sterilised 7+ для стерилизованных кошек и'
        'кастрированных котов старше 7 лет/Курица, 1,5 кг.',
        '𨭎' * 100,
    ],
)
async def test_item_title_unicode(
        build_create_request, claim_creator_v2, item_title,
):
    """
        Check correct verification of items with non-ASCII titles
    """
    request, _ = build_create_request(
        item_title_prefix=item_title, payment_method='card',
    )
    response = await claim_creator_v2(request)
    assert response.status_code == 200


async def test_long_title_item(build_create_request, claim_creator_v2):
    """
        Check maximum title size is 128 symbols.
    """
    item_title = 'f' * 129
    request, _ = build_create_request(
        item_title_prefix=item_title, payment_method='card',
    )
    response = await claim_creator_v2(request)
    assert response.status_code == 400
    assert response.json()['message'].startswith(
        'item.title max length is 128 characters, bad title:',
    )


async def test_post_payment_disabled_for_client(
        taxi_cargo_claims,
        disable_payment_on_delivery,
        build_create_request,
        mock_payment_create,
):
    """
        Check payment disabled for corp.
    """
    request, _ = build_create_request(payment_method='card')
    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=request, expect_failure=True,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('enabled', [True, False])
async def test_post_payment_disabled_by_exp(
        taxi_cargo_claims,
        exp_cargo_claims_post_payment_clients,
        build_create_request,
        mock_payment_create,
        enabled: bool,
):
    """
        Check payment disabled by exp cargo_claims_post_payment_clients
    """
    await exp_cargo_claims_post_payment_clients(enabled=enabled)

    request, _ = build_create_request(payment_method='card')
    if enabled:
        response, _ = await utils_v2.create_claim_v2(
            taxi_cargo_claims, request=request, expect_failure=False,
        )
        assert response.status_code == 200
    else:
        response = await utils_v2.create_claim_v2(
            taxi_cargo_claims, request=request, expect_failure=True,
        )
        assert response.status_code == 403
