from motor import motor_asyncio
import pytest

from taxi import db

from replication.common import mongo_settings_parser
from replication.common import sharded_mongo
from replication.common.pytest import env_util


CONNECTION_STRING = 'arbitrary-connection-string'


# TODO: heal test
@env_util.parametrize_test_env(testsuite=False, dmp=False)
@pytest.mark.parametrize('secondary', (False, True))
def test_create_collection(
        monkeypatch,
        mongo_collections_getter,
        secondary: bool,
        replication_ctx,
):
    monkeypatch.setattr(
        mongo_settings_parser,
        'get_db_settings_collections',
        mongo_collections_getter,
    )
    replication_yaml = replication_ctx.rule_keeper.replication_yaml
    arbitrary_collection_alias = next(
        iter(
            mongo_settings_parser.get_db_settings_collections(
                replication_yaml,
            ).keys(),
        ),
    )
    collection = sharded_mongo.create_collection(
        replication_yaml,
        arbitrary_collection_alias,
        CONNECTION_STRING,
        db.get_mongo_settings(secondary=secondary),
    )
    assert isinstance(collection, motor_asyncio.AsyncIOMotorCollection)
