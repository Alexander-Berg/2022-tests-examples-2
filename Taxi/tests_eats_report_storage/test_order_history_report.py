import pytest

PARTNER_ID = 222
REPORT_ID = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'


def get_order_history_reports_data(pgsql):
    cursor = pgsql['eats_report_storage'].cursor()
    cursor.execute(
        'SELECT report_id, partner_id, yql_operation_id,'
        + ' filters FROM eats_report_storage.order_history_reports',
    )
    data = cursor.fetchall()
    return [
        {
            'report_id': report[0],
            'partner_id': report[1],
            'yql_operation_id': report[2],
            'filters': report[3],
        }
        for report in data
    ]


@pytest.mark.pgsql(
    'eats_report_storage',
    files=('eats_report_storage_order_history_report_data.sql',),
)
@pytest.mark.parametrize(
    'request_body, has_from_field, has_to_field, has_statuses_field,'
    + ' has_delivery_types_field',
    [
        pytest.param(
            {
                'report_id': REPORT_ID,
                'partner_id': PARTNER_ID,
                'filters': {
                    'places': [77, 88],
                    'from': '2019-01-01T20:03:59+03:00',
                    'to': '2019-05-01T20:03:59+03:00',
                    'statuses': ['accepted'],
                    'delivery_types': ['native', 'pickup'],
                },
            },
            True,
            True,
            True,
            True,
            id='all fields are present',
        ),
        pytest.param(
            {
                'report_id': REPORT_ID,
                'partner_id': PARTNER_ID,
                'filters': {
                    'places': [77, 88],
                    'statuses': ['accepted'],
                    'delivery_types': ['native', 'pickup'],
                },
            },
            False,
            False,
            True,
            True,
            id='from and to fields are missing',
        ),
        pytest.param(
            {
                'report_id': REPORT_ID,
                'partner_id': PARTNER_ID,
                'filters': {
                    'places': [77, 88],
                    'from': '2019-01-01T20:03:59+03:00',
                    'to': '2019-05-01T20:03:59+03:00',
                },
            },
            True,
            True,
            False,
            False,
            id='statuses and delivery_types are missing',
        ),
        pytest.param(
            {
                'report_id': REPORT_ID,
                'partner_id': PARTNER_ID,
                'filters': {'places': [77, 88]},
            },
            False,
            False,
            False,
            False,
            id='all non-required fields are missing',
        ),
    ],
)
async def test_order_history_report_create(
        taxi_eats_report_storage,
        pgsql,
        stq,
        request_body,
        has_from_field,
        has_to_field,
        has_statuses_field,
        has_delivery_types_field,
):
    status_before_data = get_order_history_reports_data(pgsql)
    assert len(status_before_data) == 1
    assert status_before_data[0]['partner_id'] == 111

    response = await taxi_eats_report_storage.post(
        '/internal/reports/v1/order_history', json=request_body,
    )

    assert response.status_code == 204
    status_after_data = get_order_history_reports_data(pgsql)

    assert len(status_after_data) == 2
    assert status_after_data[1]['report_id'] == REPORT_ID
    assert status_after_data[1]['partner_id'] == PARTNER_ID
    assert not status_after_data[1]['yql_operation_id']
    assert ('from' in status_after_data[1]['filters']) == has_from_field
    assert ('to' in status_after_data[1]['filters']) == has_to_field
    assert (
        'statuses' in status_after_data[1]['filters']
    ) == has_statuses_field
    if has_statuses_field:
        assert len(status_after_data[1]['filters']['statuses']) == 1
    assert (
        'delivery_types' in status_after_data[1]['filters']
    ) == has_delivery_types_field
    if has_delivery_types_field:
        assert len(status_after_data[1]['filters']['delivery_types']) == 2

    assert (
        stq.eats_report_storage_order_history_report_generation.times_called
        == 1
    )


@pytest.mark.parametrize(
    'request_body',
    [
        pytest.param(
            {
                'partner_id': PARTNER_ID,
                'filters': {
                    'places': [77, 88],
                    'from': '2019-01-01T20:03:59+03:00',
                    'to': '2019-05-01T20:03:59+03:00',
                    'statuses': ['accepted'],
                    'delivery_types': ['native', 'pickup'],
                },
            },
            id='report_id is missing',
        ),
        pytest.param(
            {
                'report_id': REPORT_ID,
                'filters': {
                    'places': [77, 88],
                    'from': '2019-01-01T20:03:59+03:00',
                    'to': '2019-05-01T20:03:59+03:00',
                    'statuses': ['accepted'],
                    'delivery_types': ['native', 'pickup'],
                },
            },
            id='partner_id field is missing',
        ),
        pytest.param(
            {'report_id': REPORT_ID, 'partner_id': PARTNER_ID},
            id='filters field is missing',
        ),
        pytest.param(
            {
                'report_id': REPORT_ID,
                'partner_id': PARTNER_ID,
                'filters': {
                    'from': '2019-01-01T20:03:59+03:00',
                    'to': '2019-05-01T20:03:59+03:00',
                    'statuses': ['accepted'],
                    'delivery_types': ['native', 'pickup'],
                },
            },
            id='places field is missing',
        ),
        pytest.param(
            {
                'report_id': REPORT_ID,
                'partner_id': PARTNER_ID,
                'filters': {
                    'places': [],
                    'from': '2019-01-01T20:03:59+03:00',
                    'to': '2019-05-01T20:03:59+03:00',
                    'statuses': ['accepted'],
                    'delivery_types': ['native', 'pickup'],
                },
            },
            id='places array is empty',
        ),
        pytest.param(
            {
                'report_id': REPORT_ID,
                'partner_id': PARTNER_ID,
                'filters': {
                    'places': [],
                    'from': '2019-01-01T20:03:59+03:00',
                    'to': '2019-05-01T20:03:59+03:00',
                    'statuses': ['accepted'],
                    'delivery_types': ['native', 'pickup'],
                    'error': 'error',
                },
            },
            id='nonvalid filter type',
        ),
    ],
)
async def test_order_history_report_invalid_request(
        taxi_eats_report_storage, request_body, stq,
):
    response = await taxi_eats_report_storage.post(
        '/internal/reports/v1/order_history', json=request_body,
    )

    assert response.status_code == 400
    assert (
        stq.eats_report_storage_order_history_report_generation.times_called
        == 0
    )


@pytest.mark.pgsql(
    'eats_report_storage',
    files=('eats_report_storage_order_history_report_data.sql',),
)
async def test_order_history_report_create_on_existing_report_id(
        taxi_eats_report_storage, pgsql, stq,
):

    status_before_data = get_order_history_reports_data(pgsql)
    assert len(status_before_data) == 1
    assert (
        status_before_data[0]['report_id']
        == 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    )

    response = await taxi_eats_report_storage.post(
        '/internal/reports/v1/order_history',
        json={
            'report_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            'partner_id': 111,
            'filters': {
                'places': [77, 88],
                'from': '2019-01-01T20:03:59+03:00',
                'to': '2019-05-01T20:03:59+03:00',
                'statuses': ['accepted'],
                'delivery_types': ['native', 'pickup'],
            },
        },
    )

    assert response.status_code == 204
    status_after_data = get_order_history_reports_data(pgsql)
    assert status_before_data == status_after_data
    assert (
        stq.eats_report_storage_order_history_report_generation.times_called
        == 1
    )
