import pytest

from fleet_feedback import enums

SIMPLE_POLL = {
    'showing': True,
    'poll_id': 1,
    'type': enums.PollType.Main.value,
    'type_settings': {
        'questions': [
            {'id': '1', 'text': 'q1'},
            {'id': '2', 'text': 'q2'},
            {'id': '3', 'text': 'q3'},
        ],
        'labels': {'title': 't', 'button': 'b', 'comment': 'c'},
    },
}

EMPTY_RESPONSE = {'showing': False}

TRANSLATIONS = {
    'fleet_polls.questions_1': {'ru': 'q1'},
    'fleet_polls.questions_2': {'ru': 'q2'},
    'fleet_polls.questions_3': {'ru': 'q3'},
    'fleet_polls.title': {'ru': 't'},
    'fleet_polls.button': {'ru': 'b'},
    'fleet_polls.comment': {'ru': 'c'},
}


async def test_support_disabled(web_app_client, headers_support):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers_support,
    )

    assert response.status == 403


async def test_no_polls(web_app_client, headers):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == EMPTY_RESPONSE


@pytest.mark.pgsql('fleet_feedback', files=('simple_poll.sql',))
@pytest.mark.now('2019-01-05 00:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_simple_poll(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == SIMPLE_POLL


@pytest.mark.pgsql('fleet_feedback', files=('last_poll_answer_delay.sql',))
@pytest.mark.config(OPTEUM_PSAT_DELAY={'value': 5})
@pytest.mark.now('2019-01-01 00:00:00+03:00')
async def test_last_poll_answer_delay_false(web_app_client, headers):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == EMPTY_RESPONSE


@pytest.mark.pgsql('fleet_feedback', files=('last_poll_answer_delay.sql',))
@pytest.mark.config(OPTEUM_PSAT_DELAY={'value': 5})
@pytest.mark.now('2019-01-01 06:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_last_poll_answer_delay_true(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    simple_poll = dict(SIMPLE_POLL)
    simple_poll['poll_id'] = 2

    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == simple_poll


@pytest.mark.pgsql('fleet_feedback', files=('poll_filters.sql',))
@pytest.mark.now('2019-01-01 00:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_filter_country(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    mock_parks['parks'][0]['country_id'] = 'test_country'

    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == SIMPLE_POLL


@pytest.mark.pgsql('fleet_feedback', files=('poll_filters.sql',))
@pytest.mark.now('2019-01-01 00:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_filter_city(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    mock_parks['parks'][0]['city_id'] = 'test_city'
    simple_poll = dict(SIMPLE_POLL)
    simple_poll['poll_id'] = 2

    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == simple_poll


@pytest.mark.pgsql('fleet_feedback', files=('poll_filters.sql',))
@pytest.mark.now('2019-01-01 00:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_filter_park_id(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    simple_poll = dict(SIMPLE_POLL)
    simple_poll['poll_id'] = 3

    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == simple_poll


@pytest.mark.pgsql('fleet_feedback', files=('distribution_poll.sql',))
@pytest.mark.now('2019-01-10 23:59:00+03:00')
async def test_distribution_duration_false(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == EMPTY_RESPONSE


@pytest.mark.pgsql('fleet_feedback', files=('distribution_poll.sql',))
@pytest.mark.now('2019-01-11 00:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_distribution_duration_true(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == SIMPLE_POLL


@pytest.mark.pgsql('fleet_feedback', files=('periodicity_poll.sql',))
@pytest.mark.now('2019-01-01 01:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_periodicity(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == SIMPLE_POLL


@pytest.mark.pgsql(
    'fleet_feedback', files=('periodicity_poll_with_answer.sql',),
)
@pytest.mark.now('2019-01-01 02:00:00+03:00')
async def test_periodicity_with_answer_false(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == EMPTY_RESPONSE


@pytest.mark.pgsql(
    'fleet_feedback', files=('periodicity_poll_with_answer.sql',),
)
@pytest.mark.now('2019-01-03 01:00:00+03:00')
@pytest.mark.translations(opteum_component_PSAT=TRANSLATIONS)
async def test_periodicity_with_answer_true(
        web_app_client, headers, mock_parks, mock_dac_users, load_json,
):
    response = await web_app_client.post(
        '/feedback-api/v1/polls/available', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == SIMPLE_POLL
