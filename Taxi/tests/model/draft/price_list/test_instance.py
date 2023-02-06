from stall.model.draft.price_list import DraftPriceList


async def test_price_list(tap, uuid):
    with tap.plan(4):
        draft = DraftPriceList({'title': f'Черновик прайса {uuid()}'})

        tap.ok(draft, 'Inited')
        tap.ok(not draft.price_list_id, 'No id')
        tap.ok(await draft.save(), 'Saved')
        tap.ok(draft.price_list_id, 'id assigned')


async def test_dataset(tap, dataset):
    with tap.plan(2):
        draft = await dataset.draft_price_list(title='lavka 43')

        tap.ok(draft, 'Created')
        tap.eq(draft.title, 'lavka 43', 'Correct title')
