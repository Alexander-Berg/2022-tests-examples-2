import pytest

from test_rida import helpers


@pytest.mark.mongodb_collections('rida_offers')
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_pg_offer.sql'])
@pytest.mark.filldb()
@pytest.mark.parametrize(
    ['offer_guid', 'expected_is_canceled', 'expected_status'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F', True, 200, id='happy_path',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5M',
            False,
            404,
            id='not_cancelable_status',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFAAAAA',
            False,
            404,
            id='offer_not_found',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAXXX',
            False,
            200,
            id='already_canceled',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
            False,
            200,
            id='offer_in_pg',
        ),
    ],
)
@pytest.mark.parametrize('request_body_as_query', [True, False])
async def test_offer_passenger_cancel(
        web_app,
        web_app_client,
        mongodb,
        get_stats_by_label_values,
        offer_guid: str,
        expected_is_canceled: bool,
        expected_status: int,
        request_body_as_query: bool,
):
    pending_bids_cursor = mongodb.rida_bids.find(
        {'$and': [{'offer_guid': offer_guid}, {'bid_status': 'PENDING'}]},
    )
    pending_bid_guids = [doc['bid_guid'] for doc in pending_bids_cursor]

    request_params = {'headers': helpers.get_auth_headers(user_id=1234)}
    request_body = {'offer_guid': offer_guid, 'offer_cancel_reason_id': 1}
    if request_body_as_query:
        request_params['data'] = request_body
    else:
        request_params['json'] = request_body
    response = await web_app_client.post(
        '/v1/offer/passengerCancel', **request_params,
    )
    assert response.status == expected_status
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'offers.status_change'},
    )
    if expected_is_canceled:
        # check that all pending bids were set to PASSENGER_CANCELED status
        assert len(pending_bid_guids) == 1
        bids_cursor = mongodb.rida_bids.find(
            {'bid_guid': {'$in': pending_bid_guids}},
        )
        bids = [doc for doc in bids_cursor]
        assert len(bids) == 1
        assert bids[0]['bid_status'] == 'PASSENGER_CANCELED'
        # check that metrics were sent
        assert stats == [
            {
                'kind': 'IGAUGE',
                'labels': {
                    'sensor': 'offers.status_change',
                    'status': 'PASSENGER_CANCELLED',
                },
                'value': 1,
                'timestamp': None,
            },
        ]
    else:
        assert stats == []
