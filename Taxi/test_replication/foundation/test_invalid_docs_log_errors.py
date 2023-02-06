# pylint: disable=protected-access
from replication.foundation.invalid_docs import clean


async def test_check_data_invalid_docs(replication_ctx):
    errors = await replication_ctx.rule_keeper.invalid_docs_wrapper.get_errors(
        rule_name='test_initialize_columns',
    )
    msg = clean._get_error_message(errors[0])
    assert msg == (
        'doc_id: b55b3944756a22dcb7289446eb0ab048\n'
        'stage: target, unit_id: None\n'
        'error_msg: , last occurred at: None'
    )

    msg = clean._get_error_message(errors[1])
    assert msg == (
        'doc_id: 91ea564adf3b31d5a402cf39610065e4\n'
        'stage: target, unit_id: None\n'
        'error_msg: column park_corp_vat, value 11700.0, '
        'error: expected int64, but got value of type '
        '<class \'yt.yson.yson_types.YsonDouble\'>, '
        'last occurred at: None'
    )
