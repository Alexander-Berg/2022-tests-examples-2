import pytest

from stq_agent_py3.crontasks.helpers import downtimes


@pytest.mark.filldb(stq_config='downtime')
@pytest.mark.now('2019-01-01T21:00:00Z')
async def test_perform_downtime(
        cron_context, db, mock_conductor, mock_conductor_url, load_json,
):
    mock_conductor(
        hosts_info=[
            {
                'hostname': 'sas-host',
                'datacenter': 'sas',
                'group': 'taxi_prestable_stq',
            },
            {'hostname': 'vla-host', 'datacenter': 'vla', 'group': 'taxi_stq'},
        ],
    )
    alive_by_queue = {
        'queue_with_downtime_no_auto': {'vla-host', 'sas-host'},
        'queue_with_downtime_auto': {'vla-host', 'sas-host'},
        'queue_with_downtime_to_disable': {'vla-host'},
    }
    await downtimes.perform(cron_context, alive_by_queue)
    docs = await db.stq_config.find(
        {
            '_id': {
                '$in': [
                    'queue_with_downtime_no_auto',
                    'queue_with_downtime_auto',
                    'queue_with_downtime_to_disable',
                ],
            },
        },
    ).to_list(None)
    expected = load_json('perform_dt_expected_settings.json')
    for doc in docs:
        for field, expected_value in expected[doc['_id']].items():
            assert (
                expected_value == doc[field]
            ), 'values of {} differ for {}'.format(field, doc['_id'])


@pytest.mark.now('2019-01-01T21:00:00Z')
@pytest.mark.filldb(stq_config='downtime')
async def test_restore_after_downtime(cron_context, db, load_json):
    await downtimes.restore_after(cron_context)
    docs = await db.stq_config.find(
        {'_id': {'$regex': 'queue_after_downtime'}},
    ).to_list(None)
    expected = load_json('restore_after_dt_expected_settings.json')
    for doc in docs:
        doc_id = doc['_id']
        for field, expected_value in expected[doc_id].items():
            assert (
                expected_value == doc[field]
            ), f'values of {field} are different for {doc_id}'
