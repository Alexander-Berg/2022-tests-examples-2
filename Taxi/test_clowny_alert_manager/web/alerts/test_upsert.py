import pytest

from taxi.clients import juggler_api


@pytest.fixture(name='mock_juggler_checks_add_or_update')
def _mock_juggler_checks_add_or_update(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/checks/add_or_update', 'POST',
    )
    def _checks_add_or_update(method, url, **kwargs):
        assert 'Authorization' in kwargs['headers']
        assert kwargs['params']['do'] == 1
        data = kwargs['json']
        assert data['service'] == 'hejmdal'
        assert data['host'] == 'hejmdal_stable'
        assert data['aggregator'] == 'timed_more_than_limit_is_problem'
        assert data['aggregator_kwargs'] == {
            'ignore_nodata': True,
            'limits': [
                {
                    'day_start': 1,
                    'day_end': 5,
                    'time_start': '12',
                    'time_end': '20',
                    'warn': 0,
                    'crit': 0,
                },
                {
                    'day_start': 6,
                    'day_end': 7,
                    'time_start': '12',
                    'time_end': '20',
                    'warn': 0,
                    'crit': 0,
                },
                {
                    'day_start': 1,
                    'day_end': 7,
                    'time_start': '21',
                    'time_end': '11',
                    'warn': 0,
                    'crit': '101%',
                },
            ],
        }
        if len(data['children']) > 1:
            assert data['children'] == [
                {
                    'host': 'test_raw_event_host_man',
                    'service': 'hejmdal',
                    'type': 'HOST',
                    'instance': '',
                },
                {
                    'host': 'test_raw_event_host_sas',
                    'service': 'hejmdal',
                    'type': 'HOST',
                    'instance': '',
                },
            ]
        else:
            assert data['children'] == [
                {
                    'host': 'test_raw_event_host',
                    'service': 'hejmdal',
                    'type': 'HOST',
                    'instance': '',
                },
            ]
        assert data['notifications'] == [
            {
                'template_name': 'on_status_change',
                'template_kwargs': {
                    'login': ['oboroth', 'alexrasyuk'],
                    'method': 'telegram',
                    'status': [
                        {'from': 'OK', 'to': 'CRIT'},
                        {'from': 'WARN', 'to': 'CRIT'},
                        {'from': 'CRIT', 'to': 'WARN'},
                        {'from': 'CRIT', 'to': 'OK'},
                        {'from': 'OK', 'to': 'WARN'},
                        {'from': 'WARN', 'to': 'OK'},
                    ],
                },
                'description': None,
            },
        ]
        assert data['namespace'] == 'taxi.platform.prod'

        return response_mock(json={'status': 200})

    return _checks_add_or_update


async def test_alerts(web_app_client, mock_juggler_checks_add_or_update):
    response = await web_app_client.post(
        '/v1/alerts/upsert/',
        json={
            'service_id': 139,
            'branch_id': 1,
            'juggler_service': 'hejmdal',
            'juggler_raw_event_host': 'test_raw_event_host',
            'recipients': ['oboroth', 'alexrasyuk'],
        },
    )
    assert response.status == 200


async def test_alerts_multiple_raw_event_hosts(
        web_app_client, mock_juggler_checks_add_or_update,
):
    response = await web_app_client.post(
        '/v1/alerts/upsert/',
        json={
            'service_id': 139,
            'branch_id': 1,
            'juggler_service': 'hejmdal',
            'juggler_raw_event_hosts': [
                'test_raw_event_host_man',
                'test_raw_event_host_sas',
            ],
            'recipients': ['oboroth', 'alexrasyuk'],
        },
    )
    assert response.status == 200
