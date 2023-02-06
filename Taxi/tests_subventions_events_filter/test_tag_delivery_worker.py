import pytest

from tests_subventions_events_filter import helpers

_TAG_DELIVERY_WORKER = 'tag-delivery-worker'


@pytest.fixture(autouse=True)
async def _periodic_task_test(taxi_subventions_events_filter):
    await taxi_subventions_events_filter.suspend_periodic_tasks(
        [_TAG_DELIVERY_WORKER],
    )


@pytest.mark.parametrize(
    'redis_state,expected_tags_changes,expected_redis_state',
    [
        pytest.param(
            # redis_state
            {'tag:superdriver:udid1': '2020-01-01T12:00:30+0000'},
            # expected_tags_changes
            {
                'added': [
                    ('udid1', 'superdriver', '2020-01-01T12:30:32+0000'),
                ],
                'deleted': [],
            },
            # expected_redis_state
            {
                'tag:superdriver:udid1': '2020-01-01T12:00:30+0000',
                'state:superdriver:udid1': (
                    '{'
                    '"state":"added","expires_at":"2020-01-01T12:30:32+00:00"'
                    '}'
                ),
            },
            id='add new tag',
        ),
        pytest.param(
            # redis_state
            {
                'tag:superdriver:udid1': '2020-01-01T11:58:30+0000',
                'state:superdriver:udid1': (
                    '{'
                    '"state":"added","expires_at":"2020-01-01T12:25:32+00:00"'
                    '}'
                ),
            },
            # expected_tags_changes
            {'added': [], 'deleted': [('udid1', 'superdriver')]},
            # expected_redis_state
            {},
            id='remove tag',
        ),
        pytest.param(
            # redis_state
            {'tag:superdriver:udid1': '2020-01-01T11:58:30+0000'},
            # expected_tags_changes
            {'added': [], 'deleted': [('udid1', 'superdriver')]},
            # expected_redis_state
            {},
            id='dont add new but expired tag',
        ),
        pytest.param(
            # redis_state
            {
                'tag:superdriver:udid1': '2020-01-01T12:30:30+0000',
                'state:superdriver:udid1': '{"state":"on_delete"}',
            },
            # expected_tags_changes
            {'added': [], 'deleted': [('udid1', 'superdriver')]},
            # expected_redis_state
            {},
            id='finish him',
        ),
        pytest.param(
            # redis_state
            {
                'tag:superdriver:udid1': '2020-01-01T12:00:30+0000',
                'state:superdriver:udid1': (
                    '{'
                    '"state":"added","expires_at":"2020-01-01T12:00:55+00:00"'
                    '}'
                ),
            },
            # expected_tags_changes
            {
                'added': [
                    ('udid1', 'superdriver', '2020-01-01T12:30:32+0000'),
                ],
                'deleted': [],
            },
            # expected_redis_state
            {
                'tag:superdriver:udid1': '2020-01-01T12:00:30+0000',
                'state:superdriver:udid1': (
                    '{'
                    '"state":"added","expires_at":"2020-01-01T12:30:32+00:00"'
                    '}'
                ),
            },
            id='update before expiration',
        ),
        pytest.param(
            # redis_state
            {
                'tag:superdriver:udid1': '2020-01-01T12:00:30+0000',
                'state:superdriver:udid1': '{"state":"added"}',
            },
            # expected_tags_changes
            {'added': [], 'deleted': [('udid1', 'superdriver')]},
            # expected_redis_state
            {},
            id='bad state',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_TAGGING_RULES={
        'default_tag_ttl_s': 60,
        'rules': [
            {'tag': 'superdriver'},
            {'tag': 'ultradriver', 'ttl_s': 180},
        ],
    },
    SUBVENTIONS_EVENTS_FILTER_SETTINGS={
        'enabled': False,
        'bulk_size': 100,
        'tag_delivery_worker': {
            'enabled': True,
            'update_tags_before_expired_in_s': 60,
            'tags_service_tag_ttl_s': 30 * 60,
            'tags_chunk_size': 500,
            'tag_ttl_jitter_percents': 0.0,
        },
    },
)
@pytest.mark.now('2020-01-01T12:00:32+0000')
async def test_tagger_worker(
        taxi_subventions_events_filter,
        mockserver,
        redis_store,
        redis_state,
        expected_tags_changes,
        expected_redis_state,
):
    tags_changes = {'added': [], 'deleted': []}

    @mockserver.json_handler('/tags/v2/upload')
    def _mock_v1_upload(request):
        body = request.json
        assert body['provider_id'] == 'subventions-events-filter'
        if 'append' in body:
            for tag_record in body['append']:
                assert tag_record['entity_type'] == 'udid'
                for tag in tag_record['tags']:
                    tags_changes['added'].append(
                        (tag['entity'], tag['name'], tag['until']),
                    )
        if 'remove' in body:
            for tag_record in body['remove']:
                assert tag_record['entity_type'] == 'udid'
                for tag in tag_record['tags']:
                    tags_changes['deleted'].append(
                        (tag['entity'], tag['name']),
                    )
        return {'status': 'ok'}

    helpers.set_redis_state(redis_store, redis_state)

    await taxi_subventions_events_filter.run_periodic_task(
        _TAG_DELIVERY_WORKER,
    )

    assert tags_changes == expected_tags_changes

    assert helpers.get_redis_state(redis_store) == expected_redis_state
