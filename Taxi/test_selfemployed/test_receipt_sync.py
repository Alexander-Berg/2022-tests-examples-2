# pylint: disable=redefined-outer-name,unused-variable,global-statement
# pylint: disable=too-many-statements
import datetime as dt
import typing as tp

import pytest

from testsuite.utils import http

from selfemployed.crontasks import receipt_sync
from selfemployed.fns import client as fns
from selfemployed.generated.cron import run_cron
from . import conftest


# pylint: disable=too-many-locals
@pytest.mark.pgsql('selfemployed_main', files=['setup_profiles.sql'])
@pytest.mark.pgsql('selfemployed_orders@0', files=['test_receipt_sync@0.sql'])
@pytest.mark.pgsql('selfemployed_orders@1', files=['test_receipt_sync@1.sql'])
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS={
        'use_receipt_idempotency_id': True,
    },
    SELFEMPLOYED_TESTING_BALANCE_FIX={
        'clid_p11': {'inn': 'INN_11', 'longname': 'OOO ROGA I KOPYTA'},
    },
)
@pytest.mark.now('2021-11-15T12:00:00Z')
async def test_receipt_sync(
        se_cron_context,
        mock_token_update,
        patch,
        monkeypatch,
        mock_personal,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        mock_client_notify,
        stq,
):
    registered_receipts = set()
    updated_receipts = set()
    driver_status_updates = set()
    # lower chunk quantity to test it
    monkeypatch.setattr(receipt_sync, 'RECEIPT_CHUNK_SIZE', 2)
    current_year = dt.datetime.utcnow().year

    expected_registered = {
        ('inn1', 'заказ', 1.1, None),
        ('inn1', 'заказ', 1.2, None),
        ('inn1', 'субсидия', 1.3, '7704340310'),
        ('inn1', 'субсидия', 1.4, '7704340310'),
        ('inn1', 'заказ', 1.5125, None),  # total for 'order' is not rounded
        ('inn1', 'заказ', 1.6125, '7704340310'),
        ('inn10', 'заказ', 10.1, None),
        ('inn10', 'заказ', 10.2, 'inn_bci_clid_p10'),
        ('inn11', 'субсидия', 11.1, 'INN_11'),
    }
    expected_update = {
        ('order1', 'order', 'processed', 'tt', 'tt//link'),
        ('order2', 'order', 'processed', 'tt', 'tt//link'),
        ('subv1', 'subvention', 'processed', 'tt', 'tt//link'),
        ('subv2', 'subvention', 'processed', 'tt', 'tt//link'),
        ('order3', 'order', 'processed', 'tt', 'tt//link'),
        ('order4', 'order', 'processed', 'tt', 'tt//link'),
        ('order_failed_1', 'order', 'delayed', None, None),
        ('order_failed_2', 'order', 'failed', None, None),
        ('order_failed_3', 'order', 'failed', None, None),
        ('order_failed_4', 'order', 'failed', None, None),
        ('order_failed_5', 'order', 'delayed', None, None),
        ('order_failed_6', 'order', 'failed', None, None),
        ('order_duplicate_1', 'order', 'processed', 'tt', 'tt//link'),
        ('order_negative', 'order', 'skipped', None, None),
        ('order_receipts_disabled_1', 'order', 'skipped', None, None),
        ('quasi_corp', 'order', 'processed', 'tt', 'tt//link'),
        ('quasi_order', 'order', 'processed', 'tt', 'tt//link'),
        ('quasi_subv', 'subvention', 'processed', 'tt', 'tt//link'),
        ('order_income_excess', 'order', 'failed', None, None),
    }
    expected_driver_status_updates = {
        ('p3', 'd3', 'bad_permissions'),
        ('p4', 'd4', 'rejected'),
        ('p5', 'd5', 'rejected'),
    }
    expected_bindings_updates = [
        ('phone3_pd_id', 'FAILED', None),
        ('phone4_pd_id', 'IN_PROGRESS', None),
        ('phone5_pd_id', 'FAILED', None),
        ('phone9_pd_id', 'COMPLETED', current_year),
    ]

    @mock_client_notify('/v2/push')
    async def _send_message(request):
        return {'notification_id': 'notification_id'}

    @patch('selfemployed.db.dbmain.get_park_by_inn')
    async def get_park_by_inn(*args, **kwargs):
        inn = args[1]
        num = inn[3:]
        return 'p' + num, 'd' + num

    @patch('selfemployed.fns.client.Client.register_income')
    async def register_income(*args, **kwargs):
        inn = args[0]
        title = args[1]
        total = args[2]
        customer_inn = kwargs['customer_inn']
        idempotency_id = kwargs['idempotency_id']
        assert idempotency_id

        if inn == 'inn2':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.PARTNER_DENY_CODE,
            )
        if inn == 'inn3':
            raise fns.PermissionNotGranted(
                message='', code=fns.SmzErrorCode.PERMISSION_NOT_GRANTED_CODE,
            )

        if inn == 'inn4':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.TAXPAYER_UNREGISTERED_CODE,
            )

        if inn == 'inn5':
            raise fns.TaxpayerUnboundError(
                message='', code=fns.SmzErrorCode.TAXPAYER_UNBOUND_CODE,
            )

        if inn == 'inn7':
            raise fns.SmzPlatformError(
                message='', code=fns.SmzErrorCode.PARTNER_DENY_CODE,
            )

        if inn == 'inn8':
            raise fns.RequestValidationError(
                message='', code=fns.SmzErrorCode.REQUEST_VALIDATION_ERROR,
            )

        if inn == 'inn9':
            raise fns.RequestValidationError(
                message='',
                code=fns.SmzErrorCode.REQUEST_VALIDATION_ERROR,
                additional={'YEAR': str(current_year), 'THRESHOLD': '2.4'},
            )

        if inn == 'inn_d1':
            raise fns.DuplicateReceiptPlatformError(
                'msg',
                fns.SmzErrorCode.DUPLICATE_CODE,
                {'RECEIPT_ID': 'tt', 'RECEIPT_URL': 'tt//link'},
            )

        if inn == 'inn_d2':
            raise fns.DuplicateReceiptPlatformError(
                'msg',
                fns.SmzErrorCode.DUPLICATE_CODE,
                {'RECEIPT_ID': '', 'RECEIPT_URL': 'tt//link'},
            )

        if inn == 'inn_d3':
            raise fns.DuplicateReceiptPlatformError(
                'msg',
                fns.SmzErrorCode.DUPLICATE_CODE,
                {'RECEIPT_ID': 'tt', 'RECEIPT_URL': ''},
            )

        if inn == 'inn_d4':
            raise fns.DuplicateReceiptPlatformError(
                'msg',
                fns.SmzErrorCode.DUPLICATE_CODE,
                {'RECEIPT_ID': '', 'RECEIPT_URL': ''},
            )

        registered_receipts.add((inn, title, total, customer_inn))

    @patch('selfemployed.fns.client.Client.get_register_income_response')
    async def parse_income(*args, **kwargs):
        return 'tt', 'tt//link'

    @mock_personal('/v1/tins/store')
    async def _store_inn_pd(request: http.Request):
        value = request.json['value'].strip('0')
        return {'value': value, 'id': f'{value}_pd_id'}

    @patch('selfemployed.db.dbreceipts.update_processed')
    async def update_processed(
            postgres,
            shard,
            receipt_id: str,
            receipt_type: str,
            status: str,
            fns_id: tp.Optional[str],
            fns_url: tp.Optional[str],
    ):
        updated_receipts.add(
            (receipt_id, receipt_type, status, fns_id, fns_url),
        )

    @patch('selfemployed.db.dbmain.update_selfemployed_status')
    async def update_selfemployed_status(
            postgres, park_id: str, driver_id: str, status: str,
    ):
        driver_status_updates.add((park_id, driver_id, status))

    @mock_fleet_parks('/v1/parks')
    async def _get_park(request: http.Request):
        park_id = request.query['park_id']
        assert park_id in {'p10', 'p11'}
        return {
            'id': park_id,
            'login': 'login',
            'name': 'name',
            'is_active': True,
            'city_id': 'city_id',
            'tz_offset': 3,
            'locale': 'ru',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'country_id': 'country_id',
            'provider_config': {'type': 'none', 'clid': f'clid_{park_id}'},
            'demo_mode': False,
            'fleet_type': 'yandex',
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        }

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    async def _get_billing_client_id(request: http.Request):
        clid = request.query['park_id']
        assert clid == 'clid_p10'
        return {'billing_client_id': f'bci_{clid}'}

    @mock_billing_replication('/person/')
    async def _get_billing_person(request: http.Request):
        client_id = request.query['client_id']
        assert client_id == 'bci_clid_p10'
        return [
            {'ID': f'bad_{client_id}'},
            {
                'ID': f'good_{client_id}',
                'INN': f'inn_{client_id}',
                'LONGNAME': f'name_{client_id}',
            },
        ]

    await run_cron.main(['selfemployed.crontasks.receipt_sync', '-t', '0'])

    assert registered_receipts == expected_registered
    assert updated_receipts == expected_update
    assert driver_status_updates == expected_driver_status_updates

    updated_bindings = await se_cron_context.pg.main_master.fetch(
        """
        SELECT phone_pd_id, status, exceeded_legal_income_year
        FROM se.nalogru_phone_bindings
        WHERE status <> 'COMPLETED' OR exceeded_legal_income_year IS NOT NULL
        ORDER BY phone_pd_id
        """,
    )
    assert [
        (
            binding['phone_pd_id'],
            binding['status'],
            binding['exceeded_legal_income_year'],
        )
        for binding in updated_bindings
    ] == expected_bindings_updates

    tagged_profiles = set()
    while stq.selfemployed_fns_tag_contractor.has_calls:
        kwargs = stq.selfemployed_fns_tag_contractor.next_call()['kwargs']
        tagged_profiles.add(
            (kwargs['park_id'], kwargs['contractor_id'], kwargs['trigger_id']),
        )
    assert tagged_profiles == {
        ('p3', 'd3', 'taxpayer_unbound'),
        ('p4', 'd4', 'taxpayer_unbound'),
        ('p5', 'd5', 'taxpayer_unbound'),
        ('p9', 'd9', 'taxpayer_income_threshold_exceeded'),
    }


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
    assert receipt_sync.is_timeout_passed(last_full_run, timeout) == expect


@pytest.mark.pgsql(
    'selfemployed_orders@0',
    queries=[
        """
    INSERT INTO receipts
        (id, park_id, driver_id, receipt_type, inn, status, total, is_corp,
         receipt_at, receipt_at_tstz, checkout_at, checkout_at_tstz,
         created_at, modified_at)
    VALUES
        ('order2', 'p6', 'd1', 'order', 'inn1', 'delayed',
        1.2, false, NOW(), NOW(), NOW(), NOW(), NOW(), NOW());
    """,
    ],
)
@pytest.mark.pgsql(
    'selfemployed_orders@1',
    queries=[
        """
    INSERT INTO receipts
        (id, park_id, driver_id, receipt_type, inn, status, total, is_corp,
         receipt_at, receipt_at_tstz, checkout_at, checkout_at_tstz,
         created_at, modified_at)
    VALUES
        ('order1', 'p1', 'd1', 'order', 'inn1', 'new',
        1.1, false, NOW(), NOW(), NOW(), NOW(), NOW(), NOW());
    """,
    ],
)
@pytest.mark.parametrize('full_run, expected_rows', [(True, 2), (False, 1)])
async def test_sync_all_is_full_run(
        se_cron_context, patch, full_run, expected_rows,
):
    @patch('selfemployed.crontasks.receipt_sync.sync_new_receipt')
    async def sync_new(*args, **kwargs):
        pass

    await receipt_sync.sync_all(se_cron_context, full_run)

    assert len(sync_new.calls) == expected_rows
