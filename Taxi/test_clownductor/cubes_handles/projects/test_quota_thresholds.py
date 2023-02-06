import pytest


COMMENT_TEXT = """Недостаточно квоты для проекта {project_name}.
ABC квота: ((https://abc.yandex-team.ru/services/{abc_quota}/ {abc_quota})).
Namespace: {namespace}

{spoiler_start}Ошибка
{error_message}
{spoiler_end}

{spoiler_start}Для эксплуатации
Если сервис все равно нужно создать,
то пометьте кубик в (({tariff_editor_link} джобе))
кубик ProjectsWaitYPQuotaThreshold как выполненный
и процесс создания пойдет дальше
{spoiler_end}{problem_slug_phrase}"""

EXPECTED_COMMENT_TEXT = """Недостаточно квоты для проекта taxi-devops.
ABC квота: ((https://abc.yandex-team.ru/services/devops/ devops)).
Namespace: devops-namespace

<{Ошибка
Segment **default** in **MAN**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||cpu | 163.5 cores | 234 cores | Usage 69.87% > Limit 60%||
||hdd | 5523.9 GB | 7600 GB | Usage 72.68% > Limit 70%||
||ssd | 732.62 GB | 829.44 GB | Diff 96.82 GB < 1200 GB||
||hdd_io | 911 MB/s | 972 MB/s | Diff 61 MB/s < 500 MB/s
Usage 93.72% > Limit 90%||
|#

Segment **default** in **SAS**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||hdd | 5523.9 GB | 7600 GB | Usage 72.68% > Limit 60%||
||hdd_io | 911 MB/s | 972 MB/s | Diff 61 MB/s < 400 MB/s
Usage 93.72% > Limit 90%||
|#

Segment **default** in **VLA**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||hdd_io | 911 MB/s | 972 MB/s | Usage 93.72% > Limit 90%||
||network | 911 MB/s | 972 MB/s | Usage 93.72% > Limit 90%||
|#

}>

<{Для эксплуатации
Если сервис все равно нужно создать,
то пометьте кубик в ((/services/1/edit/1/jobs?jobId=1&isClownJob=true джобе))
кубик ProjectsWaitYPQuotaThreshold как выполненный
и процесс создания пойдет дальше
}>

Problem slug: quotaexceededproblem"""

EXPECTED_COMMENT_TEXT_NO_SSD = """Недостаточно квоты для проекта taxi-devops.
ABC квота: ((https://abc.yandex-team.ru/services/devops/ devops)).
Namespace: devops-namespace

<{Ошибка
Segment **default** in **MAN**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||cpu | 163.5 cores | 234 cores | Usage 69.87% > Limit 60%||
||hdd | 5523.9 GB | 7600 GB | Usage 72.68% > Limit 70%||
||hdd_io | 911 MB/s | 972 MB/s | Diff 61 MB/s < 500 MB/s
Usage 93.72% > Limit 90%||
|#

Segment **default** in **SAS**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||hdd | 5523.9 GB | 7600 GB | Usage 72.68% > Limit 60%||
||hdd_io | 911 MB/s | 972 MB/s | Diff 61 MB/s < 400 MB/s
Usage 93.72% > Limit 90%||
|#

Segment **default** in **VLA**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||hdd_io | 911 MB/s | 972 MB/s | Usage 93.72% > Limit 90%||
||network | 911 MB/s | 972 MB/s | Usage 93.72% > Limit 90%||
|#

}>

<{Для эксплуатации
Если сервис все равно нужно создать,
то пометьте кубик в ((/services/1/edit/1/jobs?jobId=1&isClownJob=true джобе))
кубик ProjectsWaitYPQuotaThreshold как выполненный
и процесс создания пойдет дальше
}>

Problem slug: quotaexceededproblem"""


EXPECTED_COMMENT_TEXT_NO_HDD = """Недостаточно квоты для проекта taxi-devops.
ABC квота: ((https://abc.yandex-team.ru/services/devops/ devops)).
Namespace: devops-namespace

<{Ошибка
Segment **default** in **MAN**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||cpu | 163.5 cores | 234 cores | Usage 69.87% > Limit 60%||
||ssd | 732.62 GB | 829.44 GB | Diff 96.82 GB < 1200 GB||
|#

Segment **default** in **VLA**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||network | 911 MB/s | 972 MB/s | Usage 93.72% > Limit 90%||
|#

}>

<{Для эксплуатации
Если сервис все равно нужно создать,
то пометьте кубик в ((/services/1/edit/1/jobs?jobId=1&isClownJob=true джобе))
кубик ProjectsWaitYPQuotaThreshold как выполненный
и процесс создания пойдет дальше
}>

Problem slug: quotaexceededproblem"""

COMMENT_TEXT_WITH_PROBLEM_SLUG = """Недостаточно квоты для проекта taxi-devops.
ABC квота: ((https://abc.yandex-team.ru/services/devops/ devops)).
Namespace: devops-namespace

<{Ошибка
Segment **default** in **MAN**:
#|
|| Ресурс| Использование | Предел | Ошибки||
||cpu | 160 cores | 200 cores | Usage 80% > Limit 60%||
|#

}>

<{Для эксплуатации
Если сервис все равно нужно создать,
то пометьте кубик в ((/services/1/edit/1/jobs?jobId=1&isClownJob=true джобе))
кубик ProjectsWaitYPQuotaThreshold как выполненный
и процесс создания пойдет дальше
}>

Problem slug: quotaexceededproblem"""

TRANSLATIONS = {
    'tickets.projects_wait_quota_threshold_comment': {'ru': COMMENT_TEXT},
}

CONFIG = {
    'yp_namespaces': {
        '__default__': 'default-namespace',
        'devops': 'devops-namespace',
    },
    'yp': {
        '__default__': {
            'enabled': True,
            'regions': {
                '__default__': {
                    '__default__': {'percent_limit': 0.9},
                    'cpu': {'percent_limit': 0.85, 'number_limit_cores': 10},
                    'ram': {'percent_limit': 0.9, 'number_limit_gb': 100},
                    'hdd_io': {'number_limit_mb_per_sec': 10},
                    'network': {'number_limit_mb_per_sec': 10},
                },
            },
        },
        'devops': {
            'enabled': True,
            'regions': {
                '__default__': {'__default__': {'percent_limit': 0.9}},
                'MAN': {
                    'cpu': {'percent_limit': 0.6},
                    'ssd': {'number_limit_gb': 1200, 'percent_limit': 0.9},
                    'hdd': {'number_limit_gb': 1200, 'percent_limit': 0.7},
                    'ssd_io': {'percent_limit': 0.9},
                    'hdd_io': {
                        'number_limit_mb_per_sec': 500,
                        'percent_limit': 0.9,
                    },
                },
                'SAS': {
                    'cpu': {'percent_limit': 0.7},
                    'ssd': {'number_limit_gb': 50, 'percent_limit': 0.9},
                    'hdd': {'number_limit_gb': 120, 'percent_limit': 0.6},
                    'ssd_io': {'percent_limit': 0.9},
                    'hdd_io': {
                        'number_limit_mb_per_sec': 400,
                        'percent_limit': 0.9,
                    },
                },
            },
        },
        'clients': {'enabled': False},
    },
}


@pytest.fixture(name='yp_get_quota')
def _yp_get_quota(mockserver, load_json):
    @mockserver.json_handler('/yp-api/ObjectService/GetObject')
    def handler(request):
        assert request.json == {
            'object_type': 'account',
            'object_id': 'abc:service:3155',
            'selector': {'paths': ['/spec', '/status']},
        }
        return load_json('taxi_devops_quota.json')

    return handler


@pytest.mark.parametrize(
    'comments',
    [
        [],
        [
            {
                'id': 1,
                'text': COMMENT_TEXT_WITH_PROBLEM_SLUG,
                'createdBy': {'id': 'robot-taxi-infra'},
                'createdAt': '2021-12-02T16:00:00.000+0000',
            },
        ],
    ],
)
@pytest.mark.usefixtures('st_get_myself', 'st_get_ticket')
@pytest.mark.translations(clownductor=TRANSLATIONS)
@pytest.mark.config(CLOWNDUCTOR_QUOTA_THRESHOLDS_BY_REGIONS=CONFIG)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_wait_quota_threshold(
        call_cube_handle,
        abc_mockserver,
        yp_get_quota,
        st_create_comment,
        patch,
        comments,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        if kwargs.get('short_id') is not None:
            return []
        return comments

    abc_mock = abc_mockserver(services=['devops'])

    await call_cube_handle(
        'ProjectsWaitYPQuotaThreshold',
        {
            'content_expected': {
                'status': 'in_progress',
                'sleep_duration': 30,
            },
            'data_request': {
                'input_data': {
                    'project_name': 'taxi-devops',
                    'project_quota_slug': 'devops',
                    'st_ticket': 'TAXIADMIN-123',
                    'yp_locations': ['man', 'sas', 'vla'],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert abc_mock.times_called == 1
    assert yp_get_quota.times_called == 3
    st_create_comment_calls = st_create_comment.calls
    if comments:
        assert not st_create_comment_calls
    else:
        assert len(st_create_comment_calls) == 1
        assert st_create_comment_calls[0]['text'] == EXPECTED_COMMENT_TEXT


@pytest.mark.config(CLOWNDUCTOR_QUOTA_THRESHOLDS_BY_REGIONS=CONFIG)
async def test_quota_check_disable(call_cube_handle):
    await call_cube_handle(
        'ProjectsWaitYPQuotaThreshold',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'project_name': 'taxi-clients',
                    'project_quota_slug': 'clients',
                    'st_ticket': 'TAXIADMIN-123',
                    'yp_locations': ['man', 'sas', 'vla'],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )


@pytest.mark.config(CLOWNDUCTOR_QUOTA_THRESHOLDS_BY_REGIONS=CONFIG)
async def test_fallback_default_success(
        call_cube_handle, abc_mockserver, yp_get_quota,
):
    abc_mock = abc_mockserver(services=['meow'])

    await call_cube_handle(
        'ProjectsWaitYPQuotaThreshold',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'project_name': 'taxi-meow',
                    'project_quota_slug': 'meow',
                    'st_ticket': 'TAXIADMIN-123',
                    'yp_locations': ['man', 'sas', 'vla'],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    assert abc_mock.times_called == 1
    assert yp_get_quota.times_called == 3


@pytest.mark.parametrize(
    'expected_comment_text, drive_types',
    [
        pytest.param(EXPECTED_COMMENT_TEXT, ['ssd', 'hdd'], id='ssd/hdd'),
        pytest.param(EXPECTED_COMMENT_TEXT_NO_HDD, ['ssd'], id='ssd'),
        pytest.param(EXPECTED_COMMENT_TEXT_NO_SSD, ['hdd'], id='hdd'),
        pytest.param(EXPECTED_COMMENT_TEXT, [], id='empty'),
    ],
)
@pytest.mark.usefixtures('st_get_myself', 'st_get_ticket')
@pytest.mark.translations(clownductor=TRANSLATIONS)
@pytest.mark.config(CLOWNDUCTOR_QUOTA_THRESHOLDS_BY_REGIONS=CONFIG)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_check_quota_threshold(
        call_cube_handle,
        abc_mockserver,
        yp_get_quota,
        st_create_comment,
        patch,
        expected_comment_text,
        drive_types,
):
    abc_mockserver(services=['devops'])

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        return []

    await call_cube_handle(
        'ProjectsWaitYPQuotaThreshold',
        {
            'content_expected': {
                'status': 'in_progress',
                'sleep_duration': 30,
            },
            'data_request': {
                'input_data': {
                    'project_name': 'taxi-devops',
                    'project_quota_slug': 'devops',
                    'st_ticket': 'TAXIADMIN-123',
                    'yp_locations': ['man', 'sas', 'vla'],
                    'drive_types': drive_types,
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    st_create_comment_calls = st_create_comment.calls
    assert len(st_create_comment_calls) == 1
    assert st_create_comment_calls[0]['text'] == expected_comment_text
