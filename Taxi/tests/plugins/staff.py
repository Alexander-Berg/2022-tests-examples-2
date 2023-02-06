import pytest

from taxi_buildagent import report_utils


@pytest.fixture
def staff_persons_mock(patch_requests, monkeypatch, mock):
    monkeypatch.setenv('STAFF_TOKEN', 'staff-token')

    # Reset LRU cache before each test
    # pylint: disable=protected-access
    report_utils._resolve_telegram_login.cache_clear()

    @mock
    def logins(login):
        if login.endswith('_no'):
            return None
        return 'tg_' + login

    @patch_requests('https://staff-api.yandex-team.ru/v3/persons')
    def _persons(method, url, **kwargs):
        assert url == 'https://staff-api.yandex-team.ru/v3/persons'
        assert kwargs['headers'] == {'Authorization': 'OAuth staff-token'}
        assert method.upper() == 'GET'
        fields = kwargs['params']['_fields'].split(',')
        assert 'accounts' in fields
        assert 'login' in fields
        split_logins = kwargs['params']['login'].split(',')
        tg_logins = [logins(login) for login in split_logins]
        result = [
            {
                'login': login,
                'accounts': (
                    [
                        {'type': 'telegram', 'value': 'nope', 'private': True},
                        {
                            'type': 'telegram',
                            'value': 'sai_bot',
                            'private': False,
                        },
                        {'type': 'telegram', 'value': tg, 'private': False},
                    ]
                    if tg is not None
                    else []
                ),
            }
            for login, tg in zip(split_logins, tg_logins)
        ]
        return patch_requests.response(json={'result': result})

    return logins
