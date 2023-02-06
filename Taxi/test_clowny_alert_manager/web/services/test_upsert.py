import json

import pytest

from testsuite.utils import matching

from test_clowny_alert_manager.helpers import builders


@pytest.fixture(name='upsert_service')
def _upsert_service(upsert_service):
    async def _wrapper(data, status=200, use_draft_api=False):
        if not use_draft_api:
            return await upsert_service(data, status)
        response = await upsert_service(data, status, 'check')
        if status != 200:
            return response
        return await upsert_service(response['data'], status, 'apply')

    return _wrapper


def case(*, data, status, result, objects_in_queue=None, id_=None):
    return pytest.param(data, status, result, objects_in_queue, id=id_)


@pytest.mark.parametrize('use_draft_api', [True, False])
@pytest.mark.parametrize(
    'data, status, result, objects_in_queue',
    [
        case(
            data={
                'type': 'cgroup',
                'service_name': 'srv_1',
                'project_name': 'prj_1',
                'branches': [
                    {
                        'names': ['branch1'],
                        'clown_branch_ids': [],
                        'repo_meta': {
                            'file_name': 'foo.yaml',
                            'file_path': 'ns1/foo.yaml',
                            'config_project': 'taxi',
                        },
                        'namespace': 'ns1',
                        'basename': 'branch1',
                        'juggler_host': 'branch1',
                    },
                ],
                'repo_meta': {'config_project': 'taxi'},
            },
            status=200,
            result={
                'id': 1,
                'is_deleted': False,
                'project_name': 'prj_1',
                'service_name': 'srv_1',
                'type': 'cgroup',
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'repo_meta': {'config_project': 'taxi'},
                'branches': [
                    {
                        'names': ['branch1'],
                        'clown_branch_ids': [],
                        'repo_meta': {
                            'file_name': 'foo.yaml',
                            'file_path': 'ns1/foo.yaml',
                            'config_project': 'taxi',
                        },
                        'namespace': 'ns1',
                        'service_id': 1,
                        'configs': [],
                        'basename': 'branch1',
                        'juggler_host': 'branch1',
                    },
                ],
            },
        ),
        case(
            data={
                'type': 'rtc',
                'service_name': 'clownductor',
                'project_name': 'taxi-infra',
                'clown_service_id': 1,
                'clown_project_id': 150,
                'repo_meta': {'config_project': 'taxi'},
                'branches': [
                    {
                        'names': ['taxi_clownductor_stable'],
                        'clown_branch_ids': [1],
                        'repo_meta': {
                            'file_name': 'foo.yaml',
                            'file_path': 'ns1/foo.yaml',
                            'config_project': 'taxi',
                        },
                        'configs': [],
                        'namespace': 'ns1',
                        'basename': 'taxi_clownductor_stable',
                        'juggler_host': 'taxi_clownductor_stable',
                    },
                ],
            },
            status=200,
            result={
                'id': 1,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'service_name': 'clownductor',
                'clown_project_id': 150,
                'clown_service_id': 1,
                'type': 'rtc',
                'repo_meta': {'config_project': 'taxi'},
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'branches': [
                    {
                        'names': ['taxi_clownductor_stable'],
                        'clown_branch_ids': [1],
                        'repo_meta': {
                            'file_name': 'foo.yaml',
                            'file_path': 'ns1/foo.yaml',
                            'config_project': 'taxi',
                        },
                        'namespace': 'ns1',
                        'service_id': 1,
                        'configs': [],
                        'basename': 'taxi_clownductor_stable',
                        'juggler_host': 'taxi_clownductor_stable',
                    },
                ],
            },
        ),
        case(
            data={
                'type': 'rtc',
                'service_name': 'clownductor',
                'project_name': 'taxi',
                'clown_service_id': 1,
                'clown_project_id': 150,
                'repo_meta': {'config_project': 'taxi'},
            },
            status=400,
            result={
                'code': 'BAD_PARAMS',
                'message': (
                    'provided project name is not as in clownductor: '
                    'provided("taxi") != clownductor("taxi-infra")'
                ),
            },
        ),
        case(
            data={
                'type': 'rtc',
                'service_name': 'clownductor',
                'project_name': 'taxi-infra',
                'clown_service_id': 3,
                'clown_project_id': 150,
                'repo_meta': {'config_project': 'taxi'},
            },
            status=400,
            result={
                'code': 'BAD_PARAMS',
                'message': (
                    'provided service name is not as in clownductor: '
                    'provided("clownductor") != clownductor("some")'
                ),
            },
        ),
        case(
            data={
                'type': 'rtc',
                'service_name': 'clownductor',
                'project_name': 'taxi-infra',
                'clown_service_id': 1,
                'clown_project_id': 2,
                'repo_meta': {'config_project': 'taxi'},
            },
            status=400,
            result={
                'code': 'BAD_PARAMS',
                'message': (
                    'provided project name is not as in clownductor: '
                    'provided("taxi-infra") != clownductor("taxi")'
                ),
            },
        ),
        case(
            data=builders.service(
                builders.branch(
                    builders.Config(for_upsert=True)
                    .with_events(
                        builders.Event(
                            1, 'some', for_upsert=True, ignore_nodata=None,
                        ),
                    )
                    .with_templates(
                        builders.LinkedTemplate(
                            builders.template(
                                'tmpl',
                                builders.Event(2, 'another', for_upsert=True),
                                for_upsert=True,
                            ),
                            ignore_nodata=True,
                        ),
                    )
                    .with_notifications(
                        builders.notification(
                            ['d1mbas'], 'default', 1, for_upsert=True,
                        ),
                    ),
                    for_upsert=True,
                ),
                for_upsert=True,
            ),
            status=200,
            result=builders.service(
                builders.branch(
                    builders.Config(for_upsert=True)
                    .with_events(
                        builders.Event(
                            1, 'some', for_upsert=True, ignore_nodata=False,
                        ),
                    )
                    .with_templates(
                        builders.LinkedTemplate(
                            builders.template('tmpl', for_upsert=True),
                            ignore_nodata=True,
                        ),
                    )
                    .with_notifications(
                        builders.notification(
                            ['d1mbas'], 'default', 1, for_upsert=True,
                        ),
                    ),
                    id_=0,
                    for_upsert=True,
                ),
            ),
            objects_in_queue=[
                {
                    'branch_id': 1,
                    'data': {
                        'events': [
                            {
                                'name': 'some',
                                'settings': {
                                    'times': [
                                        {
                                            'crit': {'count_threshold': 0},
                                            'warn': {'count_threshold': 0},
                                            'days': ['Mon', 'Sun'],
                                            'time': [0, 23],
                                        },
                                    ],
                                    'ignore_nodata': False,
                                },
                            },
                        ],
                        'branch_id': 1,
                        'repo_meta': {
                            'file_name': 'b1.yaml',
                            'file_path': 'b1.yaml',
                            'config_project': 'taxi',
                        },
                        'templates': [
                            {
                                'overrides': {'ignore_nodata': True},
                                'template': {
                                    'events': [],
                                    'name': 'tmpl',
                                    'namespace': 'default',
                                    'repo_meta': {
                                        'config_project': 'taxi',
                                        'file_name': 'pkgver.yaml',
                                        'file_path': 'templates/pkgver.yaml',
                                    },
                                },
                            },
                        ],
                        'notification_options': [
                            {
                                'logins': ['d1mbas'],
                                'name': 'default',
                                'repo_meta': {
                                    'config_project': '',
                                    'file_name': '',
                                },
                                'statuses': [{'from': 'OK', 'to': 'WARN'}],
                                'type': 'telegram',
                            },
                        ],
                    },
                    'status': 'pending',
                    'job_id': None,
                },
            ],
            id_='add config',
        ),
    ],
)
async def test_create(
        web_context,
        upsert_service,
        use_draft_api,
        data,
        status,
        result,
        objects_in_queue,
):
    assert (await upsert_service(data, status, use_draft_api)) == result
    if objects_in_queue is not None:
        rows = await web_context.pg.primary.fetch(
            'SELECT branch_id, data, status, job_id '
            'FROM alert_manager.configs_queue;',
        )

        def _convert(row):
            _data = dict(row)
            _data['data'] = json.loads(_data.pop('data'))
            return _data

        assert [_convert(x) for x in rows] == objects_in_queue


@pytest.mark.parametrize('use_draft_api', [True, False])
@pytest.mark.parametrize(
    'service_id, before_update, data, status, result, after_update',
    [
        pytest.param(
            2,
            {
                'id': 2,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'service_name': 'clownductor',
                'type': 'rtc',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
                'clown_service_id': 1,
                'clown_project_id': 150,
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'branches': [],
            },
            {
                'type': 'cgroup',
                'service_name': 'clownductor',
                'project_name': 'taxi-infra',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
            },
            200,
            {
                'id': 2,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'service_name': 'clownductor',
                'type': 'cgroup',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'branches': [],
            },
            {
                'id': 2,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'service_name': 'clownductor',
                'type': 'cgroup',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'branches': [],
            },
            id='change service type',
        ),
        pytest.param(
            1,
            {
                'id': 1,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'service_name': 'some',
                'type': 'rtc',
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'branches': [],
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
            },
            {
                'type': 'rtc',
                'service_name': 'some',
                'project_name': 'taxi-infra',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
            },
            200,
            {
                'id': 1,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'service_name': 'some',
                'type': 'rtc',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
                'clown_service_id': 4,
                'clown_project_id': 150,
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'branches': [],
            },
            {
                'id': 1,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'service_name': 'some',
                'type': 'rtc',
                'repo_meta': {
                    'config_project': 'taxi',
                    'file_name': 'b.yaml',
                    'file_path': 'b.yaml',
                },
                'clown_service_id': 4,
                'clown_project_id': 150,
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'branches': [],
            },
            id='set clowny ids by auto discover',
        ),
        pytest.param(
            3,
            builders.service(
                builders.branch(
                    builders.Config(
                        id_=1,
                        branch_id=1,
                        repo_meta_=builders.repo_meta(
                            'taxi', 'b.yaml', 'b.yaml',
                        ),
                    )
                    .with_events(builders.Event(1, 'oom', config_id=1))
                    .with_templates(
                        builders.LinkedTemplate(
                            builders.template(
                                'pkgver',
                                builders.Event(2, 'pkgver', template_id=1),
                                repo_meta_=builders.repo_meta(
                                    'taxi',
                                    'pkgver.yaml',
                                    'templates/pkgver.yaml',
                                ),
                            ),
                            ignore_nodata=False,
                        ).with_notifications(
                            builders.notification(
                                ['d1mbas'], 'telegram_option1', 1,
                            ),
                        ),
                    ),
                    id_=1,
                    names=['clowny-alerts'],
                    clown_branch_ids=[3],
                    namespace='taxi',
                    service_id=3,
                    repo_meta_=builders.repo_meta('taxi', 'b.yaml', 'b.yaml'),
                ),
                id_=3,
                service_name='clowny-alerts',
                project_name='taxi-infra',
                clown_service_id=2,
                clown_project_id=2,
                type_='rtc',
                repo_meta_=builders.repo_meta('taxi', 'b.yaml', 'b.yaml'),
            ),
            {
                'project_name': 'taxi-infra',
                'repo_meta': {'config_project': 'taxi'},
                'service_name': 'clowny-alerts',
                'type': 'rtc',
            },
            200,
            {
                'branches': [],
                'created_at': matching.datetime_string,
                'id': 3,
                'is_deleted': False,
                'project_name': 'taxi-infra',
                'repo_meta': {'config_project': 'taxi'},
                'service_name': 'clowny-alerts',
                'type': 'rtc',
                'updated_at': matching.datetime_string,
            },
            builders.service(
                builders.branch(
                    builders.Config(
                        id_=1,
                        branch_id=1,
                        repo_meta_=builders.repo_meta(
                            'taxi', 'b.yaml', 'b.yaml',
                        ),
                    )
                    .with_events(builders.Event(1, 'oom', config_id=1))
                    .with_templates(
                        builders.LinkedTemplate(
                            builders.template(
                                'pkgver',
                                builders.Event(2, 'pkgver', template_id=1),
                                repo_meta_=builders.repo_meta(
                                    'taxi',
                                    'pkgver.yaml',
                                    'templates/pkgver.yaml',
                                ),
                            ),
                            ignore_nodata=False,
                        ).with_notifications(
                            builders.notification(
                                ['d1mbas'], 'telegram_option1', 1,
                            ),
                        ),
                    ),
                    id_=1,
                    names=['clowny-alerts'],
                    clown_branch_ids=[3],
                    namespace='taxi',
                    service_id=3,
                    repo_meta_=builders.repo_meta('taxi', 'b.yaml', 'b.yaml'),
                ),
                id_=3,
                service_name='clowny-alerts',
                project_name='taxi-infra',
                type_='rtc',
                repo_meta_=builders.repo_meta('taxi', None, None),
            ),
            id='update service with events',
        ),
    ],
)
async def test_update(
        web_context,
        upsert_service,
        get_service,
        use_draft_api,
        service_id,
        before_update,
        data,
        status,
        result,
        after_update,
):
    assert (await get_service(service_id)) == before_update
    assert (await upsert_service(data, status, use_draft_api)) == result
    assert (await get_service(service_id)) == after_update


@pytest.mark.parametrize('use_draft_api', [True, False])
async def test_create_n_update(upsert_service, use_draft_api):
    create_data = {
        'type': 'rtc',
        'service_name': 'some',
        'project_name': 'taxi-infra',
        'repo_meta': {
            'config_project': 'taxi',
            'file_name': 'b.yaml',
            'file_path': 'b.yaml',
        },
    }
    assert (
        (await upsert_service(create_data, use_draft_api=use_draft_api))
        == {
            'id': 1,
            'project_name': 'taxi-infra',
            'service_name': 'some',
            'clown_project_id': 150,
            'clown_service_id': 4,
            'type': 'rtc',
            'repo_meta': {
                'config_project': 'taxi',
                'file_name': 'b.yaml',
                'file_path': 'b.yaml',
            },
            'is_deleted': False,
            'created_at': matching.datetime_string,
            'updated_at': matching.datetime_string,
            'branches': [],
        }
    )

    update_data = {
        'type': 'cgroup',
        'service_name': 'some',
        'project_name': 'taxi-infra',
        'repo_meta': {
            'config_project': 'taxi',
            'file_name': 'b.yaml',
            'file_path': 'b.yaml',
        },
    }
    assert (
        (await upsert_service(update_data, use_draft_api=use_draft_api))
        == {
            'id': 1,
            'project_name': 'taxi-infra',
            'service_name': 'some',
            'type': 'cgroup',
            'repo_meta': {
                'config_project': 'taxi',
                'file_name': 'b.yaml',
                'file_path': 'b.yaml',
            },
            'is_deleted': False,
            'created_at': matching.datetime_string,
            'updated_at': matching.datetime_string,
            'branches': [],
        }
    )
