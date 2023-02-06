import pytest


@pytest.fixture(autouse=True)
def _sync_with_core_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_place_groups_replica/sync_with_core',
        config_name='eats_place_groups_replica_sync_with_core',
        args=[
            {'name': 'place_id', 'type': 'string', 'value': 'place_id1'},
            {'name': 'brand_id', 'type': 'string', 'value': 'brand_id1'},
            {
                'name': 'place_group_id',
                'type': 'string',
                'value': 'place_group_id1',
            },
            {'name': 'type', 'type': 'string', 'value': 'nomenclature'},
        ],
        value={'is_active_sync_with_core': True},
    )
    client_experiments3.add_record(
        consumer='eats_place_groups_replica/sync_with_core',
        config_name='eats_place_groups_replica_sync_with_core',
        args=[
            {'name': 'place_id', 'type': 'string', 'value': 'place_id2'},
            {'name': 'brand_id', 'type': 'string', 'value': 'brand_id2'},
            {
                'name': 'place_group_id',
                'type': 'string',
                'value': 'place_group_id2',
            },
            {'name': 'type', 'type': 'string', 'value': 'nomenclature'},
        ],
        value={'is_active_sync_with_core': False},
    )


@pytest.mark.parametrize(
    'place_id, is_active, using_fallback',
    [
        ('place_id1', True, False),
        ('place_id2', False, False),
        ('place_id3', True, True),
    ],
)
@pytest.mark.parametrize('fallback_value', [True, False])
@pytest.mark.pgsql('eats_place_groups_replica', files=['places.sql'])
async def test_sync_with_core_config_checker(
        web_context, place_id, is_active, using_fallback, fallback_value,
):
    web_context.config.EATS_PLACE_GROUPS_REPLICA_SETTINGS[
        'is_active_sync_with_core'
    ] = fallback_value
    checker = web_context.sync_with_core_config_checker
    assert await checker.is_active_sync_with_core(
        place_id, 'nomenclature',
    ) == (fallback_value if using_fallback else is_active)
