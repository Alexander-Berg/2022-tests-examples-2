import collections
import datetime

import pytest

from testsuite.utils import http

from selfemployed.fns import client as fns
from selfemployed.fns import client_models as fns_models
from selfemployed.generated.stq3 import stq_context as context_module
from selfemployed.stq import report_income
from .. import conftest

_ENTRIES_SELECT_QUERY = """
SELECT id, park_id, contractor_id, agreement_id, sub_account,
    doc_ref, event_at::TEXT, inn_pd_id, is_own_park, do_send_receipt,
    status, amount::TEXT, order_id, reverse_entry_id,
    receipt_id, receipt_url
FROM se_income.entries
ORDER BY id
"""
_PROFILES_SELECT_QUERY = """
SELECT id, status
FROM profiles
ORDER BY id
"""
_BINDINGS_SELECT_QUERY = """
SELECT inn_pd_id, status, increment
FROM se.nalogru_phone_bindings
ORDER BY inn_pd_id
"""

_EVENTS_CFG = {
    'entries_receipt_properties': {
        'agreement1': {
            'subaccount1': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement2': {
            'subaccount2': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement3': {
            'subaccount3': {
                'income_type': 'FROM_LEGAL_ENTITY',
                'service_name': 'receipt_item',
            },
        },
        'agreement4': {
            'subaccount4': {
                'income_type': 'FROM_LEGAL_ENTITY',
                'service_name': 'receipt_subvention_item',
            },
        },
        'agreement6': {
            'subaccount6': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement7': {
            'subaccount7': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement8': {
            'subaccount8': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement9': {
            'subaccount9': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement10': {
            'subaccount10': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement11': {
            'subaccount11': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
        'agreement12': {
            'subaccount12': {
                'income_type': 'FROM_INDIVIDUAL',
                'service_name': 'receipt_item',
            },
        },
    },
}
_EVENTS_TRANSITION_CFG = {
    'entries_receipt_compatibility': {
        'agreement1': {'subaccount1': {'receipt_type': 'order'}},
        'agreement4': {'subaccount4': {'receipt_type': 'subvention'}},
    },
    'skip_actual_reporting': False,
}


def _serialize_income_data(income_data: fns_models.RegisterIncomeRawModel):
    return {
        'inn': income_data.inn,
        'request_time': income_data.request_time.isoformat(),
        'operation_time': income_data.operation_time.isoformat(),
        'income_type': income_data.income_type.value,
        'services': [
            {
                'amount': str(service.amount),
                'name': service.name,
                'quantity': service.quantity,
            }
            for service in income_data.services
        ],
        'total_amount': str(income_data.total_amount),
        'customer_inn': income_data.customer_inn,
        'customer_organization': income_data.customer_organization,
        'geo_info': (
            {
                'latitude': income_data.geo_info.latitude,
                'longitude': income_data.geo_info.longitude,
            }
            if income_data.geo_info
            else None
        ),
        'operation_unique_id': income_data.operation_unique_id,
    }


@pytest.mark.pgsql('selfemployed_main', files=['setup_profiles.sql'])
@pytest.mark.pgsql('selfemployed_orders@0', files=['setup_entries@0.sql'])
@pytest.mark.pgsql('selfemployed_orders@1', files=['setup_entries@1.sql'])
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.now('2021-11-15T12:00:00Z')
@pytest.mark.config(
    SELFEMPLOYED_INCOME_EVENTS=_EVENTS_CFG,
    SELFEMPLOYED_INCOME_EVENTS_TRANSITION=_EVENTS_TRANSITION_CFG,
)
async def test_report(
        stq3_context: context_module.Context,
        patch,
        mock_personal,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        mock_client_notify,
        load_json,
        stq,
):
    current_year = datetime.datetime.utcnow().year
    nalogru_requests = {}

    @mock_personal('/v1/tins/retrieve')
    async def _retrieve_inn_pd(request: http.Request):
        pd_id = request.json['id']
        return {'value': pd_id[:-6], 'id': pd_id}

    @patch('selfemployed.fns.client.Client.register_income_raw')
    async def _register_income_raw(
            income_data: fns_models.RegisterIncomeRawModel,
    ):
        nalogru_requests[income_data.inn] = _serialize_income_data(income_data)
        return income_data.inn

    @patch('selfemployed.fns.client.Client.get_register_income_response')
    async def _get_register_income_response(msg_id):
        if msg_id == 'inn7':
            raise fns.TaxpayerUnregisteredError(
                message='', code=fns.SmzErrorCode.TAXPAYER_UNREGISTERED_CODE,
            )
        if msg_id == 'inn9':
            raise fns.TaxpayerUnboundError(
                message='', code=fns.SmzErrorCode.TAXPAYER_UNBOUND_CODE,
            )
        if msg_id == 'inn10':
            raise fns.PermissionNotGranted(
                message='', code=fns.SmzErrorCode.PERMISSION_NOT_GRANTED_CODE,
            )
        if msg_id == 'inn11':
            raise fns.RequestValidationError(
                message='', code=fns.SmzErrorCode.REQUEST_VALIDATION_ERROR,
            )
        if msg_id == 'inn12':
            raise fns.TaxpayerUnboundError(
                message='', code=fns.SmzErrorCode.TAXPAYER_UNBOUND_CODE,
            )
        if msg_id == 'inn6':
            raise fns.DuplicateReceiptPlatformError(
                'msg',
                fns.SmzErrorCode.DUPLICATE_CODE,
                {'RECEIPT_ID': 'tt_dup', 'RECEIPT_URL': 'tt_dup//link'},
            )
        if msg_id == 'inn8':
            raise fns.RequestValidationError(
                message='',
                code=fns.SmzErrorCode.REQUEST_VALIDATION_ERROR,
                additional={'YEAR': str(current_year), 'THRESHOLD': '2.4'},
            )

        return f'tt_{msg_id}', f'tt_{msg_id}//link'

    @mock_fleet_parks('/v1/parks')
    async def _get_park(request: http.Request):
        park_id = request.query['park_id']
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
        return {'billing_client_id': f'bci_{clid}'}

    @mock_billing_replication('/person/')
    async def _get_billing_person(request: http.Request):
        client_id = request.query['client_id']
        return [
            {
                'ID': client_id,
                'INN': f'inn_{client_id}',
                'LONGNAME': f'name_{client_id}',
            },
        ]

    @mock_client_notify('/v2/push')
    async def _send_message(request):
        return {'notification_id': 'notification_id'}

    reports_to_schedule = []  # type: ignore
    for shard in stq3_context.pg.orders_masters:
        records = await shard.fetch(
            'SELECT id, park_id, contractor_id FROM se_income.entries',
        )
        reports_to_schedule.extend(records)

    for record in reports_to_schedule:
        await report_income.task(
            stq3_context,
            entry_id=record['id'],
            park_id=record['park_id'],
            contractor_id=record['contractor_id'],
        )

    entries_by_shards = {}
    for num, shard in enumerate(stq3_context.pg.orders_masters):
        shard_records = await shard.fetch(_ENTRIES_SELECT_QUERY)
        entries_by_shards[str(num)] = [
            dict(record) for record in shard_records
        ]

    legacy_profiles_records = await stq3_context.pg.main_master.fetch(
        _PROFILES_SELECT_QUERY,
    )
    legacy_profiles = [
        dict(lp_record) for lp_record in legacy_profiles_records
    ]

    bindings_records = await stq3_context.pg.main_master.fetch(
        _BINDINGS_SELECT_QUERY,
    )
    bindings = [dict(npb_record) for npb_record in bindings_records]

    assert entries_by_shards == load_json('expected_entries.json')

    assert nalogru_requests == load_json('expected_nalogru_requests.json')

    assert legacy_profiles == load_json('expected_legacy_profiles.json')

    assert bindings == load_json('expected_bindings.json')

    triggers = collections.defaultdict(set)
    while stq.selfemployed_fns_tag_contractor.has_calls:
        kwargs = stq.selfemployed_fns_tag_contractor.next_call()['kwargs']
        triggers[(kwargs['park_id'], kwargs['contractor_id'])].add(
            kwargs['trigger_id'],
        )
    assert triggers == {
        ('p7', 'c7'): {'taxpayer_unbound'},
        ('p9', 'c9'): {'taxpayer_unbound'},
        ('p10', 'c10'): {'taxpayer_unbound'},
        ('p12', 'c12'): {'taxpayer_unbound'},
        ('p8', 'c8'): {'taxpayer_income_threshold_exceeded'},
    }
