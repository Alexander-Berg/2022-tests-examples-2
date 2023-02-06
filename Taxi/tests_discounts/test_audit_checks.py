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


def get_last_time_check(pgsql):
    cursor = pgsql['discounts'].conn.cursor()
    cursor.execute('select * from discounts.audit_check_threshold;')
    result = list(cursor)
    cursor.close()
    assert len(result) == 1
    return result[0][1].isoformat()


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
        'audit_check.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True},
    DISCOUNTS_AUDIT_CHECK_SETTINGS={
        'enabled': True,
        'lookup_offset': 60,
        'log_username': 'robot-taxi-infra',
    },
)
@pytest.mark.now('2018-12-31T23:58:30Z')
async def test_audit_notifications(taxi_discounts, mockserver, pgsql):
    @mockserver.json_handler('/audit/v1/robot/logs/')
    def mock_create_log(request):
        request_json = json.loads(request.get_data())
        assert request_json == {
            'action': 'discount_start',
            'arguments': {
                'discount_description': 'discount1',
                'discount_id': 'discount1',
                'zone_name': 'moscow',
            },
            'login': 'robot-taxi-infra',
            'timestamp': '2019-01-01T00:00:00+00:00',
        }
        return {'id': '123456'}

    assert get_last_time_check(pgsql) == '2019-01-01T02:58:29+03:00'

    async with taxi_discounts.spawn_task('discounts-audit-notify-task'):
        await mock_create_log.wait_call()

    assert get_last_time_check(pgsql) == '2019-01-01T03:00:30+03:00'
