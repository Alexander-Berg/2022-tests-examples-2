from typing import Dict
from typing import List
from typing import NamedTuple
from urllib import parse as urlparse

from aiohttp import web
import pytest

from taxi_teamcity_monitoring.generated.cron import run_cron


class Params(NamedTuple):
    groupmemberships: List[Dict]
    persons: List[Dict]
    expected_staff_calls: List[Dict]
    expected_telegram_calls: List[Dict]


def staff_groupmemberships_query(department: str, page: str = '') -> str:
    return (
        f'groupmembership?_query=group.url+%3D%3D+%22{department}%22+or+'
        f'group.ancestors.url+%3D%3D+%22{department}%22&_fields=id,'
        f'person.login,group.url{page}&_sort=id&group.type='
        'department&person.official.is_dismissed=false&person.'
        'official.is_robot=false'
    )


def staff_persons_query(login: str) -> str:
    return f'persons?login={login}&_fields=telegram_accounts'


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                groupmemberships=[
                    {
                        'yandex_taxi_automatization_100500': {
                            'result': [
                                {'person': {'login': 'oyaso'}},
                                {'person': {'login': 'aselutin'}},
                            ],
                        },
                        'yandex_rkub_taxi_develop_6154': {
                            'result': [{'person': {'login': 'alberist'}}],
                        },
                        'yandex_some_group': {
                            'result': [
                                {'person': {'login': 'petya'}},
                                {'person': {'login': 'some'}},
                            ],
                        },
                        'yandex_kebab': {
                            'result': [{'person': {'login': 'kolya'}}],
                        },
                    },
                ],
                persons=[
                    {
                        'result': [
                            {'telegram_accounts': [{'value': 'selutin'}]},
                        ],
                    },
                    {'result': [{'telegram_accounts': [{'value': 'yudaev'}]}]},
                    {'result': [{'telegram_accounts': [{'value': 'petya'}]}]},
                    {'result': [{'login': 'some'}]},
                ],
                expected_staff_calls=[
                    {
                        'method': 'GET',
                        'url': staff_groupmemberships_query(
                            'yandex_taxi_automatization_100500',
                        ),
                    },
                    {'method': 'GET', 'url': staff_persons_query('aselutin')},
                    {'method': 'GET', 'url': staff_persons_query('oyaso')},
                    {
                        'method': 'GET',
                        'url': staff_groupmemberships_query(
                            'yandex_some_group',
                        ),
                    },
                    {'method': 'GET', 'url': staff_persons_query('petya')},
                    {'method': 'GET', 'url': staff_persons_query('some')},
                ],
                expected_telegram_calls=[
                    {'login': 'selutin', 'chat_id': -123456789},
                    {'login': 'selutin', 'chat_id': -987654321},
                    {'login': 'yudaev', 'chat_id': -123456789},
                    {'login': 'yudaev', 'chat_id': -987654321},
                    {'login': 'petya', 'chat_id': -123456789},
                    {'login': 'petya', 'chat_id': -111222333},
                ],
            ),
            id='add to chat',
        ),
    ],
)
@pytest.mark.config(
    TEAMCITY_MONITORING_TELEGRAM_UPDATER_ENABLED=True,
    TEAMCITY_MONITORING_TELEGRAM_UPDATER_GROUPS=[
        {
            'department': 'yandex_taxi_automatization_100500',
            'chats': [
                {'name': 'first_chat', 'id': -123456789},
                {'name': 'second_chat', 'id': -987654321},
            ],
        },
        {
            'department': 'yandex_some_group',
            'chats': [
                {'name': 'first_chat', 'id': -123456789},
                {'name': 'third_chat', 'id': -111222333},
            ],
        },
    ],
)
def test_telegram_updater(monkeypatch, mock_staff, params):
    @mock_staff('/v3', prefix=True)
    async def staff_request(request):
        if request.path.endswith('/groupmembership'):
            query = urlparse.urlparse(request.url).query
            parsed_query = urlparse.parse_qs(query)
            if '_page' not in parsed_query:
                page_no = 0
            else:
                page_no = int(parsed_query['_page'][0]) - 1
            for key in params.groupmemberships[page_no].keys():
                if key in request.url:
                    return web.json_response(
                        params.groupmemberships[page_no][key],
                    )
        if request.path.endswith('/persons'):
            response = params.persons[staff_request.person_counter]
            staff_request.person_counter += 1
            return web.json_response(response)

    staff_request.person_counter = 0

    async def mock_start_telegram_client(*args):
        mock_start_telegram_client.counter += 1
        assert mock_start_telegram_client.counter == 1

    mock_start_telegram_client.counter = 0

    async def mock_add_user_to_chat(*args):
        assert (
            args[1]
            == params.expected_telegram_calls[mock_add_user_to_chat.counter][
                'login'
            ]
        )
        assert (
            args[2]
            == params.expected_telegram_calls[mock_add_user_to_chat.counter][
                'chat_id'
            ]
        )
        mock_add_user_to_chat.counter += 1

    mock_add_user_to_chat.counter = 0

    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.telegram_updater.'
        'run_telegram_updater.start_telegram_client',
        mock_start_telegram_client,
    )
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.telegram_updater.'
        'run_telegram_updater.add_user_to_chat',
        mock_add_user_to_chat,
    )

    run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'telegram_updater.run_telegram_updater',
            '-t',
            '0',
        ],
    )

    assert staff_request.times_called == len(params.expected_staff_calls)
    i = 0
    while staff_request.has_calls:
        sf_req = staff_request.next_call()['request']
        assert sf_req.method == params.expected_staff_calls[i]['method']
        short_url = str(sf_req.url).split('/', maxsplit=5)[5]
        assert short_url == params.expected_staff_calls[i]['url']
        i += 1
