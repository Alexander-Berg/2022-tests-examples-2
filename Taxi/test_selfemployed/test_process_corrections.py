# pylint: disable=redefined-outer-name,unused-variable,global-statement
# pylint: disable=too-many-statements
# pylint: disable=too-many-arguments
# pylint: disable=import-only-modules
import datetime as dt

import pytest

from selfemployed.crontasks import process_corrections
from selfemployed.fns import client as fns
from selfemployed.generated.cron import run_cron
from . import conftest


# pylint: disable=too-many-locals
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles (id, inn, status, park_id, driver_id,
                              created_at, modified_at)
        VALUES ('smz1', 'inn1', 'confirmed', 'p1', 'd1', NOW(), NOW()),
               ('smz2', 'inn2', 'confirmed', 'p2', 'd2', NOW(), NOW()),
               ('smz3', 'inn3', 'confirmed', 'p3', 'd3', NOW(), NOW()),
               ('smz4', 'inn4', 'confirmed', 'p4', 'd4', NOW(), NOW()),
               ('smz5', 'inn5', 'confirmed', 'p5', 'd5', NOW(), NOW()),
               ('smz7', 'inn7', 'confirmed', 'p7', 'd7', NOW(), NOW()),
               ('smz8', 'inn8', 'confirmed', 'p8', 'd8', NOW(), NOW());
       """,
    ],
)
@pytest.mark.pgsql(
    'selfemployed_orders@0', files=['test_process_corrections@0.sql'],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.config(
    SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION_JOB=(
        conftest.SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION_JOB
    ),
)
async def test_process_corrections(
        se_cron_context, mock_token_update, patch, monkeypatch,
):
    reverted_receipts = set()
    correction_updates = set()
    updated_receipts = set()
    inserted_receipts = set()
    # lower chunk quantity to test it
    monkeypatch.setattr(process_corrections, 'CORRECTION_CHUNK_SIZE', 2)

    expected_reverted = {
        ('inn1', 'tt1'),
        ('inn1', 'tt2'),
        ('inn1', 'tt3'),
        ('inn1', 'tt4'),
    }
    expected_correction_updates = {
        ('subv_processed_1_1', 'processed'),
        ('subv_processed_1_2', 'processed'),
        ('subv_processed_1_3', 'processed'),
        ('subv_processed_1_4', 'processed'),
        ('subv_processed_2', 'delayed'),
        ('subv_processed_3', 'delayed'),
        ('subv_processed_7', 'delayed'),
        ('subv_processed_8', 'delayed'),
        ('subv_processed_4', 'failed'),
        ('subv_processed_5', 'failed'),
        ('subv_processed_6', 'failed'),
        ('subv_delayed_1', 'delayed'),
        ('subv_failed_1', 'processed'),
        ('subv_failed_wont_fix_1', 'processed'),
        ('subv_missing_inn_1', 'processed'),
        ('subv_missing_inn_1_new', 'processed'),
        # trying to correct previously failed after cancel correcitons
        ('subv_processed_4_failed', 'failed'),
        ('subv_processed_5_failed', 'failed'),
        ('subv_processed_6_failed', 'failed'),
        # testing behaviour for cancelled and dismissed subventions
        ('subv_cancelled_1', 'processed'),
        ('subv_cancelled_2', 'processed'),
        ('subv_cancelled_3', 'processed'),
        ('subv_dismissed_1', 'processed'),
        ('subv_dismissed_2', 'processed'),
        ('subv_dismissed_3', 'processed'),
        # trying to correct delayed corrections, must be delayed
        ('subv_processed_2_delayed', 'delayed'),
        ('subv_processed_3_delayed', 'delayed'),
        ('subv_processed_7_delayed', 'delayed'),
        ('subv_processed_8_delayed', 'delayed'),
        # trying to correct outdated receipts
        ('outdated_1', 'outdated'),
    }
    expected_update = {
        ('subv_processed_1_1', 'cancelled'),
        ('subv_processed_1_2', 'cancelled'),
        ('subv_processed_1_3', 'cancelled'),
        ('subv_processed_1_4', 'cancelled'),
        ('subv_failed_1', 'dismissed'),
        ('subv_failed_wont_fix_1', 'dismissed'),
        ('subv_missing_inn_1', 'dismissed'),
        ('subv_missing_inn_1_new', 'dismissed'),
    }
    expected_inserted = {
        ('subv_processed_1_1_new', 'subvention', 'p1', 'd1', 'new', 3.0),
        ('subv_processed_1_3_new', 'subvention', 'p1', 'd1', 'new', 3.1),
        ('subv_failed_1_new', 'subvention', 'p1', 'd1', 'new', 4.0),
        ('subv_failed_wont_fix_1_new', 'subvention', 'p1', 'd1', 'new', 4.1),
        (
            'subv_missing_inn_1_new',
            'subvention',
            'p1',
            'd1',
            'missing_inn',
            4.2,
        ),
        (
            'subv_missing_inn_1_new_1',
            'subvention',
            'p1',
            'd1',
            'missing_inn',
            8.4,
        ),
        # testing behaviour for cancelled and dismissed subventions
        ('subv_cancelled_1_new', 'subvention', 'p1', 'd1', 'new', 3.5),
        ('subv_dismissed_1_new', 'subvention', 'p1', 'd1', 'new', 3.7),
    }

    @patch('selfemployed.db.dbmain.get_park_by_inn')
    async def get_park_by_inn(*args, **kwargs):
        inn = args[1]
        num = inn[3:]
        return 'p' + num, 'd' + num

    @patch('selfemployed.fns.client.Client.revert_income')
    async def revert_income(*args, **kwargs):
        inn = args[0]
        receipt_id = args[1]

        if inn == 'inn2':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.PARTNER_DENY_CODE,
            )
        if inn == 'inn3':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.PERMISSION_NOT_GRANTED_CODE,
            )

        if inn == 'inn4':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.TAXPAYER_UNREGISTERED_CODE,
            )

        if inn == 'inn5':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.TAXPAYER_UNBOUND_CODE,
            )

        if inn == 'inn7':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.PARTNER_DENY_CODE,
            )

        if inn == 'inn8':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.REQUEST_VALIDATION_ERROR,
            )

        reverted_receipts.add((inn, receipt_id))
        raise fns.SmzPlatformError(
            message='', code=fns.SmzErrorCode.ALREADY_DELETED,
        )

    @patch('selfemployed.fns.client.Client.get_revert_income_response')
    async def parse_revert(*args, **kwargs):
        return 'DELETED'

    from selfemployed.db.dbreceipts import update_receipt_status
    orig_update_receipt_status = update_receipt_status

    @patch('selfemployed.db.dbreceipts.update_receipt_status')
    async def update_receipt_status_mock(
            postgres, shard: int, receipt_id: str, new_status: str,
    ):
        await orig_update_receipt_status(
            postgres, shard, receipt_id, new_status,
        )
        updated_receipts.add((receipt_id, new_status))

    from selfemployed.db.dbreceipts import update_correction_status
    orig_update_correction_status = update_correction_status

    @patch('selfemployed.db.dbreceipts.update_correction_status')
    # pylint: disable=invalid-name
    async def update_correction_status_mock(
            pg, shard: int, reverse_id: str, status: str,
    ):
        await orig_update_correction_status(pg, shard, reverse_id, status)
        correction_updates.add((reverse_id, status))

    from selfemployed.db.dbreceipts import insert_new
    orig_insert_new = insert_new

    @patch('selfemployed.db.dbreceipts.insert_new')
    # pylint: disable=invalid-name
    async def insert_new_mock(
            pg,
            shard: int,
            receipt_id: str,
            receipt_type: str,
            park_id: str,
            driver_id: str,
            inn: str,
            status: str,
            total: float,
            is_corp: bool,
            is_cashless: bool,
            receipt_at,
            checkout_at,
    ):
        await orig_insert_new(
            pg,
            shard,
            receipt_id,
            receipt_type,
            park_id,
            driver_id,
            inn,
            status,
            total,
            is_corp,
            is_cashless,
            receipt_at,
            checkout_at,
        )
        inserted_receipts.add(
            (
                receipt_id,
                receipt_type,
                park_id,
                driver_id,
                status,
                float(total),
            ),
        )

    await run_cron.main(
        ['selfemployed.crontasks.process_corrections', '-t', '0'],
    )

    assert reverted_receipts == expected_reverted
    assert updated_receipts == expected_update
    assert inserted_receipts == expected_inserted
    assert correction_updates == expected_correction_updates


@pytest.mark.parametrize(
    'last_full_run, timeout, expect',
    [
        (dt.datetime(1970, 1, 1), dt.timedelta(seconds=1), True),
        (dt.datetime(1970, 1, 2), dt.timedelta(days=1), False),
        (None, dt.timedelta(seconds=1), True),
    ],
)
@pytest.mark.now('1970-01-02')
async def test_is_timeout_passed(last_full_run, timeout, expect, patch):
    assert (
        process_corrections.is_timeout_passed(last_full_run, timeout) == expect
    )


@pytest.mark.pgsql(
    'selfemployed_orders@0',
    queries=[
        """
    INSERT INTO corrections
        (reverse_id, new_id, park_id, driver_id, status,
        total, receipt_at, checkout_at, created_at, modified_at)
    VALUES
        ('subv2', 'subv3', 'p6', 'd6', 'delayed',
        3.1, NOW(), NOW(), NOW(), NOW());
    """,
    ],
)
@pytest.mark.pgsql(
    'selfemployed_orders@1',
    queries=[
        """
    INSERT INTO corrections
        (reverse_id, new_id, park_id, driver_id, status,
        total, receipt_at, checkout_at, created_at, modified_at)
    VALUES
        ('subv1', 'subv2', 'p1', 'd1', 'new',
        3.1, NOW(), NOW(), NOW(), NOW());
    """,
    ],
)
@pytest.mark.parametrize('full_run, expected_rows', [(True, 2), (False, 1)])
@pytest.mark.config(
    SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION_JOB=(
        conftest.SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION_JOB
    ),
)
async def test_sync_all_is_full_run(
        se_cron_context, patch, full_run, expected_rows,
):
    @patch('selfemployed.crontasks.process_corrections.process_correction')
    async def process_correction(*args, **kwargs):
        pass

    await process_corrections.sync_all(se_cron_context, full_run)

    assert len(process_correction.calls) == expected_rows
