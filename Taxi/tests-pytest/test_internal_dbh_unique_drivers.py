import datetime

import pytest

from taxi.core import async
from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('use_secondary', [
    False,
    True
])
@pytest.inline_callbacks
def test_find_one_by_license_conn_type(use_secondary):
    # Test fetching document from primary/secondary

    doc = {'_id': 'megadoc', 'licenses': [{'license': 'abc'}]}
    queries = []

    class Collection(object):
        is_secondary = False

        @async.inline_callbacks
        def find_one(self, query, fields=None):
            yield
            queries.append((self.is_secondary, query))
            async.return_value(doc)

    collection = Collection()
    collection.secondary = Collection()
    collection.secondary.is_secondary = True

    class Doc(dbh.unique_drivers.Doc):

        @classmethod
        def _get_db_collection(cls, secondary=False):
            return collection.secondary if secondary else collection

    license = doc['licenses'][0]['license']
    secondary = use_secondary
    found = yield Doc.find_one_by_license(license, secondary=secondary)
    assert queries == [(secondary, {'licenses.license': license})]
    assert found._id == doc['_id']


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_find_one_by_license_not_found(stub):
    # Test proper exception is raised

    class NotFound(Exception):
        pass

    class Doc(dbh.unique_drivers.Doc):
        _db_collection = stub(find_one=lambda *args, **kwargs: None)
        _not_found_class = NotFound

    with pytest.raises(NotFound):
        yield Doc.find_one_by_license('unknown')


@pytest.mark.now('2016-12-05T11:39:00')
@pytest.mark.filldb(
    unique_drivers='for_is_frauder_test',
)
@pytest.mark.parametrize('driver_license,expected_result', [
    ('some_good_license', False),
    ('some_frauder_license', True),
    ('some_blacklisted_license', True),
    ('some_blacklisted_with_till_license', True),
    ('some_blacklisted_with_expired_till_license', False),
])
@pytest.inline_callbacks
def test_is_frauder(driver_license, expected_result):
    unique_driver = yield dbh.unique_drivers.Doc.find_one_by_license(
        driver_license
    )
    actual_result = unique_driver.is_frauder()
    assert actual_result is expected_result


@pytest.mark.now('2016-12-05T11:39:00')
@pytest.mark.filldb(
    unique_drivers='for_is_frauder_test',
)
@pytest.mark.parametrize('stamp,with_blacklisted,expected_licenses', [
    (
        None, True,
        {
            'some_frauder_license',
            'some_blacklisted_license',
            'some_blacklisted_with_till_license',
        }
    ),
    (
        None, False,
        {
            'some_frauder_license',
        }
    ),
    (
        datetime.datetime(2018, 1, 1), True,
        {
            'some_frauder_license',
            'some_blacklisted_license',
        }
    ),
    (
        datetime.datetime(2018, 1, 1), False,
        {
            'some_frauder_license',
        }
    ),
])
@pytest.inline_callbacks
def test_get_frauder_licenses(stamp, with_blacklisted, expected_licenses):
    actual_licenses = yield dbh.unique_drivers.Doc.get_frauder_licenses(
        stamp=stamp,
        with_blacklisted=with_blacklisted,
    )
    assert actual_licenses == expected_licenses


@pytest.inline_callbacks
def _check_history(licenses, expected_history):
    blacklist_history_docs = yield dbh.blacklist_history.Doc.find_many(
        {
            dbh.blacklist_history.Doc.license: {'$in': licenses}
        }
    )
    blacklist_history = [dict(blacklist_history_doc)
                         for blacklist_history_doc in blacklist_history_docs]
    for item in blacklist_history:
        item.pop('_id')
        item['details'].pop('till', None)
    assert blacklist_history == expected_history


@pytest.mark.now('2018-01-01T00:00:00')
@pytest.mark.filldb(
    unique_drivers='blacklist_test',
)
@pytest.mark.parametrize('licenses,expected_history', [
    (
        ['TEST_LICENSE_2'],
        [
            {
                'license': 'TEST_LICENSE_2',
                'created': datetime.datetime(2018, 1, 1),
                'blacklisted': True,
                'details': {
                    'login': 'test_login',
                    'at': datetime.datetime(2018, 1, 1),
                    'otrs_ticket': 'test_ticket',
                    'reason': 'test_reason'
                }
            }
        ]
    )
])
@pytest.inline_callbacks
def test_add_to_blacklist(licenses, expected_history):
    now = datetime.datetime.utcnow()
    yield dbh.unique_drivers.Doc.add_to_blacklist(
        licenses, 'test_login', 'test_reason', 'test_ticket', now)
    unique_drivers = yield dbh.unique_drivers.Doc.find_many_by_licenses(
        licenses
    )
    assert unique_drivers
    for unique_driver in unique_drivers:
        assert unique_driver.blacklisted
    yield _check_history(licenses, expected_history)


@pytest.mark.now('2018-01-01T00:00:00')
@pytest.mark.filldb(
    unique_drivers='blacklist_test',
)
@pytest.mark.parametrize('licenses,expected_history', [
    (
        ['TEST_LICENSE_1'],
        [
            {
                'license': 'TEST_LICENSE_1',
                'created': datetime.datetime(2018, 1, 1),
                'blacklisted': False,
                'details': {
                    'at': datetime.datetime(2018, 1, 1),
                    'login': 'test_login',
                    'otrs_ticket': 'test_ticket',
                    'reason': 'test_reason'
                }
            }
        ]
    )
])
@pytest.inline_callbacks
def test_remove_from_blacklist(licenses, expected_history):
    yield dbh.unique_drivers.Doc.remove_from_blacklist_manually(
        licenses, 'test_login', 'test_reason', 'test_ticket')
    unique_drivers = yield dbh.unique_drivers.Doc.find_many_by_licenses(
        licenses
    )
    assert unique_drivers
    for unique_driver in unique_drivers:
        assert not unique_driver.blacklisted
    yield _check_history(licenses, expected_history)


@pytest.mark.filldb(
    unique_drivers='remove_with_logging',
)
@pytest.inline_callbacks
def test_remove_with_logging():
    doc_id = 'test_id_1'
    yield dbh.unique_drivers.Doc.remove_driver_with_logging(doc_id)
    try:
        yield dbh.unique_drivers.Doc.find_one_by_id(doc_id)
    except dbh.unique_drivers.NotFound:
        assert True
    else:
        assert False

    deleted_docs = yield dbh.unique_drivers_deletions.Doc.find_many({
        dbh.unique_drivers_deletions.Doc.doc_id: doc_id
    })
    assert len(deleted_docs) == 1
    assert deleted_docs[0].doc_id == doc_id


@pytest.mark.parametrize('licenses,excluded_ids,expected,expected_logged', [
    (
        ['TEST_LICENSE_1', 'TEST_LICENSE_3', 'TEST_LICENSE_4'],
        ['test_id_1', 'test_id_2'],
        [
            {
                dbh.unique_drivers.Doc.id: "test_id_1",
                dbh.unique_drivers.Doc.licenses: [
                    {
                        dbh.unique_drivers.Doc.licenses.license.key: "TEST_LICENSE_1"
                    }
                ]
            }, {
                dbh.unique_drivers.Doc.id: "test_id_2",
                dbh.unique_drivers.Doc.licenses: [
                    {
                        dbh.unique_drivers.Doc.licenses.license.key: "TEST_LICENSE_2"
                    }
                ]
            }
        ],
        ['test_id_3', 'test_id_4']
    ),
    (
        ['TEST_LICENSE_1', 'TEST_LICENSE_2', 'TEST_LICENSE_3', 'TEST_LICENSE_4'],
        [],
        [],
        ['test_id_1', 'test_id_2', 'test_id_3', 'test_id_4']
    )
])
@pytest.mark.filldb(
    unique_drivers='remove_with_logging',
)
@pytest.inline_callbacks
def test_remove_new_import(licenses, excluded_ids, expected, expected_logged):
    yield dbh.unique_drivers.Doc.remove_new_import(licenses, excluded_ids)
    docs = yield dbh.unique_drivers.Doc.find_many({})
    assert expected == docs

    logged_docs = yield dbh.unique_drivers_deletions.Doc.find_many({})
    assert expected_logged == [doc.doc_id for doc in logged_docs]
