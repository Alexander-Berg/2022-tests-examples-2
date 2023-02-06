from taxi.util import dates as dates_utils


async def test_ok(mock_unique_drivers, mock_tags, stq_runner, stq):
    park_id = 'park1'
    contractor_id = 'contractor1'
    park_contractor_id = f'{park_id}_{contractor_id}'
    udid = 'udid1'
    append_tags = [
        {'name': 'tag1', 'entity': 'udid', 'ttl': None, 'until': None},
        {'name': 'tag2', 'entity': 'udid', 'ttl': None, 'until': None},
        {'name': 'tag3', 'entity': 'udid', 'ttl': 1, 'until': None},
        {
            'name': 'tag4',
            'entity': 'udid',
            'ttl': None,
            'until': dates_utils.parse_timestring('2000-01-01T00:00:00'),
        },
    ]

    @mock_unique_drivers('/v1/driver/uniques/retrieve_by_profiles')
    async def _retrieve(request):
        assert request.json == {'profile_id_in_set': ['park1_contractor1']}
        return {
            'uniques': [
                {
                    'park_driver_profile_id': park_contractor_id,
                    'data': {'unique_driver_id': udid},
                },
            ],
        }

    @mock_tags('/v2/upload')
    async def _v2_upload(request):
        assert request.headers['X-Idempotency-Token'] == 'task_id'
        assert request.json == {
            'provider_id': 'selfemployed',
            'append': [
                {
                    'entity_type': 'udid',
                    'tags': [
                        {'name': 'tag1', 'entity': udid},
                        {'name': 'tag2', 'entity': udid},
                        {'name': 'tag3', 'entity': udid, 'ttl': 1},
                        {
                            'name': 'tag4',
                            'entity': 'udid1',
                            'until': '2000-01-01T00:00:00+0300',
                        },
                    ],
                },
            ],
        }
        return {}

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_tag_udid.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            park_id=park_id,
            contractor_id=contractor_id,
            append_tags=append_tags,
            remove_tags=[],
        ),
        reschedule_counter=0,
    )

    assert not stq.selfemployed_fns_tag_udid.has_calls


async def test_not_ready(mock_unique_drivers, stq_runner, stq):
    park_id = 'park1'
    contractor_id = 'contractor1'
    park_contractor_id = f'{park_id}_{contractor_id}'
    append_tags = [
        {'name': 'tag1', 'entity': 'udid', 'ttl': None, 'until': None},
        {'name': 'tag2', 'entity': 'udid', 'ttl': None, 'until': None},
    ]

    @mock_unique_drivers('/v1/driver/uniques/retrieve_by_profiles')
    async def _retrieve(request):
        assert request.json == {'profile_id_in_set': ['park1_contractor1']}
        return {
            'uniques': [
                {'park_driver_profile_id': park_contractor_id, 'data': None},
            ],
        }

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_tag_udid.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            park_id=park_id,
            contractor_id=contractor_id,
            append_tags=append_tags,
            remove_tags=[],
        ),
        reschedule_counter=99,
    )

    assert stq.selfemployed_fns_tag_udid.has_calls


async def test_not_ready_dropped(mock_unique_drivers, stq_runner, stq):
    park_id = 'park1'
    contractor_id = 'contractor1'
    park_contractor_id = f'{park_id}_{contractor_id}'
    append_tags = [
        {'name': 'tag1', 'entity': 'udid', 'ttl': None, 'until': None},
        {'name': 'tag2', 'entity': 'udid', 'ttl': None, 'until': None},
    ]

    @mock_unique_drivers('/v1/driver/uniques/retrieve_by_profiles')
    async def _retrieve(request):
        assert request.json == {'profile_id_in_set': ['park1_contractor1']}
        return {
            'uniques': [
                {'park_driver_profile_id': park_contractor_id, 'data': None},
            ],
        }

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_tag_udid.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            park_id=park_id,
            contractor_id=contractor_id,
            append_tags=append_tags,
            remove_tags=[],
        ),
        reschedule_counter=100,
    )

    assert not stq.selfemployed_fns_tag_udid.has_calls
