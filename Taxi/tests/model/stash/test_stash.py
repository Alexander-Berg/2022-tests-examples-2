from easytap.pytest_plugin import PytestTap
from stall.model.stash import Stash
import tests.dataset as dt


def test_instance(tap, uuid):
    with tap.plan(2):
        s = Stash(
            {
                'name': uuid(),
                'value': {'a': 1, 'b': 2},
            }
        )
        tap.ok(s, 'Stash')

        s = Stash({})
        tap.ok(s, 'Stash too')


async def test_dataset(tap, dataset):
    with tap.plan(1):
        s = await dataset.stash()
        tap.ok(s.stash_id, 'Stash created')


async def test_save(tap, uuid):
    with tap.plan(4):
        data = {
            'name': uuid(),
            'value': {'a': 1, 'b': 2},
        }
        s = Stash(data)

        await s.save()

        tap.ok(s.stash_id, 'Stash saved')
        tap.eq_ok(s.name, data['name'], 'name')
        tap.eq_ok(s.value, data['value'], 'value')
        tap.eq_ok(s.revision, 1, 'revision')


async def test_drop(tap):
    with tap:
        s = Stash({})
        await s.save()

        tap.eq_ok(s.revision, 1, 'Initial Revision')

        try:
            async with s:
                raise ValueError
        except ValueError:
            pass

        tap.eq_ok(s.revision, 2, 'Revision incremented on error')

        async with s:
            pass

        tap.is_ok(
            await Stash.load(s.stash_id), None, 'Stash dropped on success',
        )

async def test_save_with_group(tap: PytestTap, dataset: dt, uuid):
    with tap.plan(2):
        group = uuid()
        s = await dataset.stash(group=group)

        tap.ok(s.stash_id, 'Стеш сохранён')
        tap.eq_ok(s.group, group, 'У стеша задана группа')

