import pytest

ENDPOINT_V1 = 'driver-feedback/v1/feedback'
ENDPOINT_V2 = 'driver-feedback/v2/feedback'


def _get_feedback_exist_params_(endpoint):
    def _get_id(data):
        return data.format('v1' if endpoint == ENDPOINT_V1 else 'v2')

    return [
        pytest.param(
            {'park_id': 'park_id_0', 'order_id': 'order_id_0'},
            endpoint,
            0,
            200,
            {'score': 4, 'comment': 'Good', 'feed_type': 'passenger'},
            id=_get_id('{}. With comment.'),
        ),
        pytest.param(
            {
                'park_id': 'park_id_0',
                'order_id': 'order_id_1',
                'feed_type': 'sender',
            },
            endpoint,
            0,
            200,
            {'score': 3, 'choices': ['key3', 'key4'], 'feed_type': 'sender'},
            id=_get_id('{}. With choices.'),
        ),
        pytest.param(
            {
                'park_id': 'park_id_1',
                'order_id': 'order_id_0',
                'feed_type': 'passenger',
            },
            endpoint,
            1,
            200,
            {
                'score': 5,
                'choices': ['key5'],
                'comment': 'Best',
                'feed_type': 'passenger',
            },
            id=_get_id('{}. With comment and choices.'),
        ),
        pytest.param(
            {
                'park_id': 'park_id_1',
                'order_id': 'order_id_1',
                'feed_type': 'recipient',
            },
            endpoint,
            1,
            200,
            {
                'score': 1,
                'choices': ['key1', 'key2'],
                'feed_type': 'recipient',
            },
            id=_get_id('{}. Another one'),
        ),
        pytest.param(
            {
                'park_id': 'park_id_1',
                'order_id': 'order_id_0',
                'feed_type': '',
            },
            endpoint,
            1,
            200,
            {
                'score': 5,
                'choices': ['key5'],
                'comment': 'Best',
                'feed_type': 'passenger',
            },
            id=_get_id('{}. With empty feed_type'),
        ),
    ]


@pytest.mark.pgsql(
    'taximeter_feedbacks@0',
    files=[
        'pg_taximeter_feedbacks@0.sql',
        'pg_taximeter_feedbacks_forbidden@0.sql',
    ],
)
@pytest.mark.pgsql(
    'taximeter_feedbacks@1', files=['pg_taximeter_feedbacks@1.sql'],
)
@pytest.mark.parametrize(
    'params,endpoint,shard_number,expected_status,expected_response',
    _get_feedback_exist_params_(ENDPOINT_V1)
    + _get_feedback_exist_params_(ENDPOINT_V2),
)
async def test_feedback_exist(
        taxi_driver_feedback,
        fleet_parks_service,
        params,
        endpoint,
        shard_number,
        expected_status,
        expected_response,
):
    fleet_parks_service.set_feedbacks_data(shard_number, 'feedbacks_0')
    response = await taxi_driver_feedback.get(endpoint, params=params)
    assert response.status_code == expected_status
    data = response.json()
    if endpoint == ENDPOINT_V1:
        assert data['feedback'] == expected_response
    else:
        assert data['feedback'][0] == expected_response


@pytest.mark.pgsql(
    'taximeter_feedbacks@0',
    files=[
        'pg_taximeter_feedbacks@0.sql',
        'pg_taximeter_feedbacks_forbidden@0.sql',
    ],
)
async def test_feedback_forbidden(taxi_driver_feedback, fleet_parks_service):
    fleet_parks_service.set_feedbacks_data(0, 'feedbacks_0')
    response = await taxi_driver_feedback.get(
        ENDPOINT_V2, params={'park_id': 'park_id_8', 'order_id': 'order_id_8'},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Bad Request'}


@pytest.mark.parametrize(
    'endpoint,expected_response',
    [
        pytest.param(ENDPOINT_V1, {'editable': True}, id='v1'),
        pytest.param(ENDPOINT_V2, {'editable': True}, id='v2'),
    ],
)
async def test_non_scored_order(
        taxi_driver_feedback, endpoint, expected_response,
):
    params = {'park_id': 'park_id_1', 'order_id': 'order_id_1'}
    response = await taxi_driver_feedback.get(endpoint, params=params)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(DRIVER_FEEDBACK_SETTINGS={'time_to_make_feedback': 72})
@pytest.mark.parametrize(
    'endpoint,expected_response',
    [
        pytest.param(ENDPOINT_V1, {'editable': False}, id='v1'),
        pytest.param(ENDPOINT_V2, {'editable': False}, id='v2'),
    ],
)
async def test_old_non_scored_order(
        taxi_driver_feedback, endpoint, expected_response,
):
    params = {'park_id': 'park_id_1', 'order_id': 'order_id_1'}
    response = await taxi_driver_feedback.get(endpoint, params=params)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'endpoint,expected_response',
    [
        pytest.param(ENDPOINT_V1, {'editable': False}, id='v1'),
        pytest.param(ENDPOINT_V2, {'editable': False}, id='v2'),
    ],
)
async def test_uncomplete_order(
        taxi_driver_feedback, driver_orders, endpoint, expected_response,
):

    params = {'park_id': 'park_id_1', 'order_id': 'order_id_1'}
    driver_orders.set_order_params(params['order_id'], {'status': 'cancelled'})

    response = await taxi_driver_feedback.get(endpoint, params=params)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'endpoint,expected_response',
    [
        pytest.param(ENDPOINT_V1, {'editable': False}, id='v1'),
        pytest.param(ENDPOINT_V2, {'editable': False}, id='v2'),
    ],
)
async def test_unexist_order(
        taxi_driver_feedback, driver_orders, endpoint, expected_response,
):
    params = {'park_id': 'park_id_1', 'order_id': 'order_id_1'}
    driver_orders.response_template['orders'] = [{'id': params['order_id']}]

    response = await taxi_driver_feedback.get(endpoint, params=params)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'endpoint',
    [pytest.param(ENDPOINT_V1, id='v1'), pytest.param(ENDPOINT_V2, id='v2')],
)
async def test_table_injection(
        taxi_driver_feedback, fleet_parks_service, endpoint,
):
    fleet_parks_service.set_feedbacks_data(0, '; Injection DROP ALL DATA --')
    params = {'park_id': 'park_id1', 'order_id': 'no matter'}
    response = await taxi_driver_feedback.get(endpoint, params=params)
    assert response.status_code == 404


@pytest.mark.pgsql(
    'taximeter_feedbacks@0', files=['pg_taximeter_feedbacks_multiple@0.sql'],
)
async def test_multiple_feedbacks(taxi_driver_feedback, fleet_parks_service):
    fleet_parks_service.set_feedbacks_data(0, 'feedbacks_0')
    response = await taxi_driver_feedback.get(
        ENDPOINT_V2, params={'park_id': 'park_id_0', 'order_id': 'order_id_0'},
    )
    assert response.status_code == 200
    data = response.json()
    assert sorted(data['feedback'], key=lambda x: x['score']) == [
        {'feed_type': 'passenger', 'score': 3, 'comment': 'Ok'},
        {'feed_type': 'sender', 'score': 4, 'comment': 'Good'},
        {'feed_type': 'recipient', 'score': 5, 'comment': 'Best'},
    ]
