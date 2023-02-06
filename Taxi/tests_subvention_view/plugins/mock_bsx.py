# pylint: disable=C5521
from collections import defaultdict
import datetime
import json

import pytest
import pytz


class BillingSubventionsXContext:
    def __init__(self):
        self.calls = defaultdict(int)
        self.rules_select = None
        self.by_driver = None
        self.match = None
        self.by_draft = None
        self.by_ids = None
        self.orders_by_driver = {}

        self.tz_name = 'Europe/Moscow'
        self.rules = []
        self.match_throws = False
        self.fixed_days = False

    def set_rules(self, rules):
        self.rules = rules

    def set_rules_timezone(self, time_zone):
        self.tz_name = time_zone

    def set_use_fixed_days(self, fixed):
        self.fixed_days = fixed

    def set_match_throws(self, throws):
        self.match_throws = throws

    def set_by_driver(self, by_driver):
        self.orders_by_driver.update(by_driver)

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

    def do_rules_select(
            self, zones, tariff_classes, tags, start, end, unique_driver_ids,
    ):
        rules = [
            r
            for r in self.rules
            if (
                unique_driver_ids is not None
                or zones is None
                or BillingSubventionsXContext._get_zone(r) in zones
            )
            and (tariff_classes is None or r['tariff_class'] in tariff_classes)
            and (
                datetime.datetime.fromisoformat(r['start']) <= end
                or datetime.datetime.fromisoformat(r['end']) > start
            )
            and BillingSubventionsXContext._match_tags(r, tags)
            and (
                unique_driver_ids is None
                or (
                    'unique_driver_id' in r
                    and r['unique_driver_id'] in unique_driver_ids
                )
            )
        ]
        return rules

    async def do_by_draft(self, draft_id):
        return [r for r in self.rules if r['draft_id'] == draft_id]

    async def do_by_ids(self, rule_ids):
        return [r for r in self.rules if r['id'] in rule_ids]

    async def do_by_driver(self, global_counters):
        subventions = []
        for counter in global_counters:
            if counter in self.orders_by_driver:
                subventions.append(
                    {
                        'counter': counter,
                        'num_orders': self.orders_by_driver[counter],
                        'payoff': {'amount': '100', 'currency': 'RUB'},
                        'period': {
                            'start': '2020-03-15T21:00:00+00:00',
                            'end': '2023-03-15T21:00:00+00:00',
                        },
                    },
                )
        return subventions

    @staticmethod
    def _get_day_no(day):
        _days = {
            'mon': 0,
            'tue': 1,
            'wed': 2,
            'thu': 3,
            'fri': 4,
            'sat': 5,
            'sun': 6,
        }
        return _days[day]

    def _get_rate(self, rule, at_time):
        at_day = at_time.weekday() if self.fixed_days else at_time.day
        at_min = at_time.hour * 60 + at_time.minute

        rate = None
        for sch_item in rule['rates']:
            s_day = BillingSubventionsXContext._get_day_no(
                sch_item['week_day'],
            )
            if not self.fixed_days:
                s_day = s_day + 1

            s_min = int(sch_item['start'][:2]) * 60 + int(
                sch_item['start'][3:],
            )

            if s_day > at_day or (s_day == at_day and s_min > at_min):
                break
            if sch_item['bonus_amount'] == '0':
                rate = None
            else:
                rate = sch_item

        return rate

    async def do_match(self, zone, tariff_class, geoareas, at_time):
        suitable = [
            r
            for r in self.rules
            if r['zone'] == zone
            and r['tariff_class'] == tariff_class
            and ('geoarea' not in r or r['geoarea'] in geoareas)
            and (
                datetime.datetime.fromisoformat(r['start']) <= at_time
                or datetime.datetime.fromisoformat(r['end']) > at_time
            )
            and self._get_rate(r, at_time)
        ]

        if not suitable:
            return []

        best = sorted(
            suitable,
            key=lambda s: 0 if 'geoarea' not in s else 1,
            reverse=True,
        )[0]
        rate = self._get_rate(best, at_time)
        return [
            {
                'rule': best,
                'type': best['rule_type'],
                'amount': rate['bonus_amount'],
            },
        ]


@pytest.fixture
def bsx(mockserver):
    bsx_context = BillingSubventionsXContext()

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _mock_rules_select(request_data):
        bsx_context.calls['rules_select'] += 1
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
        rules = bsx_context.do_rules_select(
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

    @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
    async def _mock_match(request_data):
        bsx_context.calls['rules_match'] += 1

        if bsx_context.match_throws is True:
            return mockserver.make_response(status=500)

        request = json.loads(request_data.get_data())
        match = await bsx_context.do_match(
            request['zone'],
            request['tariff_class'],
            request['geoareas'],
            datetime.datetime.fromisoformat(
                request['reference_time'],
            ).astimezone(
                tz=pytz.timezone(bsx_context.tz_name),
            ),  # moscow TZ
        )

        return {'matches': match}

    @mockserver.json_handler('/billing-subventions-x/v2/by_driver')
    async def _mock_by_driver(request_data):
        request = json.loads(request_data.get_data())

        return {
            'subventions': await bsx_context.do_by_driver(
                request['global_counters'],
            ),
        }

    @mockserver.json_handler('/billing-subventions-x/v2/rules/by_draft')
    async def _mock_by_draft(request_data):
        request = json.loads(request_data.get_data())

        assert len(request['drafts']) == 1
        draft_id = request['drafts'][0]
        by_draft = await bsx_context.do_by_draft(draft_id)

        return {
            'rules': [{'draft_id': draft_id, 'added': by_draft, 'closed': []}],
        }

    @mockserver.json_handler('/billing-subventions-x/v2/rules/by_ids')
    async def _mock_by_ids(request_data):
        request = json.loads(request_data.get_data())

        rule_ids = request['rules']
        rules = await bsx_context.do_by_ids(rule_ids)

        return {'rules': rules}

    bsx_context.rules_select = _mock_rules_select
    bsx_context.match = _mock_match
    bsx_context.by_driver = _mock_by_driver
    bsx_context.by_draft = _mock_by_draft
    bsx_context.by_ids = _mock_by_ids

    return bsx_context
