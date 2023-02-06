import datetime

import pytest

from testsuite.utils import http


@pytest.mark.config(
    SELFEMPLOYED_TAGGING=dict(
        ownpark_profile_created=dict(
            append=[
                dict(name='test1', entity='dbid', ttl=1),
                dict(name='test2', entity='dbid', until='2000-01-01T00:00:00'),
                dict(
                    name='udid',
                    entity='udid',
                    ttl=1,
                    until='2000-01-01T00:00:00',
                ),
            ],
        ),
        quasi_profile_created=dict(
            append=[dict(name='test3', entity='dbid_uuid')],
            remove=[
                dict(name='test2', entity='dbid'),
                dict(name='udid', entity='udid'),
            ],
        ),
    ),
)
async def test(mock_unique_drivers, mock_tags, stq_runner, stq):
    park_id = 'park1'
    contractor_id = 'contractor1'
    park_contractor_id = f'{park_id}_{contractor_id}'
    udid = 'udid1'
    tags = dict()

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
    async def _v2_upload(request: http.Request):
        assert request.headers['X-Idempotency-Token'] == 'task_id'
        assert request.json['provider_id'] == 'selfemployed'
        for appender in request.json.get('append', []):
            assert appender['entity_type'] in ['udid', 'park', 'dbid_uuid']
            for tag in appender['tags']:
                tags[(tag['name'], appender['entity_type'])] = (
                    tag.get('ttl'),
                    tag.get('until'),
                )
        for remover in request.json.get('remove', []):
            assert remover['entity_type'] in ['udid', 'park', 'dbid_uuid']
            for tag in remover['tags']:
                tags.pop((tag['name'], remover['entity_type']))
        return {}

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_tag_contractor.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            trigger_id='ownpark_profile_created',
            park_id=park_id,
            contractor_id=contractor_id,
        ),
        reschedule_counter=0,
    )

    assert tags == {
        ('test1', 'park'): (1, None),
        ('test2', 'park'): (None, '2000-01-01T00:00:00+0300'),
    }

    assert stq.selfemployed_fns_tag_udid.next_call() == {
        'args': [],
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'id': 'task_id|udid',
        'kwargs': {
            'append_tags': [
                {'name': 'udid', 'ttl': 1, 'until': {'$date': 946674000000}},
            ],
            'contractor_id': 'contractor1',
            'park_id': 'park1',
            'remove_tags': [],
        },
        'queue': 'selfemployed_fns_tag_udid',
    }

    # noinspection PyUnresolvedReferences
    await stq_runner.selfemployed_fns_tag_contractor.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            trigger_id='quasi_profile_created',
            park_id=park_id,
            contractor_id=contractor_id,
        ),
        reschedule_counter=0,
    )

    assert tags == {
        ('test1', 'park'): (1, None),
        ('test3', 'dbid_uuid'): (None, None),
    }

    assert stq.selfemployed_fns_tag_udid.next_call() == {
        'args': [],
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'id': 'task_id|udid',
        'kwargs': {
            'append_tags': [],
            'contractor_id': 'contractor1',
            'park_id': 'park1',
            'remove_tags': [{'name': 'udid'}],
        },
        'queue': 'selfemployed_fns_tag_udid',
    }
