import pytest


@pytest.mark.mongodb_collections('foo_extra')
def test_extra_collection_is_accessible(mongo):
    # foo_extra is defined in test_example_service/schemas/mongo
    assert hasattr(mongo, 'foo_extra')
