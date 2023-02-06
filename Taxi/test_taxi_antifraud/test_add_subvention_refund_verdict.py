import datetime
import json

import dateutil.parser
import pytest
import pytz


NOW = datetime.datetime(2019, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_params,expected_db_content',
    [
        (
            {
                'user_login': 'vasya',
                'type': 'discard',
                'comment': 'Too bad',
                'ticket': 'TRACKER-1231',
                'billing_id': '1',
            },
            [
                {
                    'user_login': 'vasya',
                    'type': 'discard',
                    'comment': 'Too bad',
                    'ticket': 'TRACKER-1231',
                    'billing_id': '1',
                    # Mongodb does not store timezone info
                    'created': NOW.replace(tzinfo=None),
                },
            ],
        ),
    ],
)
async def test_comment_db_side(
        db, web_app_client, request_params, expected_db_content,
):
    response = await web_app_client.post(
        '/v1/add_subvention_refund_verdict', data=json.dumps(request_params),
    )

    assert response.status == 200

    verdicts = (
        await db.antifraud_subventions_refund_verdicts_mdb.find().to_list(None)
    )

    assert [
        {
            'user_login': verdict['user_login'],
            'type': verdict['type'],
            'comment': verdict['comment'],
            'ticket': verdict['ticket'],
            'billing_id': verdict['billing_id'],
            'created': verdict['created'],
        }
        for verdict in verdicts
    ] == expected_db_content


@pytest.mark.parametrize(
    'write_request_params,read_request_params,expected_response_content',
    [
        (
            {
                'user_login': 'vasya',
                'type': 'discard',
                'comment': 'Too bad',
                'ticket': 'TRACKER-1231',
                'billing_id': '1',
            },
            {'limit': 100, 'order_id': 'f1d937ab7dd71c0c96bf1a84376f72be'},
            [
                {
                    'user_login': 'vasya',
                    'type': 'discard',
                    'comment': 'Too bad',
                    'ticket': 'TRACKER-1231',
                    'billing_id': '1',
                    'created': NOW,
                },
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_comment_api_side(
        db,
        web_app_client,
        write_request_params,
        read_request_params,
        expected_response_content,
):
    response = await web_app_client.post(
        '/v1/add_subvention_refund_verdict',
        data=json.dumps(write_request_params),
    )

    assert response.status == 200

    response = await web_app_client.get(
        '/v1/get_subventions', params=read_request_params,
    )

    assert response.status == 200

    response_as_dict = await response.json()

    assert len(response_as_dict) == 1

    verdicts = response_as_dict[0]['verdicts']

    assert [
        {
            'user_login': verdict['user_login'],
            'type': verdict['type'],
            'comment': verdict['comment'],
            'ticket': verdict['ticket'],
            'billing_id': verdict['billing_id'],
            'created': (
                dateutil.parser.isoparse(verdict['created']).astimezone(
                    pytz.utc,
                )
            ),
        }
        for verdict in verdicts
    ] == expected_response_content
