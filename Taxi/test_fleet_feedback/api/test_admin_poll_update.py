import pytest

from fleet_feedback.utils import pg_utils


@pytest.mark.now('2020-01-01T00:00:00+03:00')
@pytest.mark.pgsql('fleet_feedback', files=('simple_poll.sql',))
async def test_success(web_app_client, headers, load_json, pgsql):
    stub = load_json('common.json')

    response = await web_app_client.put(
        '/admin/v1/polls/update',
        headers=headers,
        json=stub['service']['success_request'],
    )

    assert response.status == 200

    cursor = pgsql['fleet_feedback'].cursor()
    cursor.execute('SELECT * from fleet_feedback.polls')
    assert cursor.rowcount == 1

    row = pg_utils.fetch_one_dict(cursor)
    assert pg_utils.date_parsed(row) == stub['service']['poll_in_db']


@pytest.mark.now('2020-01-01T00:00:00+03:00')
@pytest.mark.pgsql('fleet_feedback', files=('simple_poll.sql',))
async def test_poll_not_found(web_app_client, headers, load_json):
    stub = load_json('common.json')

    not_found_request = stub['service']['success_request']
    not_found_request['id'] = 2

    response = await web_app_client.put(
        '/admin/v1/polls/update', headers=headers, json=not_found_request,
    )

    assert response.status == 404
