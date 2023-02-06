import humbledb
import pymongo.errors
import pytest

from taxi.core import async
from taxi.internal.dbh import _helpers


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_find_one(stub, mock):
    # Test `_find_one` method

    found = object()

    @mock
    @async.inline_callbacks
    def find_one(*args, **kwargs):
        yield
        async.return_value(found)

    class Doc(_helpers.Doc):

        @classmethod
        def _get_db_collection(cls, secondary=False, fields=None):
            collection = stub(find_one=find_one)
            async.return_value(collection)

    assert (yield Doc._find_one(1, y=2)) == found
    assert find_one.calls == [{'args': (1,), 'kwargs': {'y': 2}}]


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('resp,req_kwargs', [
    ({'_id': 'doc_id'}, {}),
    ({'_id': 'doc_id'}, {'secondary': False}),
    ({'_id': 'doc_id'}, {'secondary': True}),
])
@pytest.inline_callbacks
def test_doc_class_find_one_by_id(resp, req_kwargs):
    # Test common method that returns instance of `Doc`

    queries = []

    class Collection(object):
        is_secondary = False

        @async.inline_callbacks
        def find_one(self, query, fields=None):
            yield
            queries.append((self.is_secondary, query))
            async.return_value(resp)

    collection = Collection()
    collection.secondary = Collection()
    collection.secondary.is_secondary = True

    class Doc(_helpers.Doc):

        @classmethod
        def _get_db_collection(cls, secondary=False):
            return collection.secondary if secondary else collection

    doc = yield Doc.find_one_by_id('doc_id', **req_kwargs)
    assert doc == resp
    assert doc._id == resp['_id']

    secondary = req_kwargs.get('secondary', False)
    assert queries == [(secondary, {'_id': 'doc_id'})]


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_doc_class_find_one_by_id_not_found(stub):
    # Test exception when document is not found

    class NotFound(Exception):
        """This exception will be raised if document was not found."""

    class Doc(_helpers.Doc):
        _not_found_class = NotFound

        @classmethod
        def _get_db_collection(cls, secondary=False, fields=None):
            return stub(find_one=lambda *args, **kwargs: None)

    with pytest.raises(NotFound):
        yield Doc.find_one_by_id('some_id')


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_doc_class_find_one_cached_by_id():
    # Test caching

    class NotFound(Exception):
        pass

    class Doc(_helpers.Doc):
        _not_found_class = NotFound
        _cache_inmemory_time = 10
        _cache_memcache_time = 10

        @classmethod
        @async.inline_callbacks
        def _find_one_by_id_silently(cls, doc_id):
            yield
            if doc_id == 'found':
                doc = {'_id': 'found'}
            else:
                doc = ()
            async.return_value(doc)

    doc = yield Doc.find_one_cached_by_id('found')
    assert doc._id == 'found'

    with pytest.raises(NotFound):
        yield Doc.find_one_cached_by_id('unknown')


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_remove_by_id():
    # Test removing document by id

    class Doc(_helpers.Doc):
        queries = []

        @classmethod
        @async.inline_callbacks
        def _remove(self, query):
            yield
            self.queries.append(query)

    yield Doc.remove_by_id('some_id')
    assert Doc.queries == [{'_id': 'some_id'}]


@pytest.mark.filldb(_fill=False)
def test_object_class():
    # Test proper way to work with embeded documents as with objects

    class Doc(_helpers.Doc):
        phones = humbledb.Embed('p')
        phones.phone = 'p'

    class Phone(_helpers.Object):

        def is_russian(self):
            return self.phone.startswith('+7')

    doc = Doc({'p': [{'p': '+71234...'}, {'p': '+81234'}]})
    phones = [Phone(p, Doc.phones.mapped()) for p in doc.phones]
    assert phones[0].is_russian()
    assert not phones[1].is_russian()


@pytest.mark.filldb(_fill=False)
def test_inddexed_object_class():
    # Test the way to index embeded documents

    class Doc(_helpers.Doc):
        phones = humbledb.Embed('p')
        phones.phone = 'p'

    class Phone(_helpers.IndexedObject):

        def is_russian(self):
            return self.phone.startswith('+7')

    doc = Doc({'p': [{'p': '+71234...'}, {'p': '+81234'}]})
    phones = Phone.extract(doc, doc.phones, Doc.phones.mapped())
    assert phones[0].is_russian()
    assert phones[0].index == 0
    assert phones[0].parent_object is doc
    assert not phones[1].is_russian()
    assert phones[1].index == 1
    assert phones[1].parent_object is doc


@pytest.mark.filldb(_fill=False)
def test_query_modifiers():
    # Test query helpers

    update = {}

    _helpers.Query.add_modifiers(update, '$set', '$inc')
    update['$set']['x'] = 1
    assert update == {'$set': {'x': 1}, '$inc': {}}

    _helpers.Query.drop_empty_modifiers(update)
    assert update == {'$set': {'x': 1}}


@pytest.mark.filldb(_fill=False)
def test_query_ensure_collection_exists(stub):
    # Test code that ensures that collection exists

    class Database(object):

        def __init__(self):
            self.exists = False

        def create_collection(self, name):
            if self.exists:
                raise pymongo.errors.CollectionInvalid
            self.exists = True

    collection = stub(name='cname', database=Database())

    # It's safe to create collection multiple times
    _helpers.Query.ensure_collection_exists(collection)
    _helpers.Query.ensure_collection_exists(collection)


@pytest.mark.filldb(_fill=False)
def test_copy_structure():
    # Test code that allows to reuse once described structure

    class Man(_helpers.Doc):
        name = 'n'
        contacts = humbledb.Embed('c')
        contacts.type = 't'
        contacts.value = 'v'

    class Company(_helpers.Doc):
        name = 'n'
        head = humbledb.Embed('h')
        head.id = 'i'
        head.contacts = humbledb.Embed('c')
        _helpers.copy_structure(Man.contacts, head.contacts)

    man = Man({
        '_id': 'volozh',
        'n': 'A. Volozh',
        'c': [{'t': 'email', 'v': 'volozh@yandex-team.ru'}],
    })
    company = Company({
        'n': 'Yandex',
        'h': {
            'i': 'volozh',
            'c': man.contacts,
        },
    })

    assert company.head.id == man._id
    assert company.head.contacts[0].type == 'email'
    assert company.head.contacts[0].value == 'volozh@yandex-team.ru'


@pytest.mark.filldb(_fill=False)
def test_from_json():

    class Tariff(_helpers.Doc):
        date_from = 'df'
        categories = humbledb.Embed('c')
        categories.distance_price_intervals = humbledb.Embed('dpi')
        categories.distance_price_intervals.price = 'p'
        categories.distance_price_intervals.begin = 'b'

    item = Tariff()
    item.date_from = '2016-01-01'
    item.categories = []
    cat1 = item.categories.new()
    cat1.distance_price_intervals = []
    item11 = cat1.distance_price_intervals.new()
    item11.price = 16
    item11.begin = 0
    cat2 = item.categories.new()
    cat2.distance_price_intervals = []
    item21 = cat2.distance_price_intervals.new()
    item21.price = 11
    item21.begin = 10
    item22 = cat2.distance_price_intervals.new()
    item22.price = 110
    item22.begin = 100

    jsoned = item.for_json()
    object = Tariff._from_json(jsoned)

    assert object.date_from == item.date_from
    assert len(object.categories) == len(item.categories)
    for (obj_cat, item_cat) in zip(object.categories, item.categories):
        assert len(obj_cat.distance_price_intervals) == \
               len(item_cat.distance_price_intervals)
        for (obj_dpi, item_dpi) in zip(obj_cat.distance_price_intervals,
                                       item_cat.distance_price_intervals):
            assert obj_dpi.price == item_dpi.price
            assert obj_dpi.begin == item_dpi.begin
