import argparse

from stall.model.product_group import ProductGroup
from scripts.dev.check_removed_groups import main


async def test_simple(tap, dataset):
    with tap.plan(11, 'Удаление категорий со статусом removed'):
        group1 = await dataset.product_group(
            name="Для удаления 1",
            status='removed',
        )
        group2 = await dataset.product_group(
            name="Для удаления 2",
            status='removed',
            parent_group_id=group1.group_id,
        )
        group3 = await dataset.product_group(
            name="Для удаления 3",
            status='removed',
        )
        group4 = await dataset.product_group(
            name="Обычная категория",
        )
        tap.ok(group1, 'Создана категория 1 со статусом removed')
        tap.ok(group2, 'Создана категория 2 со статусом removed')
        tap.ok(group3, 'Создана категория 3 со статусом removed')
        tap.ok(group4, 'Создана категория')

        product1 = await dataset.product()
        product2 = await dataset.product(groups=[
            group4.group_id,
        ])
        tap.ok(product1, 'Создан продукт')
        tap.ok(product2, 'Создан продукт 4ой категории')

        # Выполняем скрипт
        args = argparse.Namespace(apply=True)
        tap.ok(await main(args), 'Скрипт сработал')

        group1 = await ProductGroup.load(group1.group_id)
        tap.eq(group1, None, 'Категория 1 удалена')
        group2 = await ProductGroup.load(group2.group_id)
        tap.eq(group2, None, 'Категория 2 удалена')
        group3 = await ProductGroup.load(group3.group_id)
        tap.eq(group3, None, 'Категория 3 удалена')
        group4 = await ProductGroup.load(group4.group_id)
        tap.ok(group4, 'Категория не удалена')

async def test_non_removable(tap, dataset):
    with tap.plan(7, 'Удаление категорий со статусом removed'):
        group1 = await dataset.product_group(
            name="Сырки",
            status='removed',
        )
        group2 = await dataset.product_group(
            name="Онигири",
            status='removed',
        )
        tap.ok(group1, 'Создана категория 1 со статусом removed')
        tap.ok(group2, 'Создана категория 2 со статусом removed')

        product1 = await dataset.product()
        product2 = await dataset.product(groups=[
            group2.group_id,
        ])
        tap.ok(product1, 'Создан продукт')
        tap.ok(product2, 'Создан продукт 2ой категории')

        # Выполняем скрипт
        args = argparse.Namespace(apply=True)
        tap.ok(await main(args), 'Скрипт сработал')

        group1 = await ProductGroup.load(group1.group_id)
        tap.eq(group1, None, 'Категория 1 удалена')
        group2 = await ProductGroup.load(group2.group_id)
        tap.ok(group2, 'Категория 2 не удалена')

async def test_child_non_removable(tap, dataset):
    with tap.plan(7, 'Удаление подкатегорий с продуктами'):
        group1 = await dataset.product_group(
            name="Сырки",
            status='removed',
        )
        group2 = await dataset.product_group(
            name="Онигири",
            status='removed',
            parent_group_id=group1.group_id,
        )
        tap.ok(group1, 'Создана категория 1 со статусом removed')
        tap.ok(group2, 'Создана категория 2 со статусом removed')

        product1 = await dataset.product()
        product2 = await dataset.product(groups=[
            group2.group_id,
        ])
        tap.ok(product1, 'Создан продукт')
        tap.ok(product2, 'Создан продукт 2ой категории')

        # Выполняем скрипт
        args = argparse.Namespace(apply=True)
        tap.ok(await main(args), 'Скрипт сработал')

        group1 = await ProductGroup.load(group1.group_id)
        tap.ok(group1, 'Категория 1 не удалена')
        group2 = await ProductGroup.load(group2.group_id)
        tap.ok(group2, 'Категория 2 не удалена')

async def test_child_active(tap, dataset):
    with tap.plan(5, 'Удаление категорий со статусом removed с подкатегорией'):
        group1 = await dataset.product_group(
            name="Сырки",
            status='removed',
        )
        group2 = await dataset.product_group(
            name="Онигири",
            parent_group_id=group1.group_id,
        )
        tap.ok(group1, 'Создана категория 1 со статусом removed')
        tap.ok(group2, 'Создана категория 2')

        # Выполняем скрипт
        args = argparse.Namespace(apply=True)
        tap.ok(await main(args), 'Скрипт сработал')

        group1 = await ProductGroup.load(group1.group_id)
        tap.ok(group1, 'Категория 1 не удалена')
        group2 = await ProductGroup.load(group2.group_id)
        tap.ok(group2, 'Категория 2 не удалена')

async def test_non_apply(tap, dataset):
    with tap.plan(5, 'Удаление категорий без применения (эмуляция)'):
        group1 = await dataset.product_group(
            name="Мороженки",
            status='removed',
        )
        group2 = await dataset.product_group(
            name="Онигири",
            status='removed',
        )
        tap.ok(group1, 'Создана категория 1 со статусом removed')
        tap.ok(group2, 'Создана категория 2 со статусом removed')

        # Выполняем скрипт
        args = argparse.Namespace(apply=False)
        tap.ok(await main(args), 'Скрипт сработал')

        group1 = await ProductGroup.load(group1.group_id)
        tap.ok(group1, 'Категория 1 не удалена')
        group2 = await ProductGroup.load(group2.group_id)
        tap.ok(group2, 'Категория 2 не удалена')

async def test_sub_sub_group(tap, dataset):
    with tap.plan(7, 'Удаление категорий подкатегории подкатегории'):
        group1 = await dataset.product_group(
            name="Мороженки",
            status='removed',
        )
        group2 = await dataset.product_group(
            name="Онигири",
            status='removed',
            parent_group_id=group1.group_id,
        )
        group3 = await dataset.product_group(
            name="Онигири",
            parent_group_id=group2.group_id,
        )
        tap.ok(group1, 'Создана категория 1 со статусом removed')
        tap.ok(group2, 'Создана категория 2 со статусом removed')
        tap.ok(group3, 'Создана категория 3')

        # Выполняем скрипт
        args = argparse.Namespace(apply=True)
        tap.ok(await main(args), 'Скрипт сработал')

        group1 = await ProductGroup.load(group1.group_id)
        tap.ok(group1, 'Категория 1 не удалена')
        group2 = await ProductGroup.load(group2.group_id)
        tap.ok(group2, 'Категория 2 не удалена')
        group2 = await ProductGroup.load(group2.group_id)
        tap.ok(group2, 'Категория 3 не удалена')
