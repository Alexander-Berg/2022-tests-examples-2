from taxi.core import db


def test_collections():
    # Test all our collections are in module
    params = db.get_collections().items()
    for (in_module_name, (conn_name, db_name, coll_name)) in params:
        assert hasattr(db, in_module_name)
        wrapped_collection = getattr(db, in_module_name)
        assert wrapped_collection._connection_name == conn_name
        # Skip added by `_filldb` uuid4 ending
        assert wrapped_collection._database_name.startswith(db_name)
        assert wrapped_collection._collection_name == coll_name
