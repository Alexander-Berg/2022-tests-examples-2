import argparse

from scripts.dev.turn_off_true_mark import main

async def test_turn_off_ok(tap, dataset):
    with tap.plan(11, 'тестим хеппи флоу'):
        ps = [await dataset.product(true_mark=True) for _ in range(3)]

        args = argparse.Namespace(
            apply=False,
            product_ids=[p.product_id for p in ps],
            external_ids=None,
            product_ids_file=None,
            external_ids_file=None,
        )

        await main(args)
        for p in ps:
            await p.reload()
            tap.ok(p.vars('imported.true_mark', False), 'не поменяли')

        args.apply = True
        await main(args)
        for p in ps:
            await p.reload()
            tap.ok(not p.vars('imported.true_mark', False), 'поменяли')

        for i, p in enumerate(ps):
            if i == 1:
                continue
            p.vars['imported']['true_mark'] = True
            p.vars['imported'] = p.vars['imported']
            await p.save()
            await p.reload()
            tap.ok(p.vars('imported.true_mark', False), 'поменяли назад')

        args.product_ids = None
        args.external_ids = [p.external_id for p in ps] + [ps[0].external_id]
        await main(args)
        for p in ps:
            await p.reload()
            tap.ok(not p.vars('imported.true_mark', False), 'поменяли')


async def test_turn_off_fail(tap, dataset, uuid):
    with tap.plan(1, 'тестим не хеппи флоу'):
        p = await dataset.product(true_mark=True)
        args = argparse.Namespace(
            apply=False,
            product_ids=[uuid(), uuid()],
            external_ids=None,
            product_ids_file=None,
            external_ids_file=None,
        )

        await main(args)

        await p.reload()
        tap.ok(p.vars('imported.true_mark'), 'ниче не поменялось')


async def test_turn_off_file(tap, dataset):
    with tap.plan(3, 'тестим хеппи флоу с файлом'):
        ps = [await dataset.product(true_mark=True) for _ in range(3)]

        with open('tests/scripts/dev/data/external_ids', 'w') as f:
            f.write('\n'.join([p.external_id for p in ps]) + '\n\n\n')

        args = argparse.Namespace(
            apply=True,
            product_ids=None,
            external_ids=None,
            product_ids_file=None,
            external_ids_file='tests/scripts/dev/data/external_ids',
        )

        await main(args)
        for p in ps:
            await p.reload()
            tap.ok(not p.vars('imported.true_mark', False), 'поменяли')
