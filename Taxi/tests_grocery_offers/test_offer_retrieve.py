import datetime

import dateutil.parser as datetime_parser
import pytest
import pytz

from tests_grocery_offers import tests_headers


@pytest.mark.parametrize('good_offer_id', [True, False])
async def test_retrieve_by_id(taxi_grocery_offers, now, good_offer_id):
    tag = 'lavka:0x33ed'
    now = now.replace(tzinfo=pytz.UTC)
    create_params = {'point': [35, 57]}
    create_payload = {'surge': 3.5}
    due = now + datetime.timedelta(minutes=5)
    due = due.replace(microsecond=0)  # prevent time resolution issues
    create_response = await taxi_grocery_offers.post(
        '/v1/create',
        headers=tests_headers.HEADERS,
        json={
            'tag': tag,
            'due': due.isoformat(),
            'params': create_params,
            'payload': create_payload,
        },
    )
    assert create_response.status_code == 200

    if good_offer_id:
        offer_id = create_response.json()['id']
    else:
        offer_id = create_response.json()['id'] + '111'

    retrieve_response = await taxi_grocery_offers.post(
        '/v1/retrieve/by-id',
        headers={**{'Date': now.isoformat()}, **tests_headers.HEADERS},
        json={'tag': tag, 'id': offer_id},
    )
    if good_offer_id:
        assert retrieve_response.status_code == 200
        retrieve_response = retrieve_response.json()
        assert retrieve_response['id'] == offer_id
        assert retrieve_response['tag'] == tag
        assert datetime_parser.parse(retrieve_response['due']) == due
        assert retrieve_response['params'] == create_params
        assert retrieve_response['payload'] == create_payload
    else:
        assert retrieve_response.status_code == 404
