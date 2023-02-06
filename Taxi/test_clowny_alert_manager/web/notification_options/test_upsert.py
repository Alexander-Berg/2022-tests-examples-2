import pytest

from testsuite.utils import matching


def _no(**kwargs):
    return {
        'name': 'group',
        'logins': ['d1mbas'],
        'statuses': [{'from': 'OK', 'to': 'WARN'}],
        'type': 'telegram',
        'repo_meta': {
            'file_path': '/some.yaml',
            'file_name': 'some.yaml',
            'config_project': 'taxi',
        },
        **kwargs,
    }


@pytest.mark.parametrize(
    'data, status, result',
    [
        (
            _no(),
            200,
            _no(
                id=1,
                is_deleted=False,
                created_at=matching.datetime_string,
                updated_at=matching.datetime_string,
            ),
        ),
        (
            _no(statuses=[]),
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'empty statuses list is not allowed',
            },
        ),
        (
            _no(logins=[]),
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'empty logins list is not allowed',
            },
        ),
        (
            _no(
                statuses=[
                    {'from': 'OK', 'to': 'WARN'},
                    {'from': 'OK', 'to': 'WARN'},
                ],
            ),
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'status {\'from\': \'OK\', \'to\': \'WARN\'} '
                    'appears more then once'
                ),
            },
        ),
        (
            _no(statuses=[{'from': 'OK', 'to': 'OK'}]),
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'meaningless state (from == to == OK)',
            },
        ),
    ],
)
async def test_create(upsert_notification_option, data, status, result):
    assert (await upsert_notification_option(data, status)) == result
