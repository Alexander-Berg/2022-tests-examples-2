import json

import pytest


@pytest.fixture(autouse=True)
def select_rules_request(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return {
            'subventions': [
                {
                    'tariff_zones': ['moscow'],
                    'status': 'enabled',
                    'start': '2009-01-01T00:00:00Z',
                    'end': '9999-12-31T23:59:59Z',
                    'type': 'discount_payback',
                    'is_personal': False,
                    'taxirate': '',
                    'subvention_rule_id': '__moscow__',
                    'cursor': '',
                    'tags': [],
                    'time_zone': {'id': '', 'offset': ''},
                    'updated': '2019-01-01T00:00:00Z',
                    'currency': 'rub',
                    'visible_to_driver': False,
                    'week_days': [],
                    'hours': [],
                    'log': [],
                    'tariff_classes': [],
                },
            ],
        }


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_REPLICATION_SETTINGS={
        'enabled': True,
        'chunk_size': 1,
        'replication_rule_name': 'discounts_service_replication',
    },
)
async def test_replication(taxi_discounts, mockserver):
    @mockserver.json_handler('/replication/data/discounts_service_replication')
    def _put_data(request):
        items = json.loads(request.get_data())['items']
        assert len(items) == 1
        _id = items[0]['id']
        return {'items': [{'id': _id, 'status': 'ok'}]}

    await taxi_discounts.invalidate_caches()
    await _put_data.wait_call()
