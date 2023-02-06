import pytest


@pytest.fixture
def yamlcase_assertion_mongo(mongodb, object_substitute):
    async def run_assertion(assertion):
        # TODO: check schema
        collection_name = assertion['collection']
        operation = assertion['operation']

        assert collection_name in mongodb
        assert operation in _MONGODB_ASSERTIONS

        collection = mongodb[collection_name]

        _MONGODB_ASSERTIONS[operation](
            assertion,
            collection=collection,
            object_substitute=object_substitute,
        )

    return run_assertion


def _assertion_find_one(assertion, *, collection, object_substitute):
    query = object_substitute(assertion.get('query', {}))
    projection = assertion.get('projection', None)
    expected_result = object_substitute(assertion['expected'])
    result = collection.find_one(query, projection)
    assert result == expected_result


def _assertion_find(assertion, *, collection, object_substitute):
    query = object_substitute(assertion.get('query', {}))
    projection = assertion.get('projection', None)
    sort_order = assertion.get('sort', None)
    expected_result = object_substitute(assertion['expected'])
    cursor = collection.find(query, projection, sort=sort_order)
    result = list(cursor)
    assert result == expected_result


_MONGODB_ASSERTIONS = {
    'find-one': _assertion_find_one,
    'find': _assertion_find,
}
