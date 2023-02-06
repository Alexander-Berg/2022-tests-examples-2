import pytest

from fleet_feedback.utils import pg_utils


async def test_support_disabled(web_app_client, headers_support, load_json):
    stub = load_json('common.json')

    response = await web_app_client.post(
        '/feedback-api/v1/polls/set-answer',
        headers=headers_support,
        json=stub['service']['success_request'],
    )

    assert response.status == 403


@pytest.mark.pgsql('fleet_feedback', files=('simple_poll.sql',))
@pytest.mark.now('2019-01-01T00:00:00+03:00')
async def test_poll_not_found(web_app_client, headers, load_json):
    stub = load_json('common.json')

    json = stub['service']['success_request']
    json['poll_id'] = 2

    response = await web_app_client.post(
        '/feedback-api/v1/polls/set-answer', headers=headers, json=json,
    )

    assert response.status == 404


@pytest.mark.pgsql('fleet_feedback', files=('simple_poll.sql',))
@pytest.mark.now('2019-01-01T00:00:00+03:00')
async def test_success(
        web_app_client, headers, mock_parks, mock_dac_users, pgsql, load_json,
):

    stub = load_json('common.json')

    response = await web_app_client.post(
        '/feedback-api/v1/polls/set-answer',
        headers=headers,
        json=stub['service']['success_request'],
    )

    assert response.status == 200

    cursor = pgsql['fleet_feedback'].cursor()

    cursor.execute('SELECT * from fleet_feedback.poll_answers')

    assert cursor.rowcount == 1

    row = pg_utils.fetch_one_dict(cursor)

    assert pg_utils.date_parsed(row) == {
        'id': 1,
        'park_id': '7ad36bc7560449998acbe2c57a75c293',
        'poll_id': 1,
        'poll_type': 'main',
        'passport_uid': '123',
        'user_group': 'Администратор',
        'user_is_superuser': True,
        'country_id': 'rus',
        'city_eng': 'Москва',
        'type_data': {
            'rating': 4,
            'comment': 'test comment',
            'additional_questions': [
                {'id': '1', 'rating': 4},
                {'id': '2', 'rating': 3},
                {'id': '3', 'rating': 5},
            ],
        },
        'yt_status': 0,
        'created_at': '2019-01-01T00:00:00+03:00',
        'updated_at': '2019-01-01T00:00:00+03:00',
    }
