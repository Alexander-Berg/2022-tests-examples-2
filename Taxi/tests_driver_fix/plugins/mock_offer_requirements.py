import copy
import datetime
import json


import pytest


@pytest.fixture(name='mock_offer_requirements')
def _mock_offer_requirements(mockserver):
    class Context:
        def __init__(self):
            self.profiles_value = {}
            self.dcb_value = []
            self.payment_types_values = []
            self.nearestzone_value = ''
            self.rules_select_value = {}
            self.rules_select_call_params = []
            self.rules_select_value_by_type = None
            self.bsx_rules_select_value = []
            self.position_fallback = None
            self.profiles = None
            self.by_driver_subventions = []
            self.by_driver_calls = 0
            self.by_driver_call_params = []

        def init(
                self,
                profiles_value,
                dcb_value,
                payment_types_values,
                nearestzone_value,
                rules_select_value,
                rules_select_value_by_type,
                by_driver_subventions,
        ):
            self.profiles_value = copy.deepcopy(profiles_value)
            self.dcb_value = copy.deepcopy(dcb_value)
            self.payment_types_values = copy.deepcopy(payment_types_values)
            self.nearestzone_value = copy.deepcopy(nearestzone_value)
            self.rules_select_value = copy.deepcopy(rules_select_value)
            self.rules_select_value_by_type = copy.deepcopy(
                rules_select_value_by_type,
            )
            self.by_driver_subventions = by_driver_subventions

        def set_position_fallback(self, position):
            self.position_fallback = copy.deepcopy(position)

        def set_candidates_payment_type(self, payment_type):
            pt_to_pm = {
                'none': ['cash', 'card', 'coupon', 'promo'],
                'online': ['card', 'coupon', 'promo'],
                'cash': ['cash'],
            }
            payment_methods = pt_to_pm[payment_type]
            self.profiles_value['payment_methods'] = payment_methods

        @staticmethod
        def _get_zone(rule):
            if rule['rule_type'] == 'goal':
                return rule['geonode']
            if rule['rule_type'] in ('single_ride', 'single_ontop'):
                return rule['zone']
            raise Exception(f'wrong rule type {rule["rule_type"]}')

        @staticmethod
        def _match_tags(rule, request_tags):
            if rule['rule_type'] != 'goal':
                return True
            if request_tags is not None and not request_tags:
                return False
            return ('tag' not in rule and request_tags is None) or (
                request_tags is not None
                and ('tag' in rule and rule['tag'] in request_tags)
            )

        def do_bsx_rules_select(
                self,
                zones,
                tariff_classes,
                tags,
                start,
                end,
                unique_driver_ids,
        ):
            rules = [
                r
                for r in self.bsx_rules_select_value
                if (
                    unique_driver_ids is not None
                    or zones is None
                    or Context._get_zone(r) in zones
                )
                and (
                    tariff_classes is None
                    or r['tariff_class'] in tariff_classes
                )
                and (
                    datetime.datetime.fromisoformat(r['start']) <= end
                    or datetime.datetime.fromisoformat(r['end']) > start
                )
                and Context._match_tags(r, tags)
                and (
                    unique_driver_ids is None
                    or (
                        'unique_driver_id' in r
                        and r['unique_driver_id'] in unique_driver_ids
                    )
                )
            ]
            return rules

    ctx = Context()

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        doc = json.loads(request.get_data())

        assert 'driver_ids' in doc
        assert 'data_keys' in doc
        assert doc['driver_ids']
        assert ctx.profiles_value is not None

        if 'payment_methods' in ctx.profiles_value:
            assert 'payment_methods' in doc['data_keys']

        return {'drivers': [ctx.profiles_value]}

    @mockserver.json_handler('/driver-payment-types/service/v1/bulk-retrieve')
    def _driver_payment_types(request):
        doc = json.loads(request.get_data())
        assert doc['source'] == 'driver-fix'
        assert len(doc['items']) == len(ctx.payment_types_values)
        for item, payment_type in zip(doc['items'], ctx.payment_types_values):
            if ctx.position_fallback:
                assert ctx.position_fallback == item['position']
            else:
                assert ctx.profiles_value['position'] == item['position']
            assert payment_type['park_id'] == item['park_id']
            assert (
                payment_type['driver_profile_id'] == item['driver_profile_id']
            )
        return {'items': ctx.payment_types_values}

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        return {'nearest_zone': ctx.nearestzone_value}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        doc = json.loads(request.get_data())
        ctx.rules_select_call_params.append(doc)

        if not ctx.rules_select_value_by_type:
            return {'subventions': [ctx.rules_select_value]}

        types = doc['types']
        assert types
        return {'subventions': ctx.rules_select_value_by_type[types[0]]}

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _mock_rules_select(request_data):
        request = json.loads(request_data.get_data())
        tags_constraint = (
            request['tags_constraint']
            if 'tags_constraint' in request
            else None
        )
        tags = (
            tags_constraint['tags']
            if tags_constraint is not None and 'tags' in tags_constraint
            else None
        )
        unique_driver_ids = (
            request['drivers'] if 'drivers' in request else None
        )
        rules = ctx.do_bsx_rules_select(
            request['zones'] if 'zones' in request else None,
            request['tariff_classes'] if 'tariff_classes' in request else None,
            tags,
            datetime.datetime.fromisoformat(request['time_range']['start']),
            datetime.datetime.fromisoformat(request['time_range']['end']),
            unique_driver_ids,
        )

        limit = request['limit']
        start = 0
        if 'cursor' in request:
            start = int(request['cursor'])
        end = start + limit
        return {'rules': rules[start:end], 'next_cursor': str(end)}

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    def _get_by_driver(request):
        ctx.by_driver_calls += 1
        ctx.by_driver_call_params.append(request.get_data())
        if ctx.by_driver_subventions is None:
            ctx.by_driver_subventions = []
        print('subventions_data: {}'.format(ctx.by_driver_subventions))
        return {'subventions': ctx.by_driver_subventions}

    ctx.profiles = _profiles

    return ctx
