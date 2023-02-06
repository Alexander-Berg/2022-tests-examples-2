import pytest

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.parametrize(
    (
        'comment',
        'expected_comment',
        'task_data',
        'value',
        'robot_auth',
        'expected_url',
        'expected_query',
        'succeed_operations',
        'operations_log',
    ),
    (
        (
            'Hello! Activity amnesty done! {{activity_amnesty:10}}',
            'Hello! Activity amnesty done! ',
            None,
            10,
            False,
            'admin/driver-metrics/v1/service/activity_value',
            {
                'mode': 'additive',
                'reason': '1',
                'udid': 'unique_driver_id',
                'value': 10,
            },
            {'activity_amnesty'},
            ['Activity amnesty processed'],
        ),
        (
            'Hello! Activity amnesty done! {{activity_amnesty:-5}}',
            'Hello! Activity amnesty done! ',
            None,
            -5,
            False,
            'admin/driver-metrics/v1/service/activity_value',
            {
                'mode': 'additive',
                'reason': '1',
                'udid': 'unique_driver_id',
                'value': -5,
            },
            {'activity_amnesty'},
            ['Activity amnesty processed'],
        ),
        (
            'Hello! Activity amnesty done! {{activity_amnesty:1}}',
            'Hello! Activity amnesty done! ',
            {'task_id': '1', 'unique_driver_id': 'unique_driver_id'},
            1,
            True,
            'admin/driver-metrics/v1/service/activity_value',
            {'mode': 'additive', 'udid': 'unique_driver_id', 'value': 1},
            {'activity_amnesty'},
            ['Activity amnesty processed'],
        ),
        (
            'Hello! Complete score amnesty! {{complete_score_amnesty:10}}',
            'Hello! Complete score amnesty! ',
            None,
            10,
            False,
            '/admin/driver-metrics/'
            'v1/service/driver/complete_scores_value/correct_bulk/',
            {
                'corrections': [
                    {'unique_driver_id': 'unique_driver_id', 'value': 10},
                ],
                'mode': 'additive',
                'reason': '1',
            },
            {'complete_score_amnesty'},
            ['Complete score amnesty processed'],
        ),
        (
            'Hello! Complete score amnesty! {{complete_score_amnesty:-5}}',
            'Hello! Complete score amnesty! ',
            None,
            -5,
            False,
            '/admin/driver-metrics/'
            'v1/service/driver/complete_scores_value/correct_bulk/',
            {
                'corrections': [
                    {'unique_driver_id': 'unique_driver_id', 'value': -5},
                ],
                'mode': 'additive',
                'reason': '1',
            },
            {'complete_score_amnesty'},
            ['Complete score amnesty processed'],
        ),
        (
            'Hello! Complete score amnesty! {{complete_score_amnesty:1}}',
            'Hello! Complete score amnesty! ',
            {'task_id': '1', 'unique_driver_id': 'unique_driver_id'},
            1,
            True,
            '/admin/driver-metrics/'
            'v1/service/driver/complete_scores_value/correct_bulk/',
            {
                'corrections': [
                    {'unique_driver_id': 'unique_driver_id', 'value': 1},
                ],
                'mode': 'additive',
            },
            {'complete_score_amnesty'},
            ['Complete score amnesty processed'],
        ),
    ),
)
async def test_amnesty(
        cbox: conftest.CboxWrap,
        patch_aiohttp_session,
        response_mock,
        auth_data: dict,
        comment: str,
        expected_comment: str,
        task_data: dict,
        value: int,
        robot_auth: bool,
        expected_url,
        expected_query,
        succeed_operations,
        operations_log,
):
    @patch_aiohttp_session(cbox.settings.TARIFF_EDITOR_URL, 'POST')
    def _patch_admin_request(method, url, **kwargs):
        assert method == 'post'
        assert expected_url in url

        data = kwargs['json']
        data.pop('idempotency_token', None)
        assert data == expected_query

        if robot_auth:
            assert not kwargs['headers'].get('Cookie')
            assert (
                kwargs['headers']['Authorization']
                == 'OAuth api_admin_py3_oauth_token'
            )
        else:
            assert kwargs['headers']['Cookie']
            assert not kwargs['headers'].get('Authorization')

        return response_mock(json={'text': ''})

    @patch_aiohttp_session(cbox.settings.TARIFF_EDITOR_URL, 'GET')
    def _patch_admin_me_request(method, url, **kwargs):
        assert method == 'get'
        assert '/me' in url
        return response_mock(json={'csrf_token': '213'})

    comment_processor = cbox.app.comment_processor
    task_data = task_data or {
        'task_id': '1',
        'unique_driver_id': 'unique_driver_id',
        'order_id': '1',
    }

    if robot_auth:
        auth_data = {'token': 'api_admin_py3_oauth_token', 'cookies': None}

    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )
    assert new_comment == expected_comment
    assert processing_info.succeed_operations == succeed_operations
    assert processing_info.operations_log == operations_log
