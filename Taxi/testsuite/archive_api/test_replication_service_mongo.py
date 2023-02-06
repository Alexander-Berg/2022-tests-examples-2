import bson
import bson.binary as bbin
import bson.json_util
import pymongo
import pytest

from taxi_tests.utils import ordered_object


@pytest.fixture
def dummy_replication_single(mockserver):
    @mockserver.json_handler('/replication/configuration/queue_mongo')
    def mock_replication(request):
        return {
            'queue_mongo_collections': [
                {
                    'rule_name': 'order_proc',
                    'number_of_shards': 1,
                    'collections': [
                        {
                            'connection': 'replication_queue',
                            'database': 'replication_queue',
                            'collection': 'order_proc_00',
                            'shard_num': 0,
                        },
                    ],
                },
            ],
        }


@pytest.fixture
def dummy_replication_multi(mockserver):
    @mockserver.json_handler('/replication/configuration/queue_mongo')
    def mock_replication(request):
        return {
            'queue_mongo_collections': [
                {
                    'rule_name': 'order_proc',
                    'number_of_shards': 3,
                    'collections': [
                        {
                            'connection': 'replication_queue',
                            'database': 'replication_queue',
                            'collection': 'order_proc_10',
                            'shard_num': 0,
                        },
                        {
                            'connection': 'replication_queue',
                            'database': 'replication_queue',
                            'collection': 'order_proc_11',
                            'shard_num': 1,
                        },
                        {
                            'connection': 'replication_queue',
                            'database': 'replication_queue',
                            'collection': 'order_proc_12',
                            'shard_num': 2,
                        },
                    ],
                },
            ],
        }


@pytest.fixture
def dummy_replication_not_full(mockserver):
    @mockserver.json_handler('/replication/configuration/queue_mongo')
    def mock_replication(request):
        return {
            'queue_mongo_collections': [
                {
                    'rule_name': 'order_proc',
                    'number_of_shards': 3,
                    'collections': [
                        {
                            'connection': 'replication_queue',
                            'database': 'replication_queue',
                            'collection': 'order_proc_20',
                            'shard_num': 0,
                        },
                        {
                            'connection': 'replication_queue',
                            'database': 'replication_queue',
                            'collection': 'order_proc_22',
                            'shard_num': 2,
                        },
                    ],
                },
            ],
        }


@pytest.mark.config(ARCHIVE_API_QUEUE_MONGO_RULE_LIST=['order_proc'])
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_single_queue(
        taxi_archive_api, db, settings, dummy_replication_single,
):
    mongo_docs = [{'_id': 'single_queue_order_id'}]
    _prepare_database(settings, 'order_proc_00', mongo_docs)

    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'id': 'single_queue_order_id'},
    )
    _check_restore_response(response, ['single_queue_order_id'])
    _check_restored_docs(db, ['single_queue_order_id'])


@pytest.mark.config(ARCHIVE_API_QUEUE_MONGO_RULE_LIST=['order_proc'])
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_multi_queue(
        taxi_archive_api, db, settings, dummy_replication_multi,
):
    mongo_docs = [{'_id': 'multi_queue_order_id_shard_0'}]
    _prepare_database(settings, 'order_proc_10', mongo_docs)

    response = taxi_archive_api.post(
        'archive/order_proc/restore',
        json={'id': 'multi_queue_order_id_shard_0'},
    )
    _check_restore_response(response, ['multi_queue_order_id_shard_0'])
    _check_restored_docs(db, ['multi_queue_order_id_shard_0'])


@pytest.mark.config(ARCHIVE_API_QUEUE_MONGO_RULE_LIST=['order_proc'])
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_restore_multi_queue_reorder(
        taxi_archive_api, db, settings, dummy_replication_multi,
):
    mongo_docs = [
        {
            '_id': 'multi_queue_order_id',
            'indexes': {'reorder': {'id': 'multi_queue_order_id_reorder'}},
        },
    ]
    _prepare_database(settings, 'order_proc_11', mongo_docs)

    response = taxi_archive_api.post(
        'archive/order_proc/restore',
        json={'id': 'multi_queue_order_id_reorder'},
    )
    _check_restore_response(response, ['multi_queue_order_id_reorder'])
    _check_restored_docs(db, ['multi_queue_order_id'])


@pytest.mark.config(ARCHIVE_API_QUEUE_MONGO_RULE_LIST=['order_proc'])
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_bulk_restore_single_queue(
        taxi_archive_api, db, settings, dummy_replication_single,
):
    mongo_docs = [
        {'_id': 'single_queue_order_id_0'},
        {'_id': 'single_queue_order_id_1'},
    ]
    _prepare_database(settings, 'order_proc_00', mongo_docs)

    request_ids = ['single_queue_order_id_0', 'single_queue_order_id_1']
    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'ids': request_ids},
    )
    _check_restore_response(response, request_ids)
    _check_restored_docs(db, request_ids)


@pytest.mark.config(ARCHIVE_API_QUEUE_MONGO_RULE_LIST=['order_proc'])
@pytest.mark.now('2018-02-16T15:00:00Z')
def test_bulk_restore_multi_queue(
        taxi_archive_api, db, settings, dummy_replication_multi,
):
    mongo_docs = [{'_id': 'multi_queue_order_id_shard_0'}]
    _prepare_database(settings, 'order_proc_10', mongo_docs)

    mongo_docs = [{'_id': 'multi_queue_order_id_shard_1'}]
    _prepare_database(settings, 'order_proc_11', mongo_docs)

    request_ids = [
        'multi_queue_order_id_shard_0',
        'multi_queue_order_id_shard_1',
    ]
    response = taxi_archive_api.post(
        'archive/order_proc/restore', json={'ids': request_ids},
    )
    _check_restore_response(response, request_ids)
    _check_restored_docs(db, request_ids)


def _check_response(response, order_id):
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    assert response_json == {'source': 'repl_queue', 'doc': {'_id': order_id}}


def _check_bulk_response(response, order_ids):
    expected_response = []
    for order_id in order_ids:
        expected_response.append(
            {'source': 'repl_queue', 'doc': {'_id': order_id}},
        )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/bson'
    response_json = bson.BSON(response.content).decode()
    ordered_object.assert_eq(response_json['items'], expected_response, [''])


def _check_restore_response(response, order_ids):
    expected_response = []
    for order_id in order_ids:
        expected_response.append({'id': order_id, 'status': 'restored'})

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    ordered_object.assert_eq(response.json(), expected_response, [''])


def _check_restored_docs(db, order_ids):
    for order_id in order_ids:
        doc = db.order_proc.find_one({'_id': order_id})
        assert doc is not None


def _prepare_database(settings, collection_name, docs):
    mongo_client = pymongo.MongoClient(
        settings.MONGO_CONNECTIONS['replication_queue'],
    )
    mongo_collection = mongo_client['replication_queue'][collection_name]
    bulk = mongo_collection.initialize_ordered_bulk_op()
    bulk.find({}).remove()
    for doc in docs:
        bulk.insert(_prepare_doc(doc))
    bulk.execute()


def _prepare_doc(doc):
    mongo_doc = {'_id': doc['_id']}
    bin_doc = bson.raw_bson.RawBSONDocument(bson.BSON.encode(mongo_doc))
    doc['data'] = bbin.Binary(bin_doc.raw, 0)
    return doc
