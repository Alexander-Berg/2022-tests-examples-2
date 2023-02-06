import datetime

import bson
import pytest


_MOCK_NOW = '2021-01-01T00:00:00.000000+00:00'
PENDING_REQUEST_ID = '000000000000000000000000'
FAILED_REQUEST_ID = '111111111111111111111111'
DONE_REQUEST_ID = '222222222222222222222222'
UNEXPECTED_REQUEST_ID = '333333333333333333333333'


@pytest.mark.now(_MOCK_NOW)
async def test_create_request(web_app_client, stq, mongo):
    response = await web_app_client.post(
        '/admin/v1/point/request-arrange',
        json={'name': 'aname', 'pins_yt_table_name': '/home/taxi/pins'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert 'request_id' in response_json
    request_id = response_json['request_id']
    assert response_json == {
        'created_dt': '2021-01-01T03:00:00+03:00',
        'name': 'aname',
        'request_id': request_id,
    }
    assert stq.surge_arrange_fixed_points

    # check stq call
    assert stq.surge_arrange_fixed_points.times_called == 1
    stq_call = stq.surge_arrange_fixed_points.next_call()
    assert stq_call['queue'] == 'surge_arrange_fixed_points'
    assert stq_call['id'] == request_id
    assert stq_call['args'] == []
    assert stq_call['kwargs'] == {
        'pins_yt_table_name': '/home/taxi/pins',
        'request_id': request_id,
        'settings_override': None,
    }

    # check saved doc in mongo
    request_doc = await mongo.surge_points_arrange_requests.find_one(
        {'_id': bson.ObjectId(request_id)},
    )
    assert request_doc == {
        '_id': bson.ObjectId(request_id),
        'created_dt': datetime.datetime(2021, 1, 1, 0, 0),
        'name': 'aname',
        'pins_yt_table_name': '/home/taxi/pins',
        'status': 'pending',
    }


async def test_enumerate_requests(web_app_client, stq, mongo):
    response = await web_app_client.get('/admin/v1/point/arrange-requests')
    assert response.status == 200
    assert await response.json() == {
        'requests': [
            {
                'id': PENDING_REQUEST_ID,
                'created_dt': '2010-01-10T03:00:00+03:00',
                'name': 'request1',
                'pins_yt_table_name': '//home/taxi/pins',
                'settings_override': {'key': 'value'},
                'status': 'pending',
            },
            {
                'id': FAILED_REQUEST_ID,
                'created_dt': '2010-01-10T03:00:00+03:00',
                'name': 'request2',
                'pins_yt_table_name': '//home/taxi/pins',
                'status': 'failed',
            },
            {
                'id': DONE_REQUEST_ID,
                'created_dt': '2010-01-10T03:00:00+03:00',
                'name': 'request2',
                'pins_yt_table_name': '//home/taxi/pins',
                'status': 'done',
            },
        ],
    }


async def test_get_results(web_app_client, stq, mongo):
    # get pending
    response = await web_app_client.get(
        '/admin/v1/point/arrange-result',
        params={'request_id': PENDING_REQUEST_ID},
    )
    assert response.status == 200
    assert await response.json() == {
        'info': {
            'id': PENDING_REQUEST_ID,
            'created_dt': '2010-01-10T03:00:00+03:00',
            'name': 'request1',
            'pins_yt_table_name': '//home/taxi/pins',
            'settings_override': {'key': 'value'},
            'status': 'pending',
        },
    }

    # get failed
    response = await web_app_client.get(
        '/admin/v1/point/arrange-result',
        params={'request_id': FAILED_REQUEST_ID},
    )
    assert response.status == 200
    assert await response.json() == {
        'info': {
            'id': FAILED_REQUEST_ID,
            'created_dt': '2010-01-10T03:00:00+03:00',
            'name': 'request2',
            'pins_yt_table_name': '//home/taxi/pins',
            'status': 'failed',
        },
        'result': {'error_message': 'Someshing went wrong'},
    }

    # get done
    response = await web_app_client.get(
        '/admin/v1/point/arrange-result',
        params={'request_id': DONE_REQUEST_ID},
    )
    assert response.status == 200
    assert await response.json() == {
        'info': {
            'id': DONE_REQUEST_ID,
            'created_dt': '2010-01-10T03:00:00+03:00',
            'name': 'request2',
            'pins_yt_table_name': '//home/taxi/pins',
            'status': 'done',
        },
        'result': {
            'create': [
                {
                    'location': [37.0, 56.0],
                    'mode': 'apply',
                    'name': '',
                    'surge_zone_name': 'MSK',
                },
            ],
        },
    }


@pytest.mark.parametrize(
    'request_id,status,add_fixed_points,add_error_message,expected_code',
    [
        pytest.param(
            PENDING_REQUEST_ID, 'done', True, False, 200, id='ok, save done',
        ),
        pytest.param(
            PENDING_REQUEST_ID,
            'failed',
            False,
            True,
            200,
            id='ok, save failed',
        ),
        pytest.param(
            UNEXPECTED_REQUEST_ID,
            'done',
            True,
            False,
            404,
            id='error: unexpected request_id',
        ),
        pytest.param(
            DONE_REQUEST_ID,
            'done',
            True,
            False,
            400,
            id='error: save result for non-pending request',
        ),
        pytest.param(
            PENDING_REQUEST_ID,
            'done',
            False,
            False,
            400,
            id='error: no fixed_points in done request',
        ),
        pytest.param(
            PENDING_REQUEST_ID,
            'failed',
            False,
            False,
            400,
            id='error: no error_message in done request',
        ),
    ],
)
async def test_save_results(
        web_app_client,
        mongo,
        request_id,
        status,
        add_fixed_points,
        add_error_message,
        expected_code,
):
    body = {'status': status}
    if add_fixed_points:
        if 'result' not in body:
            body['result'] = dict()
        body['result']['fixed_points'] = [
            {'location': [1.0, 2.0], 'mode': 'apply'},
        ]
    if add_error_message:
        if 'result' not in body:
            body['result'] = dict()
        body['result']['error_message'] = 'something is broken'
    response = await web_app_client.post(
        '/v1/points/save-arranged',
        params={'request_id': request_id},
        json=body,
    )
    assert response.status == expected_code

    if expected_code == 200:
        # check updated doc in mongo
        request_doc = await mongo.surge_points_arrange_requests.find_one(
            {'_id': bson.ObjectId(request_id)},
        )
        expected_doc = {
            '_id': bson.ObjectId(PENDING_REQUEST_ID),
            'created_dt': datetime.datetime(2010, 1, 10, 0, 0),
            'name': 'request1',
            'pins_yt_table_name': '//home/taxi/pins',
            'settings_override': {'key': 'value'},
            'status': status,
        }
        if add_fixed_points:
            expected_doc['fixed_points'] = [
                {
                    'location': [1.0, 2.0],
                    'mode': 'apply',
                    'name': '',
                    'surge_zone_name': '',
                },
            ]
        if add_error_message:
            expected_doc['error_message'] = 'something is broken'
        assert request_doc == expected_doc
