import pytest

from testsuite.utils import matching

pytestmark = [pytest.mark.skip]  # pylint: disable=invalid-name


@pytest.mark.parametrize(
    'data, status, result',
    [
        (
            {
                'name': 'oom',
                'namespace': 'default',
                'events': [],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
            },
            200,
            {
                'id': 1,
                'name': 'oom',
                'namespace': 'default',
                'events': [],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'is_deleted': False,
            },
        ),
        (
            {
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {
                        'name': 'oom',
                        'ignore_nodata': True,
                        'times': [
                            {
                                'crit': {'count_threshold': 0},
                                'days': ['Mon', 'Sun'],
                                'time': [0, 23],
                                'warn': {'count_threshold': 0},
                            },
                        ],
                    },
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
            },
            200,
            {
                'id': 1,
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {
                        'id': 1,
                        'name': 'oom',
                        'template_id': 1,
                        'ignore_nodata': True,
                        'times': [
                            {
                                'crit': {'count_threshold': 0},
                                'days': ['Mon', 'Sun'],
                                'time': [0, 23],
                                'warn': {'count_threshold': 0},
                            },
                        ],
                        'created_at': matching.datetime_string,
                        'updated_at': matching.datetime_string,
                        'is_deleted': False,
                    },
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'is_deleted': False,
            },
        ),
        (
            {
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {'name': 'oom', 'ignore_nodata': True, 'times': []},
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'template oom has no time settings',
            },
        ),
        (
            {
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {
                        'name': 'oom',
                        'ignore_nodata': True,
                        'times': [
                            {
                                'crit': {'count_threshold': 0},
                                'days': ['Mon', 'Sun'],
                                'time': [0, 23],
                                'warn': {'count_threshold': 0},
                            },
                        ],
                        'flaps': {'stable_time': 100500, 'critical_time': 10},
                    },
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'stable time cannot be greater than critical time',
            },
        ),
    ],
)
async def test_create(upsert_template, data, status, result):
    assert (await upsert_template(data, status)) == result


@pytest.mark.parametrize(
    'tmpl_id, before_update, data, result, after_update',
    [
        pytest.param(
            1,
            {
                'id': 1,
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {
                        'id': 1,
                        'name': 'oom',
                        'ignore_nodata': True,
                        'template_id': 1,
                        'times': [
                            {
                                'days': ['Mon', 'Sun'],
                                'time': [0, 23],
                                'warn': {'count_threshold': 0},
                                'crit': {'count_threshold': 0},
                            },
                        ],
                        'created_at': matching.datetime_string,
                        'updated_at': matching.datetime_string,
                        'is_deleted': False,
                    },
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'is_deleted': False,
            },
            {
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {
                        'name': 'oom',
                        'ignore_nodata': True,
                        'times': [
                            {
                                'days': ['Mon', 'Sun'],
                                'time': [0, 23],
                                'warn': {'count_threshold': 0},
                                'crit': {'percent_threshold': 101},
                            },
                        ],
                    },
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
            },
            {
                'id': 1,
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {
                        'id': 1,
                        'template_id': 1,
                        'name': 'oom',
                        'ignore_nodata': True,
                        'times': [
                            {
                                'days': ['Mon', 'Sun'],
                                'time': [0, 23],
                                'warn': {'count_threshold': 0},
                                'crit': {'percent_threshold': 101},
                            },
                        ],
                        'created_at': matching.datetime_string,
                        'updated_at': matching.datetime_string,
                        'is_deleted': False,
                    },
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'is_deleted': False,
            },
            {
                'id': 1,
                'name': 'oom',
                'namespace': 'default',
                'events': [
                    {
                        'id': 1,
                        'template_id': 1,
                        'name': 'oom',
                        'ignore_nodata': True,
                        'times': [
                            {
                                'days': ['Mon', 'Sun'],
                                'time': [0, 23],
                                'warn': {'count_threshold': 0},
                                'crit': {'percent_threshold': 101},
                            },
                        ],
                        'created_at': matching.datetime_string,
                        'updated_at': matching.datetime_string,
                        'is_deleted': False,
                    },
                ],
                'repo_meta': {
                    'config_project': 'default',
                    'file_name': 'oom.yaml',
                    'file_path': 'templates/oom.yaml',
                },
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'is_deleted': False,
            },
            id='change times',
        ),
    ],
)
async def test_update(
        upsert_template,
        get_template,
        tmpl_id,
        before_update,
        data,
        result,
        after_update,
):
    assert (await get_template(tmpl_id)) == before_update
    assert (await upsert_template(data)) == result
    assert (await get_template(tmpl_id)) == after_update


async def test_create_n_update(upsert_template):
    create_data = {
        'name': 'oom',
        'namespace': 'default',
        'events': [
            {
                'name': 'oom',
                'ignore_nodata': True,
                'times': [
                    {
                        'crit': {'count_threshold': 0},
                        'days': ['Mon', 'Sun'],
                        'time': [0, 23],
                        'warn': {'count_threshold': 0},
                    },
                ],
            },
        ],
        'repo_meta': {
            'config_project': 'default',
            'file_name': 'oom.yaml',
            'file_path': 'templates/oom.yaml',
        },
    }
    assert (await upsert_template(create_data)) == {
        'id': 1,
        'name': 'oom',
        'namespace': 'default',
        'events': [
            {
                'id': 1,
                'name': 'oom',
                'template_id': 1,
                'ignore_nodata': True,
                'times': [
                    {
                        'crit': {'count_threshold': 0},
                        'days': ['Mon', 'Sun'],
                        'time': [0, 23],
                        'warn': {'count_threshold': 0},
                    },
                ],
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'is_deleted': False,
            },
        ],
        'repo_meta': {
            'config_project': 'default',
            'file_name': 'oom.yaml',
            'file_path': 'templates/oom.yaml',
        },
        'created_at': matching.datetime_string,
        'updated_at': matching.datetime_string,
        'is_deleted': False,
    }

    update_data = {
        'name': 'oom',
        'namespace': 'default',
        'events': [
            {
                'name': 'oom',
                'ignore_nodata': False,
                'times': [
                    {
                        'days': ['Mon', 'Sun'],
                        'time': [0, 23],
                        'warn': {'count_threshold': 0},
                        'crit': {'count_threshold': 101},
                    },
                ],
            },
        ],
        'repo_meta': {
            'config_project': 'default',
            'file_name': 'oom.yaml',
            'file_path': 'templates/oom.yaml',
        },
    }
    assert (await upsert_template(update_data)) == {
        'id': 1,
        'name': 'oom',
        'namespace': 'default',
        'events': [
            {
                'id': 1,
                'template_id': 1,
                'name': 'oom',
                'ignore_nodata': False,
                'times': [
                    {
                        'days': ['Mon', 'Sun'],
                        'time': [0, 23],
                        'warn': {'count_threshold': 0},
                        'crit': {'count_threshold': 101},
                    },
                ],
                'created_at': matching.datetime_string,
                'updated_at': matching.datetime_string,
                'is_deleted': False,
            },
        ],
        'repo_meta': {
            'config_project': 'default',
            'file_name': 'oom.yaml',
            'file_path': 'templates/oom.yaml',
        },
        'created_at': matching.datetime_string,
        'updated_at': matching.datetime_string,
        'is_deleted': False,
    }
