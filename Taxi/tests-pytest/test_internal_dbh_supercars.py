import pytest

from taxi.internal import dbh


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('raw_doc,clid,is_supercar', [
    ({'_id': 'K137AT178'}, 'clid', True),
    ({'_id': 'K137AT178'}, None, True),
    ({'_id': 'K137AT178', 'conditions': {}}, 'clid', True),
    ({'_id': 'K137AT178', 'conditions': {'park_in': []}}, 'clid', True),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['clid']}}, None, False),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['clid']}}, 'clid', True),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['clOd']}}, 'clid', False),
])
def test_conditions_satisfy(raw_doc, clid, is_supercar):
    doc = dbh.supercars.Doc(raw_doc)

    assert is_supercar == doc.satisfies_conditions(clid=clid)


@pytest.mark.filldb(_specified=True, supercars='')
@pytest.inline_callbacks
def test_supercar():
    supercar = yield dbh.supercars.Doc.find_one_by_id('A130MP777')
    assert supercar
    assert not supercar.get('conditions')


@pytest.mark.filldb(_specified=True, supercars='')
@pytest.mark.parametrize('car_number,clid,is_supercar', [
    ('A130MP777', None, True),
    ('K170AT178', 'clid', True),
    ('K170AT178', 'vam_vezyet', False),
    ('A777AA178', 'clid', False),
])
@pytest.inline_callbacks
def test_is_supercars(car_number, clid, is_supercar):
    supercar_docs = yield dbh.supercars.Doc.find_many()
    assert len(supercar_docs) > 0

    supercars_by_id = dbh.supercars.Doc.group_by_id(supercar_docs)

    assert is_supercar == dbh.supercars.is_supercar(
        docs_by_id=supercars_by_id, car_number=car_number, clid=clid
    )


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('car_number,park_in,expected', [
    ('A130MP777', [], {'_id': 'A130MP777', 'conditions': {}}),
    ('A130MP777', None, {'_id': 'A130MP777', 'conditions': {}}),
    ('A130MP777', ['clid1', 'clid2'],
     {'_id': 'A130MP777', 'conditions': {'park_in': ['clid2', 'clid1']}}),
    ('A130MP777', ['clid', 'clid'],
     {'_id': 'A130MP777', 'conditions': {'park_in': ['clid']}}),
])
def test_create_query(car_number, park_in, expected):
    result = dbh.supercars.Doc.get_create_query(car_number, park_in)
    assert expected == result


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('raw_doc,park_in,expected', [
    ({'_id': 'K137AT178'}, {'clid'}, None),
    ({'_id': 'K137AT178'}, None, None),
    ({'_id': 'K137AT178', 'conditions': {}}, {'clid'}, None),
    ({'_id': 'K137AT178', 'conditions': {'park_in': []}}, {'clid'}, None),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['clid']}}, None,
     {'$unset': {'conditions.park_in': 1}}),
    ({'_id': 'K137AT77', 'conditions': {'park_in': ['clid']}}, {'clid'}, None),
    ({'_id': 'K137AT77', 'conditions': {'park_in': ['clOd']}}, {'clid'},
     {'$addToSet': {'conditions.park_in': {'$each': ['clid']}}}),
    ({'_id': 'K137AT77', 'conditions': {'park_in': ['clid']}}, {'clid', 'add'},
     {'$addToSet': {'conditions.park_in': {'$each': ['add']}}}),
])
def test_append_query(raw_doc, park_in, expected):
    doc = dbh.supercars.Doc(raw_doc)
    result = doc.get_append_query(park_in)
    assert expected == result


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('raw_doc,parks_to_remove,expected_action', [
    ({'_id': 'K137AT178', 'conditions': {}}, [],
     dbh.supercars.RemoveAction(remove=True, update_query=None, error=None)),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['100500']}}, [],
     dbh.supercars.RemoveAction(remove=True, update_query=None, error=None)),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['100500']}}, ['100500'],
     dbh.supercars.RemoveAction(remove=True, update_query=None, error=None)),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['100500']}}, ['100700'],
     dbh.supercars.RemoveAction(
         remove=False, update_query=None,
         error='Can\'t unlink supercar K137AT178 from 100700 parks.')),
    ({'_id': 'K137AT178', 'conditions': {}}, ['100700'],
     dbh.supercars.RemoveAction(
         remove=False, update_query=None,
         error='Can\'t unlink global supercar K137AT178 from 100700 parks.')),
    ({'_id': 'K137AT178', 'conditions': {'park_in': ['100500', '100501']}},
     ['100500'], dbh.supercars.RemoveAction(
         remove=False, update_query={
            '$pull': {
                'conditions.park_in': {'$each': ['100500']}
            }
        }, error=None)),
])
def test_remove_query(raw_doc, parks_to_remove, expected_action):
    doc = dbh.supercars.Doc(raw_doc)
    result = doc.get_remove_action(parks_to_remove)
    assert expected_action == result
