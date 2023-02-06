import argparse
from collections import defaultdict
import csv
import os

from scripts.dev.add_shelves_to_racks_csv import main
from stall.model.shelf import Shelf


# pylint: disable=too-many-statements,too-many-locals, too-many-branches
async def test_old(tap, dataset, uuid):
    with tap.plan(
            12,
            'без типа полки и типа хранения, пропуск несуществующего стеллажа'
    ):
        store1 = await dataset.store()
        await dataset.shelf(store=store1, rack='H', title='H-1')
        await dataset.shelf(store=store1, rack='I', title='I-1')

        store2 = await dataset.store()
        await dataset.shelf(store=store2, rack='H', title='H-1')

        fake_store_exid = uuid()

        with open('add_shelves.csv', 'w', newline='') as f:
            writer = csv.writer(f,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL,
                                )
            writer.writerows([
                ['store_external_id', 'rack', 'title', 'order'],
                # полка создается
                [store1.external_id, 'H', 'H-123', 2],
                # дубль названия
                [store1.external_id, 'I', 'I-1', 1],
                # полка создается
                [store2.external_id, 'H', 'H-234', 3],
                # стелажа нет, игнорируется
                [store2.external_id, 'I', 'I-1', 1],
                # несуществующая лавка
                [fake_store_exid, 'H', 'H-1', 5],
            ])

        args = argparse.Namespace(
            apply=True, create_new_rack=False, input_file='add_shelves.csv')
        await main(args)

        shelves1 = defaultdict(list)
        for shelf in await Shelf.list(
                by='full',
                db={'mode': 'slave'},
                conditions=[('store_id', store1.store_id)],
                sort=(),
        ):
            shelves1[shelf.rack].append(shelf)

        tap.eq(len(shelves1['H']), 2, 'полка создалась')
        tap.eq(
            {shelf.title for shelf in shelves1['H']},
            {'H-1', 'H-123'},
            'названия корректные'
        )
        with [
            shelf for shelf in shelves1['H'] if shelf.title == 'H-123'
        ][0] as shelf:
            tap.eq(shelf.type, 'store', 'type')
            tap.eq(shelf.tags, [], 'tags')
            tap.eq(shelf.order, 2, 'tags')

        tap.eq(len(shelves1['I']), 1, 'полка с дублем названия не создалась')

        shelves2 = defaultdict(list)
        for shelf in await Shelf.list(
                by='full',
                db={'mode': 'slave'},
                conditions=[('store_id', store2.store_id)],
                sort=(),
        ):
            shelves2[shelf.rack].append(shelf)

        tap.eq(len(shelves2['H']), 2, 'полка создалась')
        tap.eq(
            {shelf.title for shelf in shelves2['H']},
            {'H-1', 'H-234'},
            'названия корректные'
        )
        with [
            shelf for shelf in shelves2['H'] if shelf.title == 'H-234'
        ][0] as shelf:
            tap.eq(shelf.type, 'store', 'type')
            tap.eq(shelf.tags, [], 'tags')
            tap.eq(shelf.order, 3, 'tags')

        tap.eq(
            len(shelves2.get('I', [])),
            0,
            'полка на новом стеллаже не создалась'
        )

        os.remove('add_shelves.csv')


async def test_new(tap, dataset, uuid):
    with tap.plan(
            14,
            'c типами полки и хранения, создание несуществующего стеллажа'
    ):
        store1 = await dataset.store()
        await dataset.shelf(store=store1, rack='H', title='H-1')
        await dataset.shelf(store=store1, rack='I', title='I-1')

        store2 = await dataset.store()
        await dataset.shelf(store=store2, rack='H', title='H-1')
        await dataset.shelf(store=store2, rack='J', title='J-1')

        fake_store_exid = uuid()

        with open('add_shelves.csv', 'w', newline='') as f:
            writer = csv.writer(f,
                                delimiter=',',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL,
                                )
            writer.writerows([
                [
                    'store_external_id', 'rack',
                    'title', 'order', 'type', 'tag'
                ],
                # полка создается
                [store1.external_id, 'H', 'H-123', 2, 'markdown', 'safe'],
                # дубль названия
                [store1.external_id, 'I', 'I-1', 1, 'store', None],
                # полка без type на существующем стеллаже создается
                [store2.external_id, 'H', 'H-234', 3, None, None],
                # стелажа нет, создается
                [store2.external_id, 'I', 'I-1', 1, 'incoming', None],
                # стелажа нет, не создается, так как не передан тип
                [store2.external_id, 'K', 'K-1', 1, None, None],
                # некорректные параметры, не создается
                [store2.external_id, 'J', 'J-2', 1, 'JJJ', 'J'],
                # несуществующая лавка
                [fake_store_exid, 'H', 'H-1', 5, 'store', None],
            ])

        args = argparse.Namespace(
            apply=True, input_file='add_shelves.csv', create_new_rack=True)
        await main(args)

        shelves1 = defaultdict(list)
        for shelf in await Shelf.list(
                by='full',
                db={'mode': 'slave'},
                conditions=[('store_id', store1.store_id)],
                sort=(),
        ):
            shelves1[shelf.rack].append(shelf)

        tap.eq(len(shelves1['H']), 2, 'полка создалась')
        tap.eq(
            {shelf.title for shelf in shelves1['H']},
            {'H-1', 'H-123'},
            'названия корректные'
        )
        with [
            shelf for shelf in shelves1['H'] if shelf.title == 'H-123'
        ][0] as shelf:
            tap.eq(shelf.type, 'markdown', 'type')
            tap.eq(shelf.tags, ['safe'], 'tags')
            tap.eq(shelf.order, 2, 'tags')

        tap.eq(len(shelves1['I']), 1, 'полка с дублем названия не создалась')

        shelves2 = defaultdict(list)
        for shelf in await Shelf.list(
                by='full',
                db={'mode': 'slave'},
                conditions=[('store_id', store2.store_id)],
                sort=(),
        ):
            shelves2[shelf.rack].append(shelf)

        tap.eq(len(shelves2['H']), 2, 'полка создалась')
        tap.eq(
            {shelf.title for shelf in shelves2['H']},
            {'H-1', 'H-234'},
            'названия корректные'
        )
        with [
            shelf for shelf in shelves2['H'] if shelf.title == 'H-234'
        ][0] as shelf:
            tap.eq(shelf.type, 'store', 'type')
            tap.eq(shelf.tags, [], 'tags')
            tap.eq(shelf.order, 3, 'tags')

        tap.eq(
            len(shelves2.get('I', [])),
            1,
            'полка без tag на новом стеллаже создалась'
        )
        tap.eq(
            len(shelves2.get('K', [])),
            0,
            'полка без type на новом стеллаже не создалась'
        )
        tap.eq(
            len(shelves2['J']),
            1,
            'полка с некорректными параметрами не создалась'
        )

        os.remove('add_shelves.csv')
