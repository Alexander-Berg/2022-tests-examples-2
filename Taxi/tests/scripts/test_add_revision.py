import argparse
from scripts.dev.add_revision import main


async def test_disable_user(tap, dataset):
    with tap.plan(6, 'Проставляем ревизии'):

        order = await dataset.order(
            status='processing',
            estatus='waiting',
            type='sale_stowage',
        )

        suggest_without_revision = await dataset.suggest(
            order,
            vars={}
        )
        suggest_without_revision_in_put = await dataset.suggest(
            order,
            vars={}
        )
        suggest_with_revision = await dataset.suggest(
            order,
            vars={
                'revision': -1,
            }
        )

        order.vars['put'] = {
            suggest_without_revision_in_put.suggest_id: True,
            suggest_with_revision.suggest_id: True,
        }
        await order.save()

        await order.reload()
        tap.ok(suggest_without_revision_in_put.suggest_id in order.vars['put'],
               'suggest_without_revision_in_put в путе ордера'
               )
        tap.ok(suggest_with_revision.suggest_id in order.vars['put'],
               'suggest_with_revision в путе ордера'
               )

        await main(
            args=argparse.Namespace(
                order=order.order_id,
                apply=True,
                force=False,
            )
        )

        await suggest_without_revision.reload()
        tap.ne(suggest_without_revision.vars.get('revision', -1),
               suggest_without_revision.revision,
               'в suggest_without_revision проросло'
               )
        await suggest_without_revision_in_put.reload()
        tap.eq(suggest_without_revision_in_put.vars.get('revision', -1),
               suggest_without_revision_in_put.revision,
               'в suggest_without_revision_in_put не проросло'
               )

        await suggest_with_revision.reload()
        tap.eq(suggest_with_revision.vars['revision'],
               -1,
               'в suggest_with_revision не изменилась'
               )

        await main(
            args=argparse.Namespace(
                order=order.order_id,
                apply=True,
                force=True,
            )
        )

        await suggest_with_revision.reload()
        tap.eq(suggest_with_revision.vars['revision'],
               suggest_with_revision.revision,
               'в suggest_with_revision с force изменилась'
               )
