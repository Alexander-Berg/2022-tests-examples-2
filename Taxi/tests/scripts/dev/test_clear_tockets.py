import argparse
from scripts.dev.clear_tickets import main


async def test_remove(tap, dataset):
    with tap.plan(2, 'Удаляем поле'):
        user = await dataset.user(
            vars={
                'briefing_tickets':{},
                'about': {}
            }
        )
        args = argparse.Namespace(
            apply=True,
            field='briefing_tickets'
        )

        await main(args)

        await user.reload()
        tap.ok('briefing_tickets' not in user.vars,
               'удалили'
               )
        tap.ok('about' in user.vars,
               'другой параметр остался'
               )
