import dateutil
import pytest


def make_request_from_core_data(core_data):
    request_params = {
        'partner_id': 1,
        'promo_id': core_data['id'],
        'promo_status': core_data['status'],
    }
    request_body = core_data.copy()
    for req in core_data['requirements']:
        request_body.update(req)
    for bon in core_data['bonuses']:
        request_body.update(bon)
    return request_params, request_body


def check_pg(
        pgsql,
        promo_id,
        promo_type,
        promo_status,
        starts_at,
        ends_at,
        requirements,
        bonuses,
        schedule,
        task_id,
):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT '
        'promo_id,'
        'place_ids,'
        'promo_type,'
        'status,'
        'starts,'
        'ends,'
        'requirements,'
        'bonuses,'
        'schedule,'
        'discount_task_id,'
        'discount_ids '
        'FROM eats_restapp_promo.promos '
        'WHERE promo_id = %s ;',
        (promo_id,),
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == promo_id
    assert pg_result[1] == ['1', '2']
    assert pg_result[2] == promo_type
    assert pg_result[3] == promo_status
    assert pg_result[4] == dateutil.parser.parse(starts_at)
    assert pg_result[5] == dateutil.parser.parse(ends_at)
    assert pg_result[6] == {'requirements': requirements}
    assert pg_result[7] == {'bonuses': bonuses}
    if schedule:
        assert pg_result[8] == {'schedule': schedule}
    else:
        assert pg_result[8] is None
    assert pg_result[9] == task_id
    assert pg_result[10] is None


@pytest.mark.now('2021-09-01T00:00:00+00')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    [
        'promo_type',
        'promo_id',
        'existing',
        'schedule',
        'requirements',
        'bonuses',
        'pg_bonuses',
    ],
    [
        pytest.param(
            'one_plus_one',
            123,
            False,
            [
                {'day': 1, 'from': 15, 'to': 600},
                {'day': 2, 'from': 0, 'to': 1200},
            ],
            [{'item_ids': ['3', '4', '5']}],
            [],
            [],
            id='one_plus_one non-existing',
        ),
        pytest.param(
            'one_plus_one',
            301,
            True,
            [
                {'day': 1, 'from': 15, 'to': 600},
                {'day': 2, 'from': 0, 'to': 1200},
            ],
            [{'item_ids': ['3', '4', '5']}],
            [],
            [],
            id='one_plus_one existing',
        ),
        pytest.param(
            'gift',
            123,
            False,
            [
                {'day': 1, 'from': 15, 'to': 600},
                {'day': 2, 'from': 0, 'to': 1200},
            ],
            [{'min_order_price': 123.0}],
            [{'item_id': '1'}],
            [{'item_id': '1'}],
            id='gift non-existing',
        ),
        pytest.param(
            'gift',
            302,
            True,
            [
                {'day': 1, 'from': 15, 'to': 600},
                {'day': 2, 'from': 0, 'to': 1200},
            ],
            [{'min_order_price': 123.0}],
            [{'item_id': '1'}],
            [{'item_id': '1'}],
            id='gift existing',
        ),
        pytest.param(
            'discount',
            123,
            False,
            [
                {'day': 1, 'from': 15, 'to': 600},
                {'day': 2, 'from': 0, 'to': 1200},
            ],
            [{'item_ids': ['3', '4', '5']}],
            [{'discount': 20}],
            [{'discount': 20, 'type': 'fraction'}],
            id='discount non-existing',
        ),
        pytest.param(
            'discount',
            303,
            True,
            [
                {'day': 1, 'from': 15, 'to': 600},
                {'day': 2, 'from': 0, 'to': 1200},
            ],
            [{'item_ids': ['3', '4', '5']}],
            [{'discount': 20}],
            [{'discount': 20, 'type': 'fraction'}],
            id='discount existing',
        ),
    ],
)
@pytest.mark.parametrize(
    ['promo_status', 'created_promo_status', 'discounts_calls', 'task_id'],
    [
        pytest.param(
            'new', 'new', 1, '12345678-1234-1234-1234-123412345678', id='new',
        ),
        pytest.param(
            'approved',
            'new',
            1,
            '12345678-1234-1234-1234-123412345678',
            id='approved',
        ),
        pytest.param(
            'enabled',
            'new',
            1,
            '12345678-1234-1234-1234-123412345678',
            id='enabled',
        ),
        pytest.param('disabled', 'completed', 0, '', id='disabled'),
        pytest.param('completed', 'completed', 0, '', id='completed'),
    ],
)
@pytest.mark.parametrize(
    ['starts_at', 'ends_at', 'discounts_starts_at', 'discounts_ends_at'],
    [
        pytest.param(
            '2021-10-01T00:00:00+00:00',
            '2021-10-11T00:00:00+00:00',
            '2021-10-01T00:00:00+00:00',
            '2021-10-11T00:00:00+00:00',
            id='in future',
        ),
        pytest.param(
            '2021-08-01T00:00:00+00:00',
            '2021-10-11T00:00:00+00:00',
            '2021-09-01T00:11:00+00:00',
            '2021-10-11T00:00:00+00:00',
            id='in past',
        ),
    ],
)
async def test_promos_internal_create_from_core(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_eats_restapp_core,
        pgsql,
        load_json,
        promo_type,
        promo_id,
        existing,
        schedule,
        requirements,
        bonuses,
        pg_bonuses,
        promo_status,
        created_promo_status,
        discounts_calls,
        task_id,
        starts_at,
        ends_at,
        discounts_starts_at,
        discounts_ends_at,
):
    expected_discount_request = load_json(
        'discount_request/' + promo_type + '.json',
    )
    for discount in expected_discount_request['discounts_data']:
        for rule in discount['rules']:
            if rule['condition_name'] == 'active_period':
                rule['values'] = [
                    {
                        'start': discounts_starts_at,
                        'end': discounts_ends_at,
                        'is_start_utc': True,
                        'is_end_utc': True,
                    },
                ]

    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        assert request.json == expected_discount_request
        response_body = {'task_id': task_id}
        return mockserver.make_response(status=200, json=response_body)

    core_data = {
        'id': promo_id,
        'status': promo_status,
        'name': 'promo_name',
        'description': 'description',
        'place_ids': [1, 2],
        'type': promo_type,
        'starts_at': starts_at,
        'ends_at': ends_at,
        'schedule': schedule,
        'requirements': requirements,
        'bonuses': bonuses,
    }

    request_params, request_body = make_request_from_core_data(core_data)
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promo',
        params=request_params,
        json=request_body,
    )
    assert response.status_code == 204

    assert _mock_eats_discounts.times_called == (
        discounts_calls if not existing else 0
    )

    check_pg(
        pgsql,
        promo_id,
        promo_type,
        created_promo_status if not existing else 'approved',
        starts_at if not existing else '2022-01-01T00:00:00+00',
        ends_at if not existing else '2022-02-01T00:00:00+00',
        requirements if not existing else [],
        pg_bonuses if not existing else [],
        schedule if not existing else None,
        task_id if not existing else '',
    )


@pytest.mark.now('2021-09-01T00:00:00+00')
@pytest.mark.experiments3(filename='promos_settings.json')
async def test_promos_internal_create_response_500_with_error(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_eats_restapp_core,
):
    core_data = {
        'id': 100,
        'status': 'new',
        'name': 'promo_name',
        'description': 'description',
        'place_ids': [1, 2],
        'type': 'gift',
        'starts_at': '2021-09-02T00:00:00+00',
        'ends_at': '2021-09-03T00:00:00+00',
        'schedule': [],
        'requirements': [{'min_order_price': 123.0}],
        'bonuses': [{'item_id': '1a'}],
    }

    request_params, request_body = make_request_from_core_data(core_data)
    response = await taxi_eats_restapp_promo.post(
        '/internal/eats-restapp-promo/v1/promo',
        params=request_params,
        json=request_body,
    )
    assert response.status_code == 500
    assert response.json() == {'code': '500', 'message': 'No available items'}
