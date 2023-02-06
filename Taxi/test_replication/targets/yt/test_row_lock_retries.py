import pytest

from replication.common import config_util
from replication.common.yt_tools import errors as yt_errors
from replication.foundation import consts
from replication.foundation import map_doc_classes
from replication.targets.yt import yt_targets as yt_target_classes


_ATTEMPTS_NUM = 3

DATA = [
    map_doc_classes.MapDocInfo(
        raw_doc_index=0,
        mapped_doc={'id': '1', 'value_1': None, 'value_2': None},
        doc_id='1',
    ),
]


def _get_yt_target(replication_ctx):
    rule = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='test_sharded_rule2',
        target_names='yt-test_sharded_rule2_sharded_struct-arni',
        target_types=[consts.TARGET_TYPE_YT],
    )[0]
    return rule.targets[0]


@pytest.mark.config(
    REPLICATION_YT_CTL={
        'yt_qos': {
            'attempts': _ATTEMPTS_NUM,
            'timeout': {
                '__default__': 0,
                'yt_transaction_lock_conflict': 0,
                'yt_tablet_not_mounted': 0,
            },
        },
    },
)
@pytest.mark.nofilldb()
async def test_row_lock_conflict_retries(monkeypatch, replication_ctx):
    yt_target = _get_yt_target(replication_ctx)

    count_retries = 0

    class _FakeAsyncYTClients:
        @staticmethod
        async def insert_rows(*args, **kwargs):
            nonlocal count_retries
            count_retries += 1

            if count_retries == _ATTEMPTS_NUM:
                return

            raise yt_target_classes.YTInsertionError(
                yt_error_key=yt_errors.TRANSACTION_LOCK_CONFLICT,
            )

    monkeypatch.setattr(
        yt_target_classes.YTTarget, '_async_yt_client', _FakeAsyncYTClients,
    )

    assert yt_target.meta.partial_update is True
    # pylint: disable=protected-access
    await yt_target._insert_rows_no_retry_schema(
        'test/test_struct', DATA, retries=True,
    )
    assert count_retries == _ATTEMPTS_NUM


@pytest.mark.nofilldb()
async def test_row_lock_conflict_default_retries(monkeypatch, replication_ctx):
    yt_target = _get_yt_target(replication_ctx)

    retries_config = config_util.get_yt_retries_config(replication_ctx.config)
    count_retries = 0

    class _FakeAsyncYTClients:
        @staticmethod
        async def insert_rows(*args, **kwargs):
            nonlocal count_retries
            count_retries += 1

            if count_retries == retries_config.attempts:
                return

            raise yt_target_classes.YTInsertionError(
                yt_error_key=yt_errors.TRANSACTION_LOCK_CONFLICT,
            )

    monkeypatch.setattr(
        yt_target_classes.YTTarget, '_async_yt_client', _FakeAsyncYTClients,
    )

    assert yt_target.meta.partial_update is True
    # pylint: disable=protected-access
    await yt_target._insert_rows_no_retry_schema(
        'test/test_struct', DATA, retries=True,
    )
    assert count_retries == retries_config.attempts


@pytest.mark.config(
    REPLICATION_YT_CTL={
        'yt_qos': {
            'attempts': 3,
            'timeout': {
                '__default__': 1,
                'yt_transaction_lock_conflict': 2,
                'yt_tablet_not_mounted': 3,
            },
        },
    },
)
@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'yt_error_key',
    [
        yt_errors.TRANSACTION_LOCK_CONFLICT,
        yt_errors.SCHEMA_ERROR,
        yt_errors.TABLET_NOT_MOUNTED,
        yt_errors.LONG_WAIT_ERRORS,
        'other-yt-error-key',
    ],
)
async def test_row_lock_conflict_retries_not_forever(
        monkeypatch, replication_ctx, yt_error_key,
):
    yt_target = _get_yt_target(replication_ctx)

    class _FakeAsyncYTClients:
        @staticmethod
        async def insert_rows(*args, **kwargs):
            raise yt_target_classes.YTInsertionError(yt_error_key=yt_error_key)

        @staticmethod
        async def mount_table(*args, **kwargs):
            pass

    monkeypatch.setattr(
        yt_target_classes.YTTarget, '_async_yt_client', _FakeAsyncYTClients,
    )

    assert yt_target.meta.partial_update is True
    # pylint: disable=protected-access
    with pytest.raises(yt_target_classes.YTInsertionError):
        await yt_target._insert_rows_no_retry_schema(
            'test/test_struct', DATA, retries=True,
        )
