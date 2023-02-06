from stall.model.asset import Asset


async def test_asset(tap):
    with tap.plan(4):
        asset = Asset({'title': 'привет'})
        tap.ok(asset, 'инстанцировано')
        tap.ok(await asset.save(), 'Сохранено')

        loaded = await Asset.load(asset.asset_id)
        tap.ok(loaded, f'загружено {asset.asset_id}')
        tap.eq(loaded.pure_python(), asset.pure_python(), 'значения')

async def test_asset_dataset(tap, dataset):
    with tap.plan(4):
        asset = await dataset.asset(title='Привет, медвед')
        tap.ok(asset, 'Основное средство создано')
        tap.eq(asset.title, 'Привет, медвед', 'название')

        asset = await dataset.asset()
        tap.ok(asset, 'Основное средство создано')
        tap.ok(asset.title, 'название по умолчанию есть')
