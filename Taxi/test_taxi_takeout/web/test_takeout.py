# pylint: disable=protected-access
import json
import typing

from bson import ObjectId
import pytest

from taxi_takeout import tasks
from taxi_takeout.tasks.accepted_eulas.model import AcceptedEula
from taxi_takeout.tasks.cards.model import Card
from taxi_takeout.tasks.promocode_usages.model import PromoCodeUsage
from taxi_takeout.tasks.promocode_usages2.model import PromoCodeUsage2
from taxi_takeout.tasks.support.task import SupportData
from taxi_takeout.tasks.user_consent.model import UserConsent
from taxi_takeout.tasks.user_emails.model import UserEmail
from taxi_takeout.tasks.user_phones.model import UserPhone
from taxi_takeout.tasks.users.models import User

UID_NOT_FOUND = 'uid_not_found'


@pytest.fixture(name='mock_takeout')
def mock_takeout_fixture(
        request, patch_aiohttp_session, response_mock, load_json,
):
    def _mock_takeout(
            service_name, host_url, request_data=None, response_status=200,
    ):
        @patch_aiohttp_session(host_url, 'PUT')
        def _mock_api(method, url, *args, **kwargs):
            _mock_api.times_called += 1
            assert url == host_url + '/v1/takeout/job', url
            if request_data:
                assert kwargs['json'] == request_data
            assert kwargs['headers']['Accept-Language'] == request.param[0]
            return response_mock(status=response_status)

        _mock_api.times_called = 0
        return _mock_api

    return _mock_takeout


@pytest.mark.parametrize(
    'mock_takeout',
    [
        pytest.param(
            ['ru-RU'],
            marks=pytest.mark.config(
                TAKEOUT_SERVICES_V2=[
                    {
                        'name': 'ridehistory',
                        'data_category': '',
                        'host': 'ridehistory_host',
                        'endpoints': {
                            'takeout_async': {
                                'path': '/v1/takeout/job',
                                'method': 'PUT',
                            },
                        },
                    },
                ],
            ),
        ),
    ],
    indirect=['mock_takeout'],
)
async def test_create_job(
        web_app_client,
        pgsql,
        mockserver,
        mock_takeout,
        get_stats_by_label_values,
):
    mock_takeout_ = mock_takeout('ridehistory', 'ridehistory_host')
    response = await web_app_client.post(
        '/v1/jobs/create',
        data={'uid': '777', 'unixtime': 123456789},
        headers={'Accept-Language': 'ru-RU'},
    )

    @mockserver.handler('/ridehistory/v1/takeout/job')
    def _get_takeout_job_status(request):
        return mockserver.make_response(json={'status': 'pending'})

    assert response.status == 200

    db = pgsql['taxi_takeout']
    cursor = db.cursor()
    cursor.execute('SELECT job_id, uid FROM takeout.jobs')
    jobs = list(cursor)

    response_json = await response.json()
    stats = get_stats_by_label_values(
        web_app_client.app['context'], {'sensor': 'jobs.load_queries_count'},
    )
    assert mock_takeout_.times_called == 1
    assert len(jobs) == 2
    assert jobs[0][1] == '777'
    assert response_json == {'status': 'ok', 'job_id': jobs[0][0]}
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'sensor': 'jobs.load_queries_count'},
            'value': 1,
            'timestamp': None,
        },
    ]


# pylint: disable=too-many-arguments
@pytest.mark.config(
    TAKEOUT_SERVICES_V2=[
        {
            'name': 'chatterbox',
            'data_category': 'taxi',
            'host': 'http://chatterbox.taxi.dev.yandex.net',
            'endpoints': {'takeout': {'path': '/v33/takeout'}},
        },
    ],
    TAKEOUT_ENABLE_GENERIC_API=True,
    PERSONAL_EMAILS_RETRIEVE_PY3_ENABLED=True,
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    TVM_RULES=[{'src': 'taxi-takeout', 'dst': 'personal'}],
)
@pytest.mark.parametrize(
    ['job_id', 'mock_chatterbox_api', 'exp_jobs', 'exp_status', 'exp_data'],
    [
        pytest.param(
            'job_id_uid_not_found',
            {'status': 'no_data'},
            None,
            'no_data',
            None,
            marks=pytest.mark.pgsql(
                'taxi_takeout', files=['taxi_takeout_status_simple.sql'],
            ),
        ),
        pytest.param(
            'job_id_uid_not_found',
            {'status': 'pending'},
            None,
            'no_data',
            None,
            marks=pytest.mark.pgsql(
                'taxi_takeout', files=['taxi_takeout_status_simple.sql'],
            ),
        ),
        pytest.param(
            'job_id_uid_not_found',
            None,
            [('job_id_portal_user', 'portal_user', 'takeout')],
            'no_data',
            None,
            marks=pytest.mark.pgsql(
                'taxi_takeout', files=['taxi_takeout_status_simple.sql'],
            ),
        ),
        pytest.param(
            'job_id_portal_user',
            {'status': 'no_data'},
            [('job_id_uid_not_found', 'uid_not_found', 'takeout')],
            'ok',
            {
                'user_emails.json': [
                    {
                        'email': 'test@yandex.ru',
                        'confirmed': True,
                        'created': {'$date': '2017-07-24T13:45:23.492Z'},
                        'updated': {'$date': '2018-11-21T11:02:30.152Z'},
                    },
                ],
            },
            marks=pytest.mark.pgsql(
                'taxi_takeout', files=['taxi_takeout_status_simple.sql'],
            ),
        ),
        pytest.param(
            'job_id_portal_user', {'status': 'no_data'}, None, 'no_data', None,
        ),
        pytest.param(
            'job_id_portal_user',
            {'status': 'ok', 'data': {'orders': [{'a': 'b'}]}},
            [('job_id_uid_not_found', 'uid_not_found', 'takeout')],
            'ok',
            {
                'chatterbox.json': {'orders': [{'a': 'b'}]},
                'user_emails.json': [
                    {
                        'email': 'test@yandex.ru',
                        'confirmed': True,
                        'created': {'$date': '2017-07-24T13:45:23.492Z'},
                        'updated': {'$date': '2018-11-21T11:02:30.152Z'},
                    },
                ],
            },
            marks=pytest.mark.pgsql(
                'taxi_takeout', files=['taxi_takeout_status_simple.sql'],
            ),
        ),
        pytest.param(
            'portal_user',
            {'status': 'ok', 'data': {'orders': [{'a': 'b'}]}},
            [],
            'ok',
            {
                'chatterbox.json': {'orders': [{'a': 'b'}]},
                'user_emails.json': [
                    {
                        'email': 'test@yandex.ru',
                        'confirmed': True,
                        'created': {'$date': '2017-07-24T13:45:23.492Z'},
                        'updated': {'$date': '2018-11-21T11:02:30.152Z'},
                    },
                ],
            },
            marks=pytest.mark.pgsql(
                'taxi_takeout', files=['taxi_takeout_status_old.sql'],
            ),
        ),
        pytest.param(
            'job_id_portal_user', {'status': 'no_data'}, None, 'no_data', None,
        ),
    ],
    indirect=['mock_chatterbox_api'],
)
async def test_status_job(
        web_app_client,
        mockserver,
        pgsql,
        mock_archive_api,
        mock_taximeter_api,
        mock_chatterbox_api,
        mock_personal_api,
        mock_user_api,
        mock_support_api,
        job_id,
        exp_jobs,
        exp_status,
        exp_data,
        get_stats_by_list_label_values,
        load_json,
):

    response = await web_app_client.post(
        '/v1/jobs/status',
        data={'job_id': job_id},
        headers={'Accept-Language': 'ru-Ru'},
    )

    assert response.status == 200

    data = await response.json()
    assert data['status'] == exp_status

    if exp_status != 'ok':
        return

    lables_list = [
        {'sensor': 'jobs.count_success_finished_queries'},
        {'sensor': 'jobs.takeout_load_time'},
    ]
    if job_id == '777':
        lables_list.append({'sensor': 'jobs.load_queries_count'})
    stats = get_stats_by_list_label_values(
        web_app_client.app['context'], lables_list,
    )
    assert stats[0] == [
        {
            'kind': 'IGAUGE',
            'labels': {'sensor': 'jobs.count_success_finished_queries'},
            'value': 1,
            'timestamp': None,
        },
    ]
    assert stats[1][0]['labels'] == {'sensor': 'jobs.takeout_load_time'}
    assert stats[1][0]['kind'] == 'DGAUGE'
    if job_id == '777':
        assert stats[2] == [
            {
                'kind': 'IGAUGE',
                'labels': {'sensor': 'jobs.load_queries_count'},
                'timestamp': None,
                'value': 1,
            },
        ]
        return

    assert 'data' in data

    for key, exp_value in exp_data.items():
        value = data['data'].get(key)
        if key == 'taximeter.json':
            exp_value = load_json('taximeter_api_response.json')
        assert isinstance(value, str)
        assert json.loads(value) == exp_value

    db = pgsql['taxi_takeout']
    cursor = db.cursor()
    cursor.execute(
        'SELECT job_id, uid, service_name FROM'
        ' takeout.jobs ORDER BY job_id, service_name',
    )

    assert list(cursor) == exp_jobs


def get_task_param():
    return tasks.TaskParams(
        yandex_uid='portal_user',
        users=[
            User(
                id='user_id_1',
                yandex_uid='portal_user',
                phone_id=ObjectId('00aaaaaaaaaaaaaaaaaaaa01'),
                created=None,
                updated=None,
                application='android',
                application_version=None,
                authorized=None,
                brand='yataxi',
            ),
        ],
        headers={},
    )


@pytest.mark.parametrize(
    'task, result_type',
    [
        pytest.param(
            tasks.AcceptedEulasTask, AcceptedEula, id='accepted_eulas',
        ),
        pytest.param(tasks.CardsTask, Card, id='cards'),
        pytest.param(tasks.PhonesTask, UserPhone, id='phones'),
        pytest.param(tasks.UserTask, User, id='users'),
        pytest.param(
            tasks.PromocodesUsagesTask, PromoCodeUsage, id='promocodes',
        ),
        pytest.param(
            tasks.PromocodesUsages2Task, PromoCodeUsage2, id='promocodes2',
        ),
        pytest.param(tasks.ConsentsTask, UserConsent, id='consent'),
        pytest.param(tasks.EmailsTask, UserEmail, id='emails'),
        pytest.param(tasks.SupportTask, SupportData, id='support'),
        pytest.param(tasks.TaximeterTask, typing.Dict, id='taximeter'),
    ],
)
@pytest.mark.config(
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    PERSONAL_EMAILS_RETRIEVE_PY3_ENABLED=True,
    TVM_RULES=[{'src': 'taxi-takeout', 'dst': 'personal'}],
)
@pytest.mark.now('2019-04-09')
async def test_tasks(
        web_context,
        mock_chatterbox_api,
        mock_personal_api,
        mock_user_api,
        task,
        result_type,
        mock_archive_api,
        mock_support_api,
        mock_taximeter_api,
):
    task = task(web_context)
    result = await task.execute(get_task_param())

    assert result.name == task._data_name
    assert result.data
    assert isinstance(result.data, typing.Iterable)

    for data in result.data:
        assert isinstance(data, result_type)
        if isinstance(data, typing.Dict):
            assert any(data.values())
        else:
            assert any(data._asdict().values())


EXPECTED_NOT_CONFIRMED = {
    'warning': (
        'Your phone number was not confirmed in the taxi application. '
        'Please, confirm your phone number in the application.'
    ),
}

EXPECTED_NOT_CONFIRMED_FOR_N_DAYS = {
    'warning': (
        'Your phone number was confirmed in the '
        'taxi application more than 90 days ago. '
        'Please, confirm your phone number in the application.'
    ),
}


def answer_assertion(result, expected):
    assert result.data
    assert isinstance(result.data, typing.Iterable)

    for data in result.data:
        if hasattr(data, '_asdict'):
            assert data._asdict() == expected
        else:
            assert data == expected


@pytest.mark.pgsql('taxi_takeout', files=['taxi_takeout_result.sql'])
@pytest.mark.parametrize(
    ['job_id', 'service_name', 'result', 'status', 'jobs'],
    [
        pytest.param(
            'job_id_found_pending',
            'ridehistory',
            '{"a": "b", "c": "d"}',
            200,
            [
                ('job_id_found_done', 'ridehistory', 'done', None),
                (
                    'job_id_found_pending',
                    'ridehistory',
                    'done',
                    '{"a": "b", "c": "d"}',
                ),
                (
                    'job_id_found_with_result',
                    'ridehistory',
                    'done',
                    'some_result',
                ),
                ('job_id_not_found_service', 'safety_center', 'pending', None),
            ],
        ),
        pytest.param(
            'job_id_found_pending',
            'ridehistory',
            None,
            200,
            [
                ('job_id_found_done', 'ridehistory', 'done', None),
                ('job_id_found_pending', 'ridehistory', 'done', None),
                (
                    'job_id_found_with_result',
                    'ridehistory',
                    'done',
                    'some_result',
                ),
                ('job_id_not_found_service', 'safety_center', 'pending', None),
            ],
        ),
        pytest.param(
            'job_id_not_found',
            'ridehistory',
            '{"a": "b", "c": "d"}',
            200,
            [
                ('job_id_found_done', 'ridehistory', 'done', None),
                ('job_id_found_pending', 'ridehistory', 'pending', None),
                (
                    'job_id_found_with_result',
                    'ridehistory',
                    'done',
                    'some_result',
                ),
                (
                    'job_id_not_found',
                    'ridehistory',
                    'done',
                    '{"a": "b", "c": "d"}',
                ),
                ('job_id_not_found_service', 'safety_center', 'pending', None),
            ],
        ),
        pytest.param(
            'job_id_found_done',
            'ridehistory',
            '{"a": "b", "c": "d"}',
            200,
            [
                (
                    'job_id_found_done',
                    'ridehistory',
                    'done',
                    '{"a": "b", "c": "d"}',
                ),
                ('job_id_found_pending', 'ridehistory', 'pending', None),
                (
                    'job_id_found_with_result',
                    'ridehistory',
                    'done',
                    'some_result',
                ),
                ('job_id_not_found_service', 'safety_center', 'pending', None),
            ],
        ),
        pytest.param(
            'job_id_not_found_service',
            'ridehistory',
            '{"a": "b", "c": "d"}',
            200,
            [
                ('job_id_found_done', 'ridehistory', 'done', None),
                ('job_id_found_pending', 'ridehistory', 'pending', None),
                (
                    'job_id_found_with_result',
                    'ridehistory',
                    'done',
                    'some_result',
                ),
                (
                    'job_id_not_found_service',
                    'ridehistory',
                    'done',
                    '{"a": "b", "c": "d"}',
                ),
                ('job_id_not_found_service', 'safety_center', 'pending', None),
            ],
        ),
        pytest.param(
            'job_id_found_with_result',
            'ridehistory',
            '{"a": "b", "c": "d"}',
            200,
            [
                ('job_id_found_done', 'ridehistory', 'done', None),
                ('job_id_found_pending', 'ridehistory', 'pending', None),
                (
                    'job_id_found_with_result',
                    'ridehistory',
                    'done',
                    '{"a": "b", "c": "d"}',
                ),
                ('job_id_not_found_service', 'safety_center', 'pending', None),
            ],
        ),
    ],
)
async def test_job_result(
        web_app_client, pgsql, job_id, service_name, result, status, jobs,
):
    data = dict(job_id=job_id, service_name=service_name)
    if result:
        data['result'] = result
    response = await web_app_client.post('/v1/jobs/done', json=data)

    assert response.status == status

    db = pgsql['taxi_takeout']
    cursor = db.cursor()
    cursor.execute(
        'SELECT job_id, service_name, status, result,'
        'created_at, updated_at FROM'
        ' takeout.jobs ORDER BY job_id, service_name',
    )

    results = list(cursor)
    for idx, res in enumerate(results):
        if res[0] == job_id and res[1] == service_name and 'result' in data:
            assert res[4] is not None
            assert res[5] is not None
            assert res[4] != res[5]
        results[idx] = res[:4]
    assert results == jobs
