import pytest

from chatterbox import constants
from chatterbox import settings
from chatterbox.generated.service.config import plugin as config
from test_chatterbox import plugins as conftest


TEST_BLOCKLIST_MECHANICS_MAPPING = (
    config.Config.CHATTERBOX_BLOCKLIST_MECHANICS_MAPPING
)
TEST_BLOCKLIST_MECHANICS_MAPPING['additional_meta_fields'] = [
    'task_id',
    'test_field',
]


@pytest.mark.parametrize(
    ('comment', 'expected_comment', 'task_data', 'expected_block_args'),
    (
        (
            '{{block:car_number:test_test.tanker_key:test1_test-test'
            '::license::car_number::park_id:}}',
            '',
            {
                'task_id': '1q1',
                'car_number': 't010es02',
                'test_field': 'test1',
            },
            {
                'block': {
                    'predicate_id': '11111111-1111-1111-1111-111111111111',
                    'kwargs': {'car_number': 't010es02'},
                    'reason': {'key': 'test_test.tanker_key'},
                    'comment': settings.SUPCHAT_URL + '/chat/1q1',
                    'mechanics': 'test1_test-test',
                    'meta': {'task_id': '1q1', 'test_field': 'test1'},
                },
                'identity': {'name': 'chatterbox', 'type': 'service'},
            },
        ),
        (
            '{{block:car_number+park_id:test_test.tanker_key:test1_test-test'
            '::license::car_number::park_id:}}',
            '',
            {
                'task_id': '1q1',
                'car_number': 't010es02',
                'park_db_id': 'test_park_id',
                'test_field': 'test1',
            },
            {
                'block': {
                    'predicate_id': '22222222-2222-2222-2222-222222222222',
                    'kwargs': {
                        'car_number': 't010es02',
                        'park_id': 'test_park_id',
                    },
                    'reason': {'key': 'test_test.tanker_key'},
                    'comment': settings.SUPCHAT_URL + '/chat/1q1',
                    'mechanics': 'test1_test-test',
                    'meta': {'task_id': '1q1', 'test_field': 'test1'},
                },
                'identity': {'name': 'chatterbox', 'type': 'service'},
            },
        ),
        (
            '{{block:driver_license:test_test.tanker_key:test1_test-test'
            '::license::car_number::park_id:}}',
            '',
            {'task_id': '1q1', 'driver_license_pd_id': 'test_license'},
            {
                'block': {
                    'predicate_id': '33333333-3333-3333-3333-333333333333',
                    'kwargs': {'license_id': 'test_license'},
                    'reason': {'key': 'test_test.tanker_key'},
                    'comment': settings.SUPCHAT_URL + '/chat/1q1',
                    'mechanics': 'test1_test-test',
                    'meta': {'task_id': '1q1', 'test_field': ''},
                },
                'identity': {'name': 'chatterbox', 'type': 'service'},
            },
        ),
        (
            '{{block:driver_license+park_id:tanker_key:mechanic'
            '::license::car_number::park_id:}}',
            '',
            {
                'task_id': '1q1',
                'driver_license_pd_id': 'test_license',
                'park_db_id': 'test_park_id',
            },
            {
                'block': {
                    'predicate_id': '44444444-4444-4444-4444-444444444444',
                    'kwargs': {
                        'license_id': 'test_license',
                        'park_id': 'test_park_id',
                    },
                    'reason': {'key': 'tanker_key'},
                    'comment': settings.SUPCHAT_URL + '/chat/1q1',
                    'mechanics': 'mechanic',
                    'meta': {'task_id': '1q1', 'test_field': ''},
                },
                'identity': {'name': 'chatterbox', 'type': 'service'},
            },
        ),
        (
            '{{block:driver_license+park_id:tanker_key:mechanic'
            ':1440:license::car_number::park_id:}}',
            '',
            {
                'task_id': '1q1',
                'driver_license_pd_id': 'test_license',
                'park_db_id': 'test_park_id',
            },
            {
                'block': {
                    'predicate_id': '44444444-4444-4444-4444-444444444444',
                    'kwargs': {
                        'license_id': 'test_license',
                        'park_id': 'test_park_id',
                    },
                    'reason': {'key': 'tanker_key'},
                    'comment': settings.SUPCHAT_URL + '/chat/1q1',
                    'mechanics': 'mechanic',
                    'expires': '2021-08-01T21:00:00Z',
                    'meta': {'task_id': '1q1', 'test_field': ''},
                },
                'identity': {'name': 'chatterbox', 'type': 'service'},
            },
        ),
        (
            '{{block:driver_license+park_id:tanker_key:mechanic'
            ':1440:license:not_ticket_license:car_number::'
            'park_id:not_ticket_park_id}}',
            '',
            {
                'task_id': 'license_ticket',
                'driver_license_pd_id': 'test_license',
                'park_db_id': 'test_park_id',
            },
            {
                'block': {
                    'predicate_id': '44444444-4444-4444-4444-444444444444',
                    'kwargs': {
                        'license_id': 'not_ticket_license_pd_id',
                        'park_id': 'not_ticket_park_id',
                    },
                    'reason': {'key': 'tanker_key'},
                    'comment': settings.SUPCHAT_URL + '/chat/license_ticket',
                    'mechanics': 'mechanic',
                    'expires': '2021-08-01T21:00:00Z',
                    'meta': {'task_id': 'license_ticket', 'test_field': ''},
                },
                'identity': {'name': 'chatterbox', 'type': 'service'},
            },
        ),
        (
            '{{block:car_number:tanker_key:mechanic'
            '::license::car_number:not_ticker_car_number:park_id:}}',
            '',
            {'task_id': '1q1', 'car_number': 't010es02'},
            {
                'block': {
                    'predicate_id': '11111111-1111-1111-1111-111111111111',
                    'kwargs': {'car_number': 'not_ticker_car_number'},
                    'reason': {'key': 'tanker_key'},
                    'comment': settings.SUPCHAT_URL + '/chat/1q1',
                    'mechanics': 'mechanic',
                    'meta': {'task_id': '1q1', 'test_field': ''},
                },
                'identity': {'name': 'chatterbox', 'type': 'service'},
            },
        ),
    ),
)
@pytest.mark.now('2021-08-01T00:00:00+0300')
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'chatterbox', 'dst': 'personal'},
        {'src': 'chatterbox', 'dst': 'blocklist'},
    ],
    CHATTERBOX_BLOCKLIST_MECHANICS_MAPPING=TEST_BLOCKLIST_MECHANICS_MAPPING,
)
async def test_block_driver(
        cbox: conftest.CboxWrap,
        mock_blocklist,
        mock_block_personal,
        auth_data: dict,
        comment: str,
        expected_comment: str,
        task_data: dict,
        expected_block_args: dict,
):
    comment_processor = cbox.app.comment_processor
    new_comment, processing_info = await comment_processor.process(
        comment, task_data, auth_data, constants.DEFAULT_STARTRACK_PROFILE,
    )

    assert mock_blocklist.has_calls
    assert mock_blocklist.times_called == 1

    _request_blocklist = mock_blocklist.next_call()['request']
    assert _request_blocklist.path == '/internal/blocklist/v1/add'
    assert _request_blocklist.content_type == 'application/json'
    assert _request_blocklist.headers.get('X-Idempotency-Token') is not None

    if task_data['task_id'] == 'license_ticket':
        assert mock_block_personal.has_calls
        assert mock_block_personal.times_called == 1
        _request_personal = mock_block_personal.next_call()['request']
        assert _request_personal.path == '/personal/v1/driver_licenses/find'

    assert _request_blocklist.json == expected_block_args
    assert new_comment == expected_comment
    assert processing_info.operations_log == ['Blocking driver processed']
    assert processing_info.succeed_operations == {'block_driver'}
