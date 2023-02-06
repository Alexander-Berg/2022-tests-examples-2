import dataclasses
import datetime
from typing import List

import bson
import pytest

from taxi_billing_subventions.rule_notifier import entities
from taxi_billing_subventions.rule_notifier.usecases import notify_end

_RULE_WITH_FOLLOWING = bson.ObjectId(b'bbbbbbbbbbbb')
_RULE_ID = bson.ObjectId('5e58b3a98fe28d5ce4da0950')
_CLOSED_RULE = bson.ObjectId(b'cccccccccccc')
_RULE_WITHOUT_TICKET = bson.ObjectId(b'dddddddddddd')


@pytest.mark.now('2020-04-10T12:00:00')
@pytest.mark.parametrize(
    'rule_id,expected',
    (
        (_RULE_WITH_FOLLOWING, False),
        (_RULE_WITHOUT_TICKET, False),
        (_RULE_ID, True),
        (_CLOSED_RULE, False),
    ),
)
async def test_notify_rule_ends(rule_id, expected, known_rule):
    notification_service = NotificationServiceStub()
    notifier = notify_end.EndOfTheRuleNotifier(
        rules_repository=RulesRepositoryStub(known_rule),
        notification_service=notification_service,
    )
    await notifier(rule_id)
    assert notification_service.called is expected


@pytest.fixture(name='known_rule')
def _known_rule():
    return entities.Rule(
        end=datetime.datetime(
            2020, 4, 10, 21, 0, 0, tzinfo=datetime.timezone.utc,
        ),
        kind='driver_fix',
        login='someone',
        profile_payment_type_restrictions='none',
        profile_classes=['econom'],
        rule_id=_RULE_ID,
        tags=['geobookingspecial_ekb'],
        tariffzone='zelenograd',
        ticket='RUPRICING-5001',
        time_zone='Europe/Moscow',
    )


class NotificationServiceStub:
    def __init__(self):
        self.called = False

    async def notify(self, rule: entities.Rule):
        self.called = True


class RulesRepositoryStub:
    def __init__(self, known_rule):
        self._known_rule = known_rule

    async def get_by_id(self, rule_id: bson.ObjectId) -> entities.Rule:
        rule = dataclasses.replace(self._known_rule, rule_id=rule_id)
        if rule.rule_id == _CLOSED_RULE:
            rule = dataclasses.replace(
                rule,
                end=datetime.datetime(
                    2020, 4, 1, tzinfo=datetime.timezone.utc,
                ),
            )
        if rule.rule_id == _RULE_WITHOUT_TICKET:
            rule = dataclasses.replace(rule, ticket='')
        return rule

    async def select_following_similar_to(
            self, rule: entities.Rule,
    ) -> List[bson.ObjectId]:
        if rule.rule_id == _RULE_WITH_FOLLOWING:
            return [_RULE_ID]
        return []
