# pylint: disable=redefined-outer-name
# pylint: disable=W0212
import datetime
import inspect
import logging

import pytest

from sf_data_load.utils import constants

logger = logging.getLogger(__name__)


class ContractFilter:
    def __init__(self, timestamp: float):
        self.timestamp = timestamp

    def __call__(self, row):
        if (
                row.get('updated') > self.timestamp
                and set(row.get('service_ids')) - {718, 1040}
                and row.get('is_offer')
        ):
            yield row


async def test_mapper_identical():
    from sf_data_load.crontasks.custom import get_corp_contracts

    assert inspect.getsource(
        get_corp_contracts.ContractFilter,
    ) == inspect.getsource(ContractFilter), (
        '_mapper in tests != _mapper in cron'
    )


@pytest.mark.yt(dyn_table_data=['yt_corp_contracts_info.yaml'])
@pytest.mark.now((datetime.datetime(1998, 6, 21)).strftime('%Y-%m-%d'))
async def test_map(yt_apply, cron_context):
    ctx = cron_context
    yt = ctx.yt_wrapper.hahn  # pylint: disable=C0103

    corp_path = f'//home/taxi/unittests/replica/mongo/struct/corp/'
    contract_path = yt.TablePath(corp_path + 'corp_contracts')

    await yt.unmount_table(contract_path, sync=True)
    await yt.mount_table(contract_path, sync=True)

    tmp_path = constants.YT_HOME + 'tmp'
    time_now = datetime.datetime.utcnow()
    time_now = time_now.timestamp()
    with yt.TempTable(tmp_path) as agg_tab:
        await yt.run_map(
            ContractFilter(time_now),
            source_table=contract_path,
            destination_table=agg_tab,
        )
        output = list(await yt.read_table(agg_tab))

    assert output == [
        {
            'id': 12312,
            'billing_client_id': '2343234',
            'contract_external_id': '123/19',
            'payment_type': 'prepaid',
            'is_active': True,
            'is_offer': True,
            'offer_accepted': False,
            'service_ids': [650, 668],
            'currency': 'RUB',
            'balance': {
                'balance': '123.34',
                'balance_dt': 1654614969.988,
                'total_charge': '100',
                'receipt_sum': '200',
                'apx_sum': '100',
                'discount_bonus_sum': '100',
                'receipt_dt': 1654614898.212,
                'receipt_version': 1,
                'operational_balance': '100',
            },
            'settings': {
                'is_active': True,
                'is_auto_activate': True,
                'low_balance_notification_enabled': True,
                'low_balance_threshold': '500',
                'prepaid_deactivate_threshold': '123.34',
                'prepaid_deactivate_threshold_id': (
                    'prepaid_deactivate_threshold_id'
                ),
                'prepaid_deactivate_threshold_type': 'standard',
                'contract_limit': {'limit': '123.45', 'threshold': '456.789'},
            },
            'created': 1654614899.168,
            'updated': 1654615052.869,
            'edo_accepted': None,
        },
        {
            'id': 12316,
            'billing_client_id': '2343234',
            'contract_external_id': '123/19',
            'payment_type': 'prepaid',
            'is_active': True,
            'is_offer': True,
            'offer_accepted': False,
            'service_ids': [650, 668],
            'currency': 'RUB',
            'balance': {
                'balance': '123.34',
                'balance_dt': 1654614969.988,
                'total_charge': '100',
                'receipt_sum': '200',
                'apx_sum': '100',
                'discount_bonus_sum': '100',
                'receipt_dt': 1654614898.212,
                'receipt_version': 1,
                'operational_balance': '100',
            },
            'settings': {
                'is_active': True,
                'is_auto_activate': True,
                'low_balance_notification_enabled': True,
                'low_balance_threshold': '500',
                'prepaid_deactivate_threshold': '123.34',
                'prepaid_deactivate_threshold_id': (
                    'prepaid_deactivate_threshold_id'
                ),
                'prepaid_deactivate_threshold_type': 'standard',
                'contract_limit': {'limit': '123.45', 'threshold': '456.789'},
            },
            'created': 1654614899.168,
            'updated': 1654615052.869,
            'edo_accepted': None,
        },
    ]
