import freezegun
import pytest

from qc_invites.generated.cron import run_cron


@freezegun.freeze_time('2021-07-20 16:00:00')
@pytest.mark.parametrize('ttl', [10, 90])
async def test_delete_old_invites(
        mockserver, load_json, pgsql, cron_client, ttl, taxi_config,
):
    """
    Проверка удаления старых инвайтов:
    должны удалиться первый и третий инвайты
    и сущности, которые им соответствуют;
    остальные инвайты должны остаться нетронутыми.
    """
    cursor = pgsql['qc_invites'].cursor()

    taxi_config.set_values(
        {'QC_INVITES_SERVICE_CONFIG': {'time_to_live_days': ttl}},
    )
    await cron_client.invalidate_caches()

    await run_cron.main(['qc_invites.crontasks.delete_old_invites', '-t', '0'])

    should_remain = load_json(f'should_remain_{ttl}.json')

    cursor.execute('SELECT id FROM invites.invites')
    remaining_invites = set(row[0] for row in cursor)
    assert remaining_invites == set(should_remain['invites'])

    cursor.execute(
        'SELECT invite_id, ARRAY_AGG(entity_id)'
        'FROM invites.entities GROUP BY invite_id',
    )
    invited_entities = dict(row for row in cursor)
    assert set(invited_entities.keys()) == set(
        should_remain['entities'].keys(),
    )
    for invite_id, entities in invited_entities.items():
        assert set(should_remain['entities'][invite_id]) == set(entities)
