import pytest

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token'}


@pytest.mark.parametrize(
    'params,expected_ids',
    [
        ({'limit': 2, 'recent_first': 1}, [5, 4]),
        ({'limit': 1, 'recent_first': 1, 'older_than': 3}, [2]),
        ({'creator': 'shrek'}, [2]),
        ({'cgroup_name': 'taxi_billing_docs', 'recent_first': 1}, [5, 4, 2]),
        (
            {
                'created_from': '2019-09-03T14:30:00+0300',
                'created_to': '2019-09-03T15:30:00+0300',
            },
            [3],
        ),
        (
            {'created_from': '2019-09-03T14:30:00+0300', 'recent_first': 1},
            [5, 4, 3],
        ),
        ({'without_cgroup': 1, 'recent_first': 1}, [5]),
    ],
)
@pytest.mark.pgsql('logs_errors_filters', files=['test_get_filter_list.sql'])
@pytest.mark.config(
    LOGSERRORS_DISABLING_SETTINGS={
        'auto_disabling': True,
        'filter_ttl_days': 45,
    },
)
async def test_get_filter_list(web_app_client, auth, params, expected_ids):
    response = await web_app_client.get(
        '/v1/filter/', headers=HEADERS, params=params,
    )
    assert response.status == 200
    error_filters = (await response.json())['filters']
    error_filters_ids = [
        error_filter['id']
        for error_filter in (await response.json())['filters']
    ]
    assert error_filters_ids == expected_ids
    error_filters_by_id = {
        error_filter['id']: error_filter for error_filter in error_filters
    }
    if 3 in error_filters_by_id:
        error_filter = error_filters_by_id[3]
        assert (
            error_filter['filter_information']['enabled_till'] == '2019-10-18'
        )
        assert error_filter['filter_information']['query']['rules'] == [
            {'field': 'text', 'matchstring': 'error occurred'},
            {'field': 'type', 'matchstring': 'log'},
        ]
