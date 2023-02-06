# pylint: disable=no-member
import datetime

import bson
import pytest

from chatterbox import stq_task

NOW = datetime.datetime(2019, 7, 25, 10)


@pytest.mark.parametrize(
    'task_id, tag, entity_type, tag_lifetime',
    [
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a1'),
            'test_tag',
            'user_phone_id',
            3600,
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a1'),
            'test_tag',
            'dbid_uuid',
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_not_enough_meta(
        cbox, task_id, tag, entity_type, tag_lifetime, mockserver,
):
    @mockserver.json_handler('/tags/v1/upload')
    def mock_tags(*args, **kwargs):
        return mockserver.make_response('', status=500)

    await stq_task.add_tag_to_tags_service(
        cbox.app, task_id, tag, entity_type, tag_lifetime,
    )

    assert not mock_tags.times_called


@pytest.mark.parametrize(
    'task_id, tag, entity_type, tags_service, tag_lifetime, expected_request',
    [
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a2'),
            'user_tag',
            'user_phone_id',
            'passenger-tags',
            3600,
            {
                'merge_policy': 'append',
                'entity_type': 'user_phone_id',
                'tags': [
                    {
                        'name': 'user_tag',
                        'match': {'id': 'phone_id', 'ttl': 3600},
                    },
                ],
            },
        ),
        (
            bson.ObjectId('5b2cae5cb2682a976914c2a2'),
            'driver_tag',
            'dbid_uuid',
            'tags',
            None,
            {
                'merge_policy': 'append',
                'entity_type': 'dbid_uuid',
                'tags': [
                    {
                        'name': 'driver_tag',
                        'match': {'id': 'db_id_driver_uuid'},
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_add_tag(
        cbox,
        task_id,
        tag,
        entity_type,
        tags_service,
        tag_lifetime,
        expected_request,
        mockserver,
):
    @mockserver.json_handler(f'/{tags_service}/v1/upload')
    async def _tags_upload(*args, **kwargs):
        data = args[0].json
        assert data == expected_request
        return {}

    await stq_task.add_tag_to_tags_service(
        cbox.app, task_id, tag, entity_type, tag_lifetime,
    )

    assert _tags_upload.times_called == 1
