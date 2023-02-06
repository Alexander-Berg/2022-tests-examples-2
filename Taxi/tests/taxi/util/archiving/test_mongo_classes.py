import datetime

import pytest

from taxi.util.archiving import mongo_classes


DOCS_COUNT = 12
SIMPLE_FETCHED_IDS = [
    '1',
    '2',
    '3',
    '5',
    '4',
    '6',
    '7',
    '8',
    '9',
    '12',
    '11',
    '10',
]
LARGE_BULK_FETCHED_IDS = [
    '1',
    '2',
    '2',
    '3',
    '3',
    '5',
    '5',
    '4',
    '4',
    '6',
    '6',
    '7',
    '7',
    '8',
    '8',
    '9',
    '9',
    '12',
    '12',
    '11',
    '11',
    '10',
    '10',
]
START_POINT = datetime.datetime(2018, 11, 14, 0)


@pytest.mark.mongodb_collections('archiving_test_collection')
@pytest.mark.now(START_POINT.isoformat())
@pytest.mark.parametrize(
    'fail_func,bulk_size,expected_fetch_tries,fetched_ids,error',
    [
        (
            lambda v: v % 3 in (1,),
            100,
            DOCS_COUNT * 3,
            LARGE_BULK_FETCHED_IDS,
            False,
        ),
        (
            lambda v: v % 4 in (1, 2),
            100,
            DOCS_COUNT * 4,
            LARGE_BULK_FETCHED_IDS,
            False,
        ),
        (lambda v: True, 100, 4, [], True),
        (lambda v: v % 3 in (1,), 1, 20, SIMPLE_FETCHED_IDS, False),
        (lambda v: v % 4 in (1, 2), 1, 27, SIMPLE_FETCHED_IDS, False),
        (
            lambda v: v % 4 in (1,) or v % 5 in (2,),
            1,
            23,
            SIMPLE_FETCHED_IDS,
            False,
        ),
        (lambda v: v > 5, 1, 9, ['1', '2', '3', '5', '4'], True),
        (lambda v: v > 5, 100, 9, ['1', '2', '3', '5', '4'], True),
    ],
)
async def test_doc_getter_errors(
        db, fail_func, bulk_size, expected_fetch_tries, fetched_ids, error,
):
    fetched = []

    class Getter(mongo_classes.DocGetter):
        def __init__(self):
            super().__init__(
                collection=db.archiving_test_collection,
                base_query={},
                field='updated',
                savepoint=START_POINT,
            )
            self.fetch_tries = 0

        async def _fetch_one(self):
            self.fetch_tries += 1
            if fail_func(self.fetch_tries):
                raise self._exceptions[0]
            if self.fetch_tries > 100:
                raise RuntimeError
            return await super()._fetch_one()

    getter = Getter()
    remover = mongo_classes.MongoBulkRemover(
        bulk_size,
        collection_name='archiving_test_collection',
        collection=db.archiving_test_collection,
        base_query={'updated': {'$lte': START_POINT}},
    )

    async def _do_stuff():
        async with remover:
            async for doc in getter:
                fetched.append(doc['_id'])
                await remover.add(doc)

    if error:
        # pylint: disable=protected-access
        with pytest.raises(getter._exceptions[0]):
            await _do_stuff()
    else:
        await _do_stuff()

    assert fetched == fetched_ids
    assert expected_fetch_tries == getter.fetch_tries
