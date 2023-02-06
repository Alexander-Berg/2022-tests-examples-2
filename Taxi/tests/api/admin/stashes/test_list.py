from easytap.pytest_plugin import PytestTap
import tests.dataset as dt


async def test_list(api, dataset: dt, tap: PytestTap, uuid):
    with tap.plan(9):
        group = uuid()
        group2 = uuid()

        stashes = [
            await dataset.stash(group=group),
            await dataset.stash(group=group, value={'key': 'value'}),
            await dataset.stash(group=group,
                                value={
                                    'code': 'IMPORT_DATA_IN_PAST',
                                    'row_number': 3
                                }),
        ]
        tap.ok(len(stashes) > 0, 'объекты созданы')

        another_stash = await dataset.stash(group=group2)
        tap.ok(another_stash, 'объекты в другой группе созданы')

        t = await api(role='admin')

        await t.post_ok('api_admin_stashes_list', json={'group': group})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stashes')
        t.json_has('stashes.2')
        t.json_hasnt('stashes.3')
        t.json_is('stashes.*.group', group,
                  'Все объекты принадлежат одной группе')


async def test_list_without_args(api, tap: PytestTap):
    with tap.plan(2):
        t = await api(role='admin')

        await t.post_ok('api_admin_stashes_list', json={})
        t.status_is(400, diag=True)
