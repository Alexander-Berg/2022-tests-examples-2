import datetime
import json

import dateutil.parser
import pytest


class BillingSubventionsXContext:
    def __init__(self):
        self.rules_select = None
        self.match = None
        self.bulk_match = None
        self.updates = None
        self.by_draft = None
        self.count = None

        self.rules = []
        self.updated_rules = []
        self.match_throws = False
        self.bulk_match_throws = False
        self.updates_throws_call = None
        self.count_answers = None

    def set_rules(self, rules):
        self.rules = rules

    def set_updated_rules(self, rules):
        self.updated_rules = rules

    def set_match_throws(self, throws):
        self.match_throws = throws

    def set_bulk_match_throws(self, throws):
        self.bulk_match_throws = throws

    def set_updates_throws_call(self, call_number):
        self.updates_throws_call = call_number

    def set_count_answers(self, answers):
        self.count_answers = answers

    def reset(self):
        self.rules = []
        self.updated_rules = []
        self.match_throws = False
        self.bulk_match_throws = False
        self.updates_throws_call = None

    async def do_rules_select(self, zones, tariff_classes, start, end):
        return [
            r
            for r in self.rules
            if r['zone'] in zones
            and r['tariff_class'] in tariff_classes
            and (
                dateutil.parser.parse(r['start']) <= end
                and dateutil.parser.parse(r['end']) > start
            )
        ]

    async def do_by_draft(self, draft_id):
        return [r for r in self.rules if r['draft_id'] == draft_id]

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

    @staticmethod
    def _get_rate(rule, at_time):
        at_day = at_time.weekday()
        at_min = at_time.hour * 60 + at_time.minute

        rate = None
        for sch_item in rule['rates']:
            s_day = BillingSubventionsXContext._get_day_no(
                sch_item['week_day'],
            )
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

    @staticmethod
    def _match_branding(branding, has_sticker, has_lightbox):
        if branding == 'sticker':
            return has_sticker
        if branding == 'without_sticker':
            return not has_sticker

        raise 'Unknown branding'

    async def do_match(
            self,
            zone,
            tariff_class,
            geoareas,
            activity_points,
            has_sticker,
            has_lightbox,
            at_time,
    ):
        suitable = [
            r
            for r in self.rules
            if r['zone'] in zone
            and r['tariff_class'] in tariff_class
            and ('geoarea' not in r or r['geoarea'] in geoareas)
            and (
                'activity_points' not in r
                or r['activity_points'] <= activity_points
            )
            and (
                'branding_type' not in r
                or BillingSubventionsXContext._match_branding(
                    r['branding_type'], has_sticker, has_lightbox,
                )
            )
            and dateutil.parser.parse(r['start'])
            <= at_time
            < dateutil.parser.parse(r['end'])
            and BillingSubventionsXContext._get_rate(r, at_time)
        ]

        if not suitable:
            return []

        best = sorted(
            suitable,
            key=lambda s: 0 if 'geoarea' not in s else 1,
            reverse=True,
        )[0]
        rate = BillingSubventionsXContext._get_rate(best, at_time)

        return [
            {
                'rule': best,
                'type': best['rule_type'],
                'amount': rate['bonus_amount'],
            },
        ]

    async def do_bulk_match(
            self,
            zone,
            tariff_class,
            geoareas,
            activity_points,
            has_sticker,
            has_lightbox,
            at_times,
    ):
        result = []
        for at_time in at_times:
            at_match = await self.do_match(
                zone,
                tariff_class,
                geoareas,
                activity_points,
                has_sticker,
                has_lightbox,
                at_time,
            )
            if at_match:
                result.append(
                    {
                        'id': at_match[0]['rule']['id'],
                        'reference_time': at_time,
                        'amount': at_match[0]['amount'],
                    },
                )

        return result


@pytest.fixture
def bsx(mockserver):
    bsx_context = BillingSubventionsXContext()

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    async def _mock_rules_select(request_data):
        request = json.loads(request_data.get_data())
        rules = await bsx_context.do_rules_select(
            request['zones'],
            request['tariff_classes'],
            dateutil.parser.parse(request['time_range']['start'])
            + datetime.timedelta(hours=3),  # moscow TZ
            dateutil.parser.parse(request['time_range']['end'])
            + datetime.timedelta(hours=3),  # moscow TZ
        )

        limit = request['limit']
        start = 0
        if 'cursor' in request:
            start = int(request['cursor'])
        end = start + limit
        return {'rules': rules[start:end], 'next_cursor': str(end)}

    @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
    async def _mock_match(request_data):
        request = json.loads(request_data.get_data())

        if bsx_context.match_throws is True:
            return mockserver.make_response(status=500)

        match = await bsx_context.do_match(
            request['zone'],
            request['tariff_class'],
            request['geoareas'],
            request['activity_points'],
            request['has_sticker'],
            request['has_lightbox'],
            dateutil.parser.parse(request['reference_time'])
            + datetime.timedelta(hours=3),  # moscow TZ
        )

        return {'matches': match}

    @mockserver.json_handler(
        '/billing-subventions-x/v2/rules/match/bulk_single_ride',
    )
    async def _mock_bulk_match(request_data):
        request = request_data.json

        if bsx_context.bulk_match_throws is True:
            return mockserver.make_response(status=500)

        bulk_matches = await bsx_context.do_bulk_match(
            request['zone'],
            request['tariff_class'],
            request['geoareas'],
            request['activity_points'],
            request['has_sticker'],
            request['has_lightbox'],
            [
                dateutil.parser.parse(at) + datetime.timedelta(hours=3)
                for at in request['reference_times']
            ],
        )

        for bulk_match in bulk_matches:
            bulk_match['reference_time'] = (
                bulk_match['reference_time'] - datetime.timedelta(hours=3)
            ).isoformat()

        return {'matches': bulk_matches}

    @mockserver.json_handler('/billing-subventions-x/v2/rules/by_draft')
    async def _mock_by_draft(request_data):
        request = json.loads(request_data.get_data())

        assert len(request['drafts']) == 1
        draft_id = request['drafts'][0]
        by_draft = await bsx_context.do_by_draft(draft_id)

        return {
            'rules': [{'draft_id': draft_id, 'added': by_draft, 'closed': []}],
        }

    @mockserver.json_handler('/billing-subventions-x/v2/rules/updates')
    async def _mock_updates(request_data):
        request = json.loads(request_data.get_data())

        if bsx_context.updates.times_called == bsx_context.updates_throws_call:
            return mockserver.make_response(status=500)

        index = 0
        if 'cursor' in request and 'pos' in request['cursor']:
            index = int(request['cursor']['pos'])
        if (index + 1) == len(bsx_context.updated_rules):
            return {'rules': bsx_context.updated_rules[index]}

        return {
            'next_cursor': {'pos': str(index + 1)},
            'rules': bsx_context.updated_rules[index],
        }

    @mockserver.json_handler('/billing-subventions-x/v2/rules/count')
    async def _mock_count(request_data):
        request = json.loads(request_data.get_data())
        response = []

        for zone in request['zones']:
            count = (
                bsx_context.count_answers[bsx_context.count.times_called]
                if bsx_context.count_answers is not None
                else 0
            )
            response.append(
                {
                    'zone': zone,
                    'rules_count_by_type': [
                        {'rule_type': 'single_ride', 'count': count},
                    ],
                },
            )

        return {'rules_count': response}

    bsx_context.rules_select = _mock_rules_select
    bsx_context.match = _mock_match
    bsx_context.bulk_match = _mock_bulk_match
    bsx_context.updates = _mock_updates
    bsx_context.by_draft = _mock_by_draft
    bsx_context.count = _mock_count

    return bsx_context
