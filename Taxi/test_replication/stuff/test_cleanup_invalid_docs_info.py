# pylint: disable=protected-access
from replication.foundation.invalid_docs import db_wrapper
from replication.replication import classes
from replication.stuff import cleanup_invalid_docs_info


_CACHE = [
    db_wrapper.InvalidDocInfo(
        rule_name='foo_bar',
        doc_id='123456789',
        stage='staging_foo_bar',
        unit_id='unit_id',
        error_ts=None,
        errors=None,
    ),
]


async def test_rule_is_not_available(replication_ctx, loop, monkeypatch):
    monkeypatch.setattr(db_wrapper.InvalidDocsWrapperCache, 'cache', _CACHE)
    try:
        await cleanup_invalid_docs_info._cleanup(replication_ctx)
    except classes.UnknownRuleError as err:
        assert False, err
