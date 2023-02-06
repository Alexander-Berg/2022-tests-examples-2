import pytest

from crm_admin import entity
from crm_admin.storage import resolution_adapters


@pytest.mark.parametrize(
    'experiment_id, group_name, resolution, success',
    [
        ('exp1', 'gr1', True, True),
        ('exp2', 'gr2', False, True),
        ('exp3', 'gr3', False, True),
        ('exp4', 'gr4', True, True),
        ('exp5', 'gr5', None, False),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_resolution.sql'])
async def test_resolution_fetch(
        web_context, experiment_id, group_name, resolution, success,
):
    resolution_storage = resolution_adapters.DbResolution(web_context)
    if success:
        res = await resolution_storage.fetch(experiment_id, group_name)
        assert res.resolution == resolution
    else:
        with pytest.raises(entity.EntityNotFound):
            await resolution_storage.fetch(experiment_id, group_name)


@pytest.mark.pgsql('crm_admin', files=['init_resolution.sql'])
async def test_save_pushed_resolutions(web_context):
    groups = [
        {'experiment_id': 'e1', 'group_name': 'a', 'resolution': 'approved'},
        {'experiment_id': 'e1', 'group_name': 'a', 'resolution': 'rejected'},
        {'experiment_id': 'e2', 'group_name': 'b', 'resolution': 'approved'},
    ]

    db_resolution = resolution_adapters.DbResolution(web_context)
    await db_resolution.save_pushed_resolutions(groups)

    assert await db_resolution.fetch_pushed_resolution('e1', 'a') == 'rejected'
    assert await db_resolution.fetch_pushed_resolution('e2', 'b') == 'approved'


@pytest.mark.parametrize(
    'experiment_id, group_name, resolution',
    [('ticket-1', 'group-1', 'approved'), ('ticket-1', 'group-100', None)],
)
@pytest.mark.pgsql('crm_admin', files=['init_resolution.sql'])
async def test_fetch_pushed_resolution(
        web_context, experiment_id, group_name, resolution,
):
    db_resolution = resolution_adapters.DbResolution(web_context)
    if resolution:
        saved_resolution = await db_resolution.fetch_pushed_resolution(
            experiment_id, group_name,
        )
        assert saved_resolution == resolution
    else:
        with pytest.raises(entity.EntityNotFound):
            await db_resolution.fetch_pushed_resolution(
                experiment_id, group_name,
            )
