# pylint: disable=unused-variable
import copy

import pytest

BASIC_MATCH_FILTER_BODY = {
    'description': 'Description from test',
    'query': {'rules': [{'matchstring': 'some error message'}]},
}

BAD_FILTER = {
    'description': 'Description from bad filter',
    'query': {
        'rules': [{'field': 'bad_test:', 'matchstring': 'some error message'}],
    },
}

MULTIFILTER = {
    'description': 'Фильтр с правилами',
    'key': 'TAXIPLATFORM-10',
    'cgroup': 'taxi_logserrors',
    'query': {
        'rules': [
            {'field': 'stopwatch_name', 'matchstring': 'pg_query'},
            {
                'matchstring': (
                    'Error message:  schema '
                    '"logs_errors_filters  " already exists'
                ),
            },
        ],
    },
}

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token', 'X-Yandex-Login': 'testlogin'}


@pytest.mark.pgsql('logs_errors_filters', files=['test_create_filter.sql'])
@pytest.mark.parametrize('filter_info', [BASIC_MATCH_FILTER_BODY, MULTIFILTER])
async def test_create_filter(web_app_client, filter_info, auth, patch):
    await auth()

    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    response = await web_app_client.post(
        f'/v1/filter/', json=filter_info, headers=HEADERS,
    )

    assert response.status == 200

    content = await response.json()

    assert content['id'] == 1


@pytest.mark.pgsql('logs_errors_filters', files=['test_create_filter.sql'])
async def test_create_filter_with_cgroup(web_app_client, auth, patch):

    _filter = copy.deepcopy(BASIC_MATCH_FILTER_BODY)
    _filter['cgroup'] = 'taxi_api_fake'

    await auth()

    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    response = await web_app_client.post(
        f'/v1/filter/', json=_filter, headers=HEADERS,
    )

    assert response.status == 200

    content = await response.json()

    assert content['id'] == 1


@pytest.mark.pgsql('logs_errors_filters', files=['test_create_filter.sql'])
async def test_create_filter_with_st_key(web_app_client, auth, patch):
    _filter = copy.deepcopy(BASIC_MATCH_FILTER_BODY)
    _filter['key'] = 'TAXI-1337'

    await auth()

    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    response = await web_app_client.post(
        f'/v1/filter/', json=_filter, headers=HEADERS,
    )
    assert response.status == 200

    content = await response.json()

    assert content['id'] == 1


@pytest.mark.pgsql('logs_errors_filters', files=['test_create_filter.sql'])
async def test_create_filter_with_bad_filter(web_app_client, auth, patch):
    filter_ = copy.deepcopy(BAD_FILTER)
    filter_['key'] = 'TAXI-1337'

    await auth()

    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    response = await web_app_client.post(
        f'/v1/filter/', json=filter_, headers=HEADERS,
    )
    content = await response.json()
    assert response.status == 400
    assert content['code'] == 'WRONG_FILTER'
