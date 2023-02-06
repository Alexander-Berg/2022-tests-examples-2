import pytest

from stall import keyword
from stall.scripts.change_shelves import (
    change_shelves, FIELD_TO_CHANGE_NAME,
    NEW_VALUE, INDEX)


@pytest.mark.parametrize('target_status', ['disabled', 'removed'])
async def test_status_with_stock(tap, dataset, target_status):
    with tap.plan(3, 'Смена статуса при наличии стоков'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)
        await dataset.stock(count=300, reserve=100, shelf=shelf)

        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [
                    {
                        INDEX: 1,
                        FIELD_TO_CHANGE_NAME: 'status',
                        NEW_VALUE: target_status,
                    },
                    {
                        INDEX: 1,
                        FIELD_TO_CHANGE_NAME: 'width',
                        NEW_VALUE: 100,
                    }
                ]
            },
            apply=True)
        tap.eq(len(errors), 1, '1 ошибка')

        await shelf.reload()
        tap.eq(shelf.status, 'active', 'статус не изменен')
        tap.eq(shelf.width, 100, 'ширина изменена')


@pytest.mark.parametrize('target_status', ['disabled', 'removed'])
async def test_status_empty_stock(tap, dataset, target_status):
    with tap.plan(2, 'Смена статуса при наличии пустых стоков'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)
        await dataset.stock(count=0, shelf=shelf)

        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [
                    {
                        INDEX: 1,
                        FIELD_TO_CHANGE_NAME: 'status',
                        NEW_VALUE: target_status,
                    }
                ]
            },
            apply=True)
        tap.eq(errors, [], 'ошибок нет')

        await shelf.reload()
        tap.eq(shelf.status, target_status, 'статус не изменен')


@pytest.mark.parametrize('status', ['disabled', 'removed'])
async def test_status_no_stocks(
        tap, dataset, status
):
    with tap.plan(2, 'Смена статуса при отсутствии стоков'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)

        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [{
                    INDEX: 1,
                    FIELD_TO_CHANGE_NAME: 'status',
                    NEW_VALUE: status,
                }]
            },
            apply=True)
        tap.eq(errors, [], 'ошибок нет')

        await shelf.reload()
        tap.eq(shelf.status, status, 'корректный статус')


async def test_type_with_stock(tap, dataset):
    with tap.plan(2, 'Смена типа при наличии стоков'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='store')
        await dataset.stock(count=300, reserve=100, shelf=shelf)

        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [{
                    INDEX: 1,
                    FIELD_TO_CHANGE_NAME: 'type',
                    NEW_VALUE: 'parcel',
                }]
            },
            apply=True)
        tap.eq(len(errors), 1, '1 ошибка')

        await shelf.reload()
        tap.eq(shelf.type, 'store', 'тип не изменен')


async def test_status_active(tap, dataset):
    with tap.plan(2, 'Смена статуса в active'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, status='disabled')

        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [{
                    INDEX: 1,
                    FIELD_TO_CHANGE_NAME: 'status',
                    NEW_VALUE: 'active',
                }]
            },
            apply=True)
        tap.eq(errors, [], 'ошибок нет')

        await shelf.reload()
        tap.eq(shelf.status, 'active', 'корректный статус')


async def test_apply_false(tap, dataset):
    with tap.plan(2, 'apply=False'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, status='disabled')

        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [{
                    INDEX: 1,
                    FIELD_TO_CHANGE_NAME: 'status',
                    NEW_VALUE: 'active',
                }]
            },
            apply=False)
        tap.eq(errors, [], 'ошибок нет')

        await shelf.reload()
        tap.eq(shelf.status, 'disabled', 'параметр не изменен')


async def test_incorrect_status(tap, dataset):
    with tap.plan(2, 'Некорректный параметр'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)

        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [{
                    INDEX: 1,
                    FIELD_TO_CHANGE_NAME: 'status',
                    NEW_VALUE: 'incorrect',
                }]
            },
            apply=True)
        tap.eq(len(errors), 1, '1 ошибка')

        await shelf.reload()
        tap.eq(shelf.status, 'active', 'статус не изменен')


async def test_title_full(tap, dataset):
    with tap.plan(2, 'Смена наименования'):
        store = await dataset.store()
        old_title = f'Я1 - {keyword.keyword()}'
        shelf = await dataset.shelf(store=store, title=old_title, rack='Я')

        new_title = f'КФТ-1 - {keyword.keyword()}'
        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={
                shelf.external_id: [{
                    INDEX: 1,
                    FIELD_TO_CHANGE_NAME: 'title',
                    NEW_VALUE: new_title,
                }]
            },
            apply=True)
        tap.eq(errors, [], 'ошибок нет')

        await shelf.reload()
        tap.eq(shelf.title, new_title, 'корректное наименование')


async def test_empty_shelves_changes(tap, dataset):
    with tap.plan(1, 'Пустой словарь изменений'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)
        errors = await change_shelves(
            store_exid=store.external_id,
            shelves=[shelf],
            shelves_changes={},
            apply=True)
        tap.eq(errors, [], 'ошибок нет')
