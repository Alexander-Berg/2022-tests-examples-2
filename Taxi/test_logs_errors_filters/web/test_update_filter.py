# pylint: disable=unused-variable
import copy

import pytest

BASIC_MATCH_FILTER_BODY = {
    'description': 'Description from test',
    'query': {'rules': [{'matchstring': 'some error message'}]},
}

BASIC_MATCH_FILTER_BODY_2 = {
    'description': 'Description from test',
    'query': {'rules': [{'matchstring': 'some other message'}]},
    'cgroup': 'taxi_fake_cgroup',
    'key': 'TAXI-1337',
    'creator': 'defaultcreator',
    'for_all_groups': False,
    'enabled': True,
    'threshold': 0,
    'filter_interval_minutes': 15,
    'suppress_related_errors': False,
}

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token', 'X-Yandex-Login': 'testcreator'}


@pytest.mark.parametrize(
    'data_for_update', [{'threshold': 0}, {'threshold': 1}],
)
@pytest.mark.pgsql('logs_errors_filters', files=['test_update_filter.sql'])
async def test_update_filter(
        patch, web_app_client, create_filter, auth, data_for_update,
):
    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    filter_id = await create_filter(
        BASIC_MATCH_FILTER_BODY['query'],
        BASIC_MATCH_FILTER_BODY['description'],
    )

    assert filter_id == 1
    await auth()
    expected_content = copy.deepcopy(BASIC_MATCH_FILTER_BODY_2)
    expected_content.update(data_for_update)
    response = await web_app_client.put(
        f'/v1/filter/1/', json=expected_content, headers=HEADERS,
    )
    assert response.status == 200
    response = await web_app_client.get(f'/v1/filter/1/', headers=HEADERS)
    assert response.status == 200

    content = await response.json()
    assert content['id'] == 1
    assert 'filter_information' in content

    del content['filter_information']['created']
    assert content['filter_information'] == expected_content


@pytest.mark.pgsql('logs_errors_filters', files=['test_set_enabled_at.sql'])
@pytest.mark.config(
    LOGSERRORS_DISABLING_SETTINGS={
        'auto_disabling': True,
        'filter_ttl_days': 45,
    },
)
async def test_set_enabled_at(patch, web_app_client, auth):
    await auth()

    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    data = {
        'description': 'test',
        'query': {'rules': [{'matchstring': ''}]},
        'cgroup': 'taxi_billing_replication',
        'enabled': True,
    }
    response = await web_app_client.put(
        f'/v1/filter/1/', json=data, headers=HEADERS,
    )
    assert response.status == 200
    response = await web_app_client.put(
        f'/v1/filter/2/', json=data, headers=HEADERS,
    )
    assert response.status == 200
    response = await web_app_client.get(f'/v1/filter/', headers=HEADERS)
    assert response.status == 200
    result = await response.json()
    for item in result['filters']:
        assert item['filter_information']['enabled'] is True
        if item['id'] == 2:
            assert item['filter_information']['enabled_till'] == '2019-10-18'
        else:
            assert item['filter_information']['enabled_till'] > '2019-10-18'
