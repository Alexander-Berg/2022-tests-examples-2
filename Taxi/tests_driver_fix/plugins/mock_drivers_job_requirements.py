import pytest


@pytest.fixture(name='mock_drivers_job_requirements')
def _mock_drivers_job_requirements(mockserver):
    class Context:
        def __init__(self):
            self.drivers = []
            self.mock_drivers = {}
            self.statuses = []
            self.mock_statuses = {}
            self.history = {}
            self.mock_history = {}
            self.rules = []
            self.mock_rules_select = {}
            self.by_driver_info = {}
            self.mock_by_driver = {}
            self.mock_mode_reset = {}

        def add_driver(self, driver):
            self.drivers.append(driver)

        def add_drivers(self, drivers):
            self.drivers.extend(drivers)

        def add_status(self, driver):
            res = {
                'park_id': driver.park_id,
                'driver_id': driver.driver_profile_id,
                'status': 'online',
            }
            if driver.on_order:
                res.update({'orders': [{'id': '1', 'status': 'driving'}]})
            self.statuses.append(res)

        def add_statuses(self, drivers):
            for driver in drivers:
                self.add_status(driver)

        def add_subscription(self, history, mode='geobooking'):
            event_data = {
                'external_event_ref': 'external_ref',
                'event_at': history.event_at,
                'data': {
                    'driver': {
                        'park_id': history.park_id,
                        'driver_profile_id': history.driver_profile_id,
                    },
                    'mode': mode,
                    'settings': {'rule_id': history.rule_id},
                },
            }
            history_key = f'{history.park_id}_{history.driver_profile_id}'
            if history_key not in self.history:
                self.history[history_key] = [event_data]
            else:
                self.history[history_key].append(event_data)

        def add_rules(self, rules):
            self.rules.extend(rules)

        def add_by_driver(self, by_driver):
            self.by_driver_info[f'{by_driver.udid}_{by_driver.rule_id}'] = {
                'subvention_rule_id': by_driver.rule_id,
                'payoff': {'amount': '100', 'currency': 'RUB'},
                'period': {
                    'start_time': '2019-05-04T00:00:00+0300',
                    'end_time': '2019-05-04T12:00:00+0300',
                },
                'time_on_order_minutes': by_driver.time_on_order,
                'time_free_minutes': by_driver.time_free,
            }

    context = Context()

    @mockserver.json_handler('/driver-mode-index/v1/drivers')
    def _mock_drivers(request):
        return {'drivers': context.drivers}

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _mock_statuses(request):
        return {'statuses': context.statuses}

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    async def _mock_history(request):
        driver = request.json['driver']
        dbid, uuid = driver['park_id'], driver['driver_profile_id']
        key = f'{dbid}_{uuid}'
        return {
            'docs': context.history[key] if key in context.history else [],
            'cursor': '-',
        }

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def _rules_select(request):
        if 'rule_ids' in request.json:
            subventions = [
                rule
                for rule in context.rules
                if rule['subvention_rule_id'] == request.json['rule_ids'][0]
            ]
            return {'subventions': subventions}
        return {'subventions': context.rules}

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    async def _by_driver(request):
        request_json = request.json
        udid = request_json['unique_driver_id']
        subventions = []
        for rule_id in request_json['subvention_rule_ids']:
            by_driver_key = f'{udid}_{rule_id}'
            if (
                    by_driver_key in context.by_driver_info
                    and request_json['time_range']['end_time']
                    == '2019-05-04T09:00:00+00:00'
            ):
                subventions.append(context.by_driver_info[by_driver_key])
        return {'subventions': subventions}

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/reset')
    async def _mode_reset(request):
        return {
            'active_mode': 'orders',
            'active_mode_type': 'display_mode',
            'active_since': '2019-05-04T12:00:00+0300',
        }

    context.mock_mode_reset = _mode_reset
    context.mock_by_driver = _by_driver
    context.mock_rules_select = _rules_select
    context.mock_history = _mock_history
    context.mock_statuses = _mock_statuses
    context.mock_drivers = _mock_drivers
    return context
