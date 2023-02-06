import dataclasses
import datetime
from unittest import mock

import bson
import pytest

from taxi_billing_subventions.rule_notifier import context as ctx
from taxi_billing_subventions.rule_notifier import entities
from taxi_billing_subventions.rule_notifier import exceptions
from taxi_billing_subventions.rule_notifier.rules.driver_fix import repository


async def test_get_by_id_for_absent_rule(context):
    repo = repository.DriverFixRulesRepository(context=context)
    with pytest.raises(exceptions.RuleNotFound) as exc:
        await repo.get_by_id(bson.ObjectId(b'aaaaaaaaaaaa'))
    assert str(exc.value) == 'Rule not found "616161616161616161616161"'


@pytest.mark.filldb(subvention_rules='default')
async def test_get_by_id_for_existed_rule(context, known_rule):
    repo = repository.DriverFixRulesRepository(context=context)
    rule = await repo.get_by_id(known_rule.rule_id)
    assert dataclasses.asdict(rule) == dataclasses.asdict(known_rule)


@pytest.mark.filldb(subvention_rules='default')
async def test_select_similar(context, known_rule):
    repo = repository.DriverFixRulesRepository(context=context)
    assert await repo.select_following_similar_to(known_rule) == [
        bson.ObjectId('0590ad4ec5d82ef89a3b85e5'),
    ]


@pytest.fixture(name='known_rule')
def make_rule():
    return entities.Rule(
        end=datetime.datetime(
            2020, 4, 10, 21, 0, 0, tzinfo=datetime.timezone.utc,
        ),
        kind='driver_fix',
        login='someone',
        profile_classes=['econom'],
        profile_payment_type_restrictions='none',
        rule_id=bson.ObjectId('5e58b3a98fe28d5ce4da0950'),
        tags=['geobookingspecial_ekb'],
        tariffzone='zelenograd',
        ticket='RUPRICING-5001',
        time_zone='Europe/Moscow',
    )


@pytest.fixture(name='context')
def make_context(db):
    return mock.MagicMock(ctx.Context, db=db)
